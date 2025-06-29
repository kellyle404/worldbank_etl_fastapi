from loguru import logger

logger.add("logs/etl.log", format="{time} {level} {message}", level="INFO", rotation="404 MB")