from fastapi import FastAPI

app = FastAPI(title="Helpdesk TI")


@app.get("/health")
def health():
    return {"status": "ok"}