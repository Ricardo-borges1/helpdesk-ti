# Helpdesk TI

Sistema de chamados de suporte de TI, com prazo de **SLA** calculado por tipo de chamado,
filtros, busca e painel de resumo por status.

Projeto de portfólio feito com **React**, **FastAPI** e **PostgreSQL**.

> Os dados de exemplo são fictícios. Nunca coloque neste repositório dados reais de pessoas,
> senhas ou chaves.

## O que o sistema faz

- Abrir, listar, buscar, filtrar, mudar o status e excluir chamados
- Calcular o prazo de SLA de cada chamado e mostrar quanto falta (ou quanto estourou)
- Mostrar a distribuição dos chamados por status; clicar em um status filtra a lista
- Gerar chamados fictícios para teste (`seed`)
- API documentada automaticamente em `/docs` e coberta por testes automáticos

## Tecnologias

| Parte | Tecnologia |
|---|---|
| Front-end | React 18 + Vite |
| Back-end | Python + FastAPI + SQLAlchemy |
| Banco de dados | PostgreSQL 16 |
| Testes | pytest |
| Containers | Docker e Docker Compose |

## Como rodar (Windows, Mac ou Linux)

Pré-requisitos: **Git**, **Docker Desktop** (aberto e rodando) e **Node.js LTS**.

```bash
# 1. Baixar o projeto
git clone https://github.com/SEU_USUARIO/helpdesk-ti.git
cd helpdesk-ti

# 2. Subir banco + API (a primeira vez demora um pouco)
docker compose up --build

# 3. Em OUTRO terminal: criar chamados de exemplo
docker compose exec backend python -m app.seed 120

# 4. Em OUTRO terminal: subir o front-end
cd frontend
npm install
npm run dev
```

Depois, abra:

- Aplicação: http://localhost:5173
- Documentação da API: http://localhost:8000/docs

Para parar tudo: `Ctrl + C` em cada terminal e `docker compose down`
(os dados continuam salvos; para apagá-los use `docker compose down -v`).

## Rodando os testes do back-end

```bash
cd backend
python -m venv .venv
# Windows (PowerShell): .\.venv\Scripts\Activate.ps1
# Mac/Linux:            source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Os testes usam um banco SQLite em memória; não precisam do Docker.

## Estrutura

```
helpdesk-ti/
├── docker-compose.yml     # banco + API
├── backend/
│   ├── app/
│   │   ├── main.py        # cria o app e liga as rotas
│   │   ├── database.py    # conexão com o banco
│   │   ├── models.py      # tabela de chamados
│   │   ├── schemas.py     # validação dos dados de entrada e saída
│   │   ├── sla.py         # regras de prazo por tipo de chamado
│   │   ├── seed.py        # gera chamados fictícios
│   │   └── routers/chamados.py   # rotas da API
│   ├── tests/             # testes automáticos
│   ├── Dockerfile
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.jsx        # estado da tela e chamadas à API
        ├── api.js         # comunicação com o back-end
        └── components/    # Resumo, Filtros, TabelaChamados, FormChamado
```

## Rotas da API

| Método | Rota | O que faz |
|---|---|---|
| POST | `/chamados` | Abre um chamado |
| GET | `/chamados` | Lista, com filtros `status`, `tipo`, `unidade`, `busca` |
| GET | `/chamados/{id}` | Mostra um chamado |
| PATCH | `/chamados/{id}/status` | Muda o status |
| DELETE | `/chamados/{id}` | Exclui o chamado |
| GET | `/chamados/resumo` | Totais por status e SLAs estourados |
| GET | `/chamados/unidades` | Unidades que já abriram chamados |
| GET | `/health` | Verifica se a API está no ar |

## SLA por tipo de chamado

| Tipo | Prazo |
|---|---|
| Rede | 4 h |
| Impressora | 8 h |
| Software | 24 h |
| Hardware | 24 h |
| Outros | 48 h |

Os valores ficam em `backend/app/sla.py`.

## Próximos passos

- [ ] Login de usuários (técnicos e solicitantes)
- [ ] Migrações do banco com Alembic
- [ ] Dockerfile do front-end (build + servidor web)
- [ ] Pipeline de CI no GitHub Actions (testes a cada push)
- [ ] Publicação na nuvem (Azure)
- [ ] Dashboard de análise dos chamados (Power BI ou Python)
