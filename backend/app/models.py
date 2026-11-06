"""Modelos do banco: cada classe aqui vira uma tabela."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def agora_utc() -> datetime:
    """Momento atual em UTC. Salvamos tudo em UTC e o navegador converte para o horário local."""
    return datetime.now(timezone.utc)


class Chamado(Base):
    __tablename__ = "chamados"  # nome da tabela no banco

    # Chave primária: o banco gera 1, 2, 3... sozinho.
    id: Mapped[int] = mapped_column(primary_key=True)

    titulo: Mapped[str] = mapped_column(String(120))
    descricao: Mapped[str] = mapped_column(Text)  # Text permite textos longos
    solicitante: Mapped[str] = mapped_column(String(100))

    # index=True cria um índice: deixa as buscas e filtros por esses campos mais rápidas.
    unidade: Mapped[str] = mapped_column(String(100), index=True)
    tipo: Mapped[str] = mapped_column(String(30), index=True)
    status: Mapped[str] = mapped_column(String(20), default="aberto", index=True)

    aberto_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)
    # Fica vazio (NULL) até o chamado ser resolvido.
    resolvido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
