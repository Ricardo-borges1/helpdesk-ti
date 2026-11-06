"""Schemas: descrevem e validam os dados que ENTRAM e SAEM da API (Pydantic)."""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from app.sla import calcular_prazo, como_utc, sla_estourado


class Status(str, Enum):
    """Valores permitidos para o status. Qualquer outro valor é recusado."""

    aberto = "aberto"
    em_andamento = "em_andamento"
    resolvido = "resolvido"
    fechado = "fechado"


class Tipo(str, Enum):
    """Tipos de chamado. Cada um tem um prazo de SLA (veja app/sla.py)."""

    impressora = "impressora"
    rede = "rede"
    software = "software"
    hardware = "hardware"
    outros = "outros"


class ChamadoCreate(BaseModel):
    """O que o usuário ENVIA ao abrir um chamado."""

    # str_strip_whitespace remove espaços sobrando no começo e no fim dos textos.
    model_config = ConfigDict(str_strip_whitespace=True)

    titulo: str = Field(min_length=3, max_length=120)
    descricao: str = Field(min_length=3)
    solicitante: str = Field(min_length=2, max_length=100)
    unidade: str = Field(min_length=2, max_length=100)
    tipo: Tipo


class StatusUpdate(BaseModel):
    """O que o usuário ENVIA para mudar o status de um chamado."""

    status: Status


class ChamadoOut(ChamadoCreate):
    """O que a API DEVOLVE: os dados enviados + os campos que o sistema controla."""

    # from_attributes=True deixa o Pydantic ler direto de um objeto do banco (Chamado).
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    id: int
    status: Status
    aberto_em: datetime
    resolvido_em: datetime | None = None

    @field_validator("aberto_em", "resolvido_em")
    @classmethod
    def datas_em_utc(cls, valor: datetime | None) -> datetime | None:
        """Garante que as datas saiam com fuso (ex.: 2026-10-29T12:00:00Z).

        Sem isso o navegador interpretaria a hora como local e mostraria errado.
        """
        return como_utc(valor) if valor else valor

    # computed_field: campo calculado na hora de responder (não fica salvo no banco).
    @computed_field
    @property
    def prazo_sla(self) -> datetime:
        return calcular_prazo(self.tipo, self.aberto_em)

    @computed_field
    @property
    def sla_estourado(self) -> bool:
        return sla_estourado(self.tipo, self.aberto_em, self.resolvido_em)


class Resumo(BaseModel):
    """Números para o painel: total, quantidade por status e SLAs estourados."""

    total: int
    por_status: dict[str, int]
    sla_estourados: int
