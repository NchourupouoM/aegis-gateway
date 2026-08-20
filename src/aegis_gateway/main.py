from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aegis_gateway.api.v1.health import router as health_router
from aegis_gateway.core.config import get_settings
from aegis_gateway.core.logger import logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} in [{settings.APP_ENV}] mode...")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Aegis-LLM Security Firewall & Smart Gateway",
        description="Enterprise-grade AI Guardrail Proxy with PII Masking, Smart Cost Routing & Failover.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(health_router)

    return app


app = create_app()