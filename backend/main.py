# ---------------------------------------------------------------
# IMPORTAÇÕES: trazemos de outras bibliotecas o que vamos usar
# ---------------------------------------------------------------

# datetime: guarda data e hora (usamos para registrar quando o chamado abriu/resolveu)
from datetime import datetime

# Enum: permite criar uma lista fechada de valores permitidos (usamos para o status)
from enum import Enum

# FastAPI: a classe principal que cria a API
# HTTPException: usada para devolver erros HTTP, como o 404 "não encontrado"
from fastapi import FastAPI, HTTPException

# BaseModel: base para criar modelos de dados com validação automática
# Field: permite definir regras extras em um campo (tamanho mínimo/máximo, por exemplo)
from pydantic import BaseModel, Field


# Cria a aplicação. O "title" aparece na documentação automática (/docs)
app = FastAPI(title="Helpdesk TI")


# ---------------------------------------------------------------
# MODELOS: descrevem o formato dos dados que entram e saem da API
# ---------------------------------------------------------------

# Status do chamado. Herdar de "str" faz o valor ser tratado como texto.
# Qualquer valor fora desta lista (ex.: "pendente") será recusado automaticamente.
class Status(str, Enum):
    aberto = "aberto"
    em_andamento = "em_andamento"
    resolvido = "resolvido"
    fechado = "fechado"


# O que o usuário ENVIA ao abrir um chamado.
# Os campos id, status e datas ficam de fora porque quem preenche é o sistema.
class ChamadoCreate(BaseModel):
    # min_length e max_length: o título precisa ter entre 3 e 120 caracteres.
    # Se não respeitar, a API responde com erro 422 sozinha.
    titulo: str = Field(min_length=3, max_length=120)
    descricao: str
    solicitante: str
    unidade: str  # ex.: "Secretaria de Administração"
    tipo: str     # ex.: "impressora", "rede", "software"


# O que o usuário ENVIA ao mudar o status de um chamado (só o novo status).
class StatusUpdate(BaseModel):
    status: Status


# O que a API DEVOLVE. Ela herda tudo de ChamadoCreate (título, descrição etc.)
# e acrescenta os campos que o sistema controla.
class Chamado(ChamadoCreate):
    id: int
    status: Status = Status.aberto  # todo chamado novo começa como "aberto"
    aberto_em: datetime
    resolvido_em: datetime | None = None  # "| None" = pode estar vazio até o chamado ser resolvido


# ---------------------------------------------------------------
# "BANCO DE DADOS" TEMPORÁRIO: guardado só na memória
# ---------------------------------------------------------------

# Lista que guarda todos os chamados. Ao reiniciar a API, ela volta a ficar vazia.
chamados: list[Chamado] = []

# Contador que gera o id de cada novo chamado (1, 2, 3...).
# Na Etapa 3, o banco de dados passa a fazer isso automaticamente.
proximo_id = 1


# Função auxiliar: procura um chamado pelo id.
# Se achar, devolve o chamado. Se não achar, devolve o erro 404.
# Criamos uma função para não repetir esse código em várias rotas.
def buscar_chamado(chamado_id: int) -> Chamado:
    for chamado in chamados:
        if chamado.id == chamado_id:
            return chamado
    raise HTTPException(status_code=404, detail="Chamado não encontrado")


# ---------------------------------------------------------------
# ROTAS: os "endereços" que a API oferece
# ---------------------------------------------------------------

# GET /health: rota simples só para saber se a API está viva.
# O decorador @app.get liga a função ao endereço e ao método GET.
@app.get("/health")
def health():
    return {"status": "ok"}


# POST /chamados: ABRE um novo chamado.
# response_model: diz qual formato será devolvido.
# status_code=201: código HTTP que significa "criado com sucesso".
@app.post("/chamados", response_model=Chamado, status_code=201)
def criar_chamado(dados: ChamadoCreate):  # "dados" é o JSON enviado, já validado
    # "global" permite alterar a variável proximo_id, que fica fora da função
    global proximo_id

    # Monta o chamado completo:
    # - id vem do contador
    # - aberto_em recebe a data e hora de agora
    # - **dados.model_dump() espalha os campos enviados (título, descrição...)
    chamado = Chamado(id=proximo_id, aberto_em=datetime.now(), **dados.model_dump())

    chamados.append(chamado)  # guarda na lista
    proximo_id += 1           # prepara o id do próximo chamado
    return chamado


# GET /chamados: LISTA os chamados.
# O parâmetro "status" é opcional: /chamados?status=aberto filtra só os abertos.
@app.get("/chamados", response_model=list[Chamado])
def listar_chamados(status: Status | None = None):
    if status is None:
        return chamados  # sem filtro: devolve todos
    # com filtro: devolve só os chamados cujo status é igual ao pedido
    return [c for c in chamados if c.status == status]


# GET /chamados/1: devolve UM chamado pelo id.
# {chamado_id} no endereço vira o parâmetro da função.
@app.get("/chamados/{chamado_id}", response_model=Chamado)
def obter_chamado(chamado_id: int):
    return buscar_chamado(chamado_id)


# PATCH /chamados/1/status: MUDA o status de um chamado.
# PATCH é o método usado quando alteramos só uma parte de algo.
@app.patch("/chamados/{chamado_id}/status", response_model=Chamado)
def atualizar_status(chamado_id: int, dados: StatusUpdate):
    chamado = buscar_chamado(chamado_id)  # acha o chamado (ou devolve 404)
    chamado.status = dados.status         # troca o status

    # Se o chamado foi resolvido/fechado e ainda não tem data de resolução,
    # registra o momento agora. Útil depois para calcular o tempo de resolução (SLA).
    if dados.status in (Status.resolvido, Status.fechado) and chamado.resolvido_em is None:
        chamado.resolvido_em = datetime.now()

    return chamado