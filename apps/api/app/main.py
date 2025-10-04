from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import time


def create_app() -> FastAPI:
    app = FastAPI(title="Cloud Native Infra Simulation API", version=os.getenv("APP_VERSION", "0.1.0"))

    @app.get("/")
    async def root() -> dict:
        return {"service": "api", "status": "ok"}

    @app.get("/healthz")
    async def healthz() -> dict:
        return {"ok": True}

    @app.get("/livez")
    async def livez() -> dict:
        return {"alive": True}

    @app.get("/readyz")
    async def readyz() -> JSONResponse:
        # Placeholder for future checks (DB/Redis). Keep fast and simple for now.
        return JSONResponse(status_code=200, content={"ready": True})

    @app.get("/version")
    async def version() -> dict:
        return {"version": os.getenv("APP_VERSION", "0.1.0"), "commit": os.getenv("GIT_SHA", "dev")}

    # Slow endpoint to generate measurable latency
    @app.get("/simulate/slow")
    async def simulate_slow() -> dict:
        time.sleep(0.4)
        return {"ok": True, "delay_ms": 400}

    return app


app = create_app()


