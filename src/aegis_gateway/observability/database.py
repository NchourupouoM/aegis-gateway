from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from aegis_gateway.core.config import get_settings
from aegis_gateway.core.logger import logger

settings = get_settings()

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def init_db():
    """Initialise les tables de la base de données au démarrage."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("🗄️ Base de données FinOps initialisée avec succès.")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dépendance FastAPI pour injecter la session DB asynchrone."""
    async with AsyncSessionLocal() as session:
        yield session