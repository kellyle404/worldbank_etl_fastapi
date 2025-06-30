import uvicorn
from fastapi import FastAPI
from app.routers import topics, indicators_meta, countries, indicator_values
from app.utils.logger import logger

desc = """
Welcome to Kely's World Bank API project!

This API provides access to a comprehensive dataset of global economic indicators, countries, topics, and related metadata sourced from the World Bank.
* CRUD endpoints for topics, indicators, countries, and indicator values.
Filter and paginate large datasets to locate relevant economic indicators or country data.

For questions visit:  
https://hngocle404.github.io/kalulus-lil-corner/"
"""

app = FastAPI(
    title="World Bank ETL API",
    version="1.0.0",
    description="desc"
)

app.include_router(topics.router)
app.include_router(indicators_meta.router)
app.include_router(countries.router)
app.include_router(indicator_values.router)

def main():
    logger.info("Server doc at http://127.0.0.1:8000/docs")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        access_log=False
    )

if __name__ == "__main__":
    main()
