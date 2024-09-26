from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    """
    Readiness probe.
    """
    return {"status": "healthy"}

@app.get("/liveness")
async def liveness_check():
    """
    Liveness probe.
    """
    return {"status": "alive"}
