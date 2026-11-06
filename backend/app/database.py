"""Conexão com o banco de dados (PostgreSQL) usando SQLAlchemy."""
import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Endereço do banco. Vem da variável de ambiente DATABASE_URL (o Docker Compose define).
# Se não existir, usa o PostgreSQL local do docker-compose.yml (porta 5432).
# Formato: postgresql+psycopg://USUARIO:SENHA@SERVIDOR:PORTA/NOME_DO_BANCO
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://helpdesk:helpdesk@localhost:5432/helpdesk",
)

# O "engine" é o objeto que sabe conversar com o banco.
# pool_pre_ping=True testa a conexão antes de usar, evitando erros de conexão antiga.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Fábrica de sessões. Cada requisição à API usa uma sessão própria.
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Classe base de todos os modelos (tabelas) do projeto."""


def get_db() -> Generator[Session, None, None]:
    """Entrega uma sessão do banco para a rota e a fecha no final.

    As rotas usam isto com Depends(get_db) (injeção de dependência do FastAPI).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
