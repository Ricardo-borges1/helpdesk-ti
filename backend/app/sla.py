"""Regras de SLA (prazo máximo de atendimento) de cada tipo de chamado."""
from datetime import datetime, timedelta, timezone

# Prazo em HORAS para resolver cada tipo de chamado.
# Ajuste os valores à realidade do seu setor.
SLA_HORAS = {
    "impressora": 8,
    "rede": 4,
    "software": 24,
    "hardware": 24,
    "outros": 48,
}


def como_utc(momento: datetime) -> datetime:
    """Garante que a data tenha fuso horário (UTC).

    Alguns bancos (como o SQLite usado nos testes) devolvem datas "sem fuso".
    Aqui assumimos que elas já estão em UTC, que é como salvamos tudo.
    """
    if momento.tzinfo is None:
        return momento.replace(tzinfo=timezone.utc)
    return momento


def calcular_prazo(tipo, aberto_em: datetime) -> datetime:
    """Data e hora limite para resolver o chamado."""
    # "tipo" pode chegar como Enum ou como texto; .value pega o texto nos dois casos.
    chave = getattr(tipo, "value", tipo)
    return como_utc(aberto_em) + timedelta(hours=SLA_HORAS[chave])


def sla_estourado(tipo, aberto_em: datetime, resolvido_em: datetime | None = None) -> bool:
    """True se o chamado passou do prazo.

    - Chamado já resolvido: compara a data de resolução com o prazo.
    - Chamado ainda em aberto: compara o momento atual com o prazo.
    """
    prazo = calcular_prazo(tipo, aberto_em)
    referencia = como_utc(resolvido_em) if resolvido_em else datetime.now(timezone.utc)
    return referencia > prazo
