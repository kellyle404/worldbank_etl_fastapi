# scripts/run_api.py

import uvicorn
from app.api import create_app
from app.utils.logger import logger

if __name__ == "__main__":
    logger.info("Docs at http://127.0.0.1:8000/docs")
    uvicorn.run(
        create_app(),
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
