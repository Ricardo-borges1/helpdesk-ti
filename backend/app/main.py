"""Ponto de entrada da API: cria o app e liga as rotas."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (importar garante que a tabela seja registrada)
from app.database import Base, engine
from app.routers import chamados


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Roda uma vez quando a API liga: cria as tabelas que ainda não existem."""
    Base.metadata.create_all(bind=engine)
    yield  # a API fica rodando aqui; o que viria depois do yield rodaria ao desligar


app = FastAPI(
    title="Helpdesk TI",
    version="1.0.0",
    description="API de chamados de suporte de TI, com prazo de SLA por tipo de chamado.",
    lifespan=lifespan,
)

# CORS: libera o front-end (em outra porta) para chamar a API pelo navegador.
# Os endereços permitidos vêm da variável CORS_ORIGINS, separados por vírgula.
origens = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origens,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chamados.router)


@app.get("/health", tags=["Sistema"])
def health():
    """Rota simples para saber se a API está no ar (útil no deploy)."""
    return {"status": "ok"}
