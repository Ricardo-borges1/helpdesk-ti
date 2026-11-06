"""Configuração dos testes: usa um banco SQLite em memória, sem tocar no PostgreSQL."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    # StaticPool mantém uma única conexão, para o banco em memória não sumir entre as chamadas.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Sessao = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def get_db_teste():
        db = Sessao()
        try:
            yield db
        finally:
            db.close()

    # Troca o banco real pelo banco de teste.
    app.dependency_overrides[get_db] = get_db_teste
    # Sem "with", o TestClient não executa o lifespan (que tentaria usar o PostgreSQL).
    yield TestClient(app)
    app.dependency_overrides.clear()
