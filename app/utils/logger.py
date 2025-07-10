from loguru import logger
from datetime import datetime
from app.db.db import SessionLocal
from app.models.models import ETLLog

# log to file
logger.add("logs/etl.log", format="{time} {level} {message}", level="INFO", rotation="404 MB")

# log to database
def db_sink(message):
    record = message.record
    session = SessionLocal()

    try:
        log_entry = ETLLog(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            level=record["level"].name,
            message=record["message"],
        )
        session.add(log_entry)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()

logger.add(db_sink, level="INFO")
