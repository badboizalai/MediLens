from fastapi import FastAPI

app = FastAPI(title="MediLens phi-service")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
