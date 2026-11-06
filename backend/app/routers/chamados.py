"""Rotas (endereços) da API de chamados."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Chamado
from app.schemas import (
    ChamadoCreate,
    ChamadoOut,
    Resumo,
    Status,
    StatusUpdate,
    Tipo,
)
from app.sla import sla_estourado

# APIRouter agrupa rotas relacionadas. Todas começam com /chamados.
# "tags" organiza as rotas na documentação automática (/docs).
router = APIRouter(prefix="/chamados", tags=["Chamados"])


def buscar_ou_404(db: Session, chamado_id: int) -> Chamado:
    """Procura um chamado pelo id. Se não existir, responde com erro 404."""
    chamado = db.get(Chamado, chamado_id)
    if chamado is None:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    return chamado


# POST /chamados: ABRE um novo chamado.
# status_code=201 é o código HTTP de "criado com sucesso".
@router.post("", response_model=ChamadoOut, status_code=201)
def criar_chamado(dados: ChamadoCreate, db: Session = Depends(get_db)):
    # mode="json" converte os Enums em texto simples antes de salvar no banco.
    chamado = Chamado(**dados.model_dump(mode="json"), status=Status.aberto.value)
    db.add(chamado)  # marca para salvar
    db.commit()      # grava de fato no banco
    db.refresh(chamado)  # recarrega para pegar o id e a data gerados
    return chamado


# GET /chamados: LISTA os chamados, com filtros opcionais na URL.
# Exemplo: /chamados?status=aberto&tipo=rede&busca=impressora
@router.get("", response_model=list[ChamadoOut])
def listar_chamados(
    status: Status | None = None,
    tipo: Tipo | None = None,
    unidade: str | None = None,
    busca: str | None = Query(default=None, max_length=100),
    limite: int = Query(default=100, ge=1, le=500),  # máximo de resultados
    deslocamento: int = Query(default=0, ge=0),      # quantos pular (paginação)
    db: Session = Depends(get_db),
):
    consulta = select(Chamado)

    # Cada filtro só é aplicado se o usuário o enviou.
    if status:
        consulta = consulta.where(Chamado.status == status.value)
    if tipo:
        consulta = consulta.where(Chamado.tipo == tipo.value)
    if unidade:
        consulta = consulta.where(Chamado.unidade == unidade)
    if busca:
        # ilike = "contém" sem diferenciar maiúsculas de minúsculas.
        padrao = f"%{busca}%"
        consulta = consulta.where(
            or_(
                Chamado.titulo.ilike(padrao),
                Chamado.descricao.ilike(padrao),
                Chamado.solicitante.ilike(padrao),
            )
        )

    # Os mais recentes primeiro.
    consulta = consulta.order_by(Chamado.aberto_em.desc()).limit(limite).offset(deslocamento)
    return db.scalars(consulta).all()


# GET /chamados/resumo: números para o painel.
# IMPORTANTE: esta rota fica ANTES de /chamados/{id}; senão o FastAPI
# tentaria entender a palavra "resumo" como se fosse um id.
@router.get("/resumo", response_model=Resumo)
def resumo(db: Session = Depends(get_db)):
    todos = db.scalars(select(Chamado)).all()

    por_status = {s.value: 0 for s in Status}  # começa tudo com zero
    estourados = 0
    for chamado in todos:
        por_status[chamado.status] += 1
        if sla_estourado(chamado.tipo, chamado.aberto_em, chamado.resolvido_em):
            estourados += 1

    return Resumo(total=len(todos), por_status=por_status, sla_estourados=estourados)


# GET /chamados/unidades: lista as unidades que já abriram chamados.
# Usada para montar o filtro e as sugestões do formulário.
@router.get("/unidades", response_model=list[str])
def listar_unidades(db: Session = Depends(get_db)):
    return db.scalars(select(Chamado.unidade).distinct().order_by(Chamado.unidade)).all()


# GET /chamados/1: devolve UM chamado pelo id.
@router.get("/{chamado_id}", response_model=ChamadoOut)
def obter_chamado(chamado_id: int, db: Session = Depends(get_db)):
    return buscar_ou_404(db, chamado_id)


# PATCH /chamados/1/status: MUDA o status (PATCH altera só uma parte do recurso).
@router.patch("/{chamado_id}/status", response_model=ChamadoOut)
def atualizar_status(chamado_id: int, dados: StatusUpdate, db: Session = Depends(get_db)):
    chamado = buscar_ou_404(db, chamado_id)
    chamado.status = dados.status.value

    if dados.status in (Status.resolvido, Status.fechado):
        # Registra o momento da resolução só na primeira vez.
        if chamado.resolvido_em is None:
            chamado.resolvido_em = datetime.now(timezone.utc)
    else:
        # Chamado reaberto: apaga a data de resolução.
        chamado.resolvido_em = None

    db.commit()
    db.refresh(chamado)
    return chamado


# DELETE /chamados/1: REMOVE o chamado.
# 204 = "feito, e não há nada para devolver".
@router.delete("/{chamado_id}", status_code=204)
def excluir_chamado(chamado_id: int, db: Session = Depends(get_db)):
    chamado = buscar_ou_404(db, chamado_id)
    db.delete(chamado)
    db.commit()
    return Response(status_code=204)
