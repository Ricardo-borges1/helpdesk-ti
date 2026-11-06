"""Gera chamados FICTÍCIOS para testar o app e alimentar o dashboard.

Uso (dentro da pasta backend):
    python -m app.seed            -> cria 120 chamados (só se a tabela estiver vazia)
    python -m app.seed 300        -> cria 300 chamados
    python -m app.seed 300 --limpar -> apaga os chamados existentes antes de criar

Nunca coloque dados reais de pessoas ou da Prefeitura aqui.
"""
import random
import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select

from app.database import Base, SessionLocal, engine
from app.models import Chamado
from app.sla import SLA_HORAS

UNIDADES = [
    "Secretaria de Administração",
    "Secretaria de Educação",
    "Secretaria de Saúde",
    "Secretaria de Obras",
    "UBS Central",
    "Almoxarifado Central",
    "Recursos Humanos",
]

NOMES = ["Ana", "Bruno", "Carla", "Diego", "Elisa", "Fábio", "Gisele", "Hugo", "Iara", "João"]

# Títulos de exemplo para cada tipo de chamado.
TITULOS = {
    "impressora": ["Impressora não imprime", "Papel agarrando na impressora", "Impressora sem toner"],
    "rede": ["Sem acesso à internet", "Rede lenta no setor", "Ponto de rede sem sinal"],
    "software": ["Erro ao abrir planilha", "Instalar programa de edição", "Sistema fecha sozinho"],
    "hardware": ["Computador não liga", "Monitor sem imagem", "Teclado com teclas falhando"],
    "outros": ["Dúvida de acesso ao e-mail", "Solicitar novo ramal", "Mover equipamento de sala"],
}


def gerar_chamado(agora: datetime) -> Chamado:
    tipo = random.choice(list(SLA_HORAS))
    # Abertura nos últimos 90 dias. Elevar ao quadrado concentra mais chamados
    # nos dias recentes, como numa fila real (assim sempre há chamados em aberto).
    segundos = int(90 * 24 * 3600 * random.random() ** 2)
    aberto_em = agora - timedelta(seconds=max(segundos, 60))
    idade_horas = (agora - aberto_em).total_seconds() / 3600

    # Chamados mais antigos têm mais chance de já estarem resolvidos.
    if idade_horas > 72:
        status = random.choices(["resolvido", "fechado", "em_andamento", "aberto"], [45, 45, 6, 4])[0]
    else:
        status = random.choices(["aberto", "em_andamento", "resolvido", "fechado"], [40, 35, 15, 10])[0]

    resolvido_em = None
    if status in ("resolvido", "fechado"):
        # Tempo de resolução: entre 20 min e 1,25x o SLA (uma parte estoura o prazo).
        horas = random.uniform(0.3, SLA_HORAS[tipo] * 1.25)
        resolvido_em = min(aberto_em + timedelta(hours=horas), agora)

    return Chamado(
        titulo=random.choice(TITULOS[tipo]),
        descricao="Chamado de exemplo gerado automaticamente para testes.",
        solicitante=random.choice(NOMES),
        unidade=random.choice(UNIDADES),
        tipo=tipo,
        status=status,
        aberto_em=aberto_em,
        resolvido_em=resolvido_em,
    )


def main() -> None:
    argumentos = sys.argv[1:]
    limpar = "--limpar" in argumentos
    numeros = [a for a in argumentos if a.isdigit()]
    quantidade = int(numeros[0]) if numeros else 120

    Base.metadata.create_all(bind=engine)  # garante que a tabela existe
    agora = datetime.now(timezone.utc)

    with SessionLocal() as db:
        existentes = db.scalar(select(func.count()).select_from(Chamado))
        if existentes and not limpar:
            print(f"A tabela já tem {existentes} chamados. Use --limpar para recomeçar.")
            return
        if limpar:
            db.execute(delete(Chamado))
        db.add_all(gerar_chamado(agora) for _ in range(quantidade))
        db.commit()
        print(f"{quantidade} chamados fictícios criados.")


if __name__ == "__main__":
    main()
