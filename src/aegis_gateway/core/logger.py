import sys
from loguru import logger
from aegis_gateway.core.config import get_settings

settings = get_settings()

logger.remove()

# Format lisible en console avec coloration
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level="DEBUG" if settings.DEBUG else "INFO",
    colorize=True,
)