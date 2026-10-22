from fastapi import FastAPI

app = FastAPI(title="MediLens ai-gateway")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
