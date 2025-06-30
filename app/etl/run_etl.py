from app.etl.extract import fetch_indicator_metadata, fetch_indicator_values, fetch_all_countries, fetch_all_topics
from app.etl.transform import transform_topics, transform_indicators_meta, transform_countries, transform_indicator_values
from app.etl.load import load_dimensions, load_values
from app.models.models import Base
from app.db.db import engine
from app.core.config import settings
from app.utils.logger import logger

def main():
    Base.metadata.create_all(engine)

    logger.info("Starting ETL process")
    logger.info("Extracting data...")
    topics_raw = fetch_all_topics()
    indicators_raw = fetch_indicator_metadata()
    countries_raw = fetch_all_countries()

    logger.info(f"Data time range: {settings.MIN_YEAR} to {settings.MAX_YEAR}.")
    logger.info("Transforming data...")
    topics_df = transform_topics(topics_raw)
    indicators_df = transform_indicators_meta(indicators_raw)
    countries_df = transform_countries(countries_raw)

    indicators_df = indicators_df.sample(n=20, random_state=404).copy()

    logger.info("Loading data...")
    load_dimensions(topics_df, indicators_df, countries_df)

    for code in indicators_df["code"]:
        values_raw = fetch_indicator_values(code)

        if not values_raw:
            logger.warning(f"No data for indicator: {code}")
            continue

        values_df = transform_indicator_values(values_raw)

        try:
            load_values(values_df)
            logger.info(f"Loaded indicator: {code}")
        except Exception as e:
            logger.error(f"Failed to load indicator: {code}. Error: {e}")

    logger.info("ETL process completed successfully.")

if __name__ == "__main__":
    main()
