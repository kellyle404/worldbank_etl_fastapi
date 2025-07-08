from fastapi import FastAPI
from app.routers import countries, topics, indicators_meta, indicator_values


def create_app() -> FastAPI:
    app = FastAPI(
        title="World Bank ETL API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    app.include_router(countries.router, prefix="/countries", tags=["Countries"])
    app.include_router(topics.router, prefix="/topics", tags=["Topics"])
    app.include_router(indicators_meta.router, prefix="/indicators-meta", tags=["Indicators Metadata"])
    app.include_router(indicator_values.router, prefix="/indicator-values", tags=["Indicator Values"])

    return app
