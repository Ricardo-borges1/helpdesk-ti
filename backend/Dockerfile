# Imagem base: Python 3.12 em versão enxuta
FROM python:3.12-slim

# Pasta de trabalho dentro do container
WORKDIR /code

# Copia só o requirements.txt primeiro: assim o Docker reaproveita o cache
# das dependências enquanto elas não mudarem.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da API
COPY app ./app

# Porta que a API usa
EXPOSE 8000

# Comando que inicia a API (0.0.0.0 permite acesso de fora do container)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
