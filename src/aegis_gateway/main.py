from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aegis_gateway.api.v1.analytics import router as analytics_router
from aegis_gateway.api.v1.chat import router as chat_router
from aegis_gateway.api.v1.health import router as health_router
from aegis_gateway.core.config import get_settings
from aegis_gateway.core.logger import logger
from aegis_gateway.observability.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f" Starting {settings.APP_NAME} in [{settings.APP_ENV}] mode...")
    # Initialisation de la base de données SQLite/PostgreSQL
    await init_db()
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Aegis-LLM Security Firewall & Smart Gateway",
        description="Enterprise AI Guardrail Proxy with PII Masking, Smart Routing & Resilience.",
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

    # Enregistrement des routes
    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(analytics_router)

    return app


app = create_app()