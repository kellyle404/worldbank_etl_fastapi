from src.etl.extract import fetch_indicator_metadata, fetch_indicator_values, fetch_all_countries, fetch_all_topics
from src.etl.transform import transform_topics, transform_indicators_meta, transform_countries, transform_indicator_values
from src.etl.load import load_dimensions, load_values
from src.models.models import Base, engine
from utils.logger import logger
from config.config import MIN_YEAR, MAX_YEAR


if __name__ == "__main__":

    logger.info("Starting ETL process")

    topics_raw = fetch_all_topics()
    indicators_raw = fetch_indicator_metadata()
    countries_raw = fetch_all_countries()

    logger.info(f"Transforming indicators data from {MIN_YEAR} to {MAX_YEAR}.")

    topics_df = transform_topics(topics_raw)
    print(topics_df["id"].unique())

    indicators_df = transform_indicators_meta(indicators_raw)
    print(indicators_df["topic_id"].unique())
    print(indicators_df.head())

    countries_df = transform_countries(countries_raw)
    indicators_df = indicators_df.sample(n=20, random_state=404).copy()

    Base.metadata.create_all(engine)

    load_dimensions(topics_df, indicators_df, countries_df)

    for code in indicators_df["code"]:
        values_raw = fetch_indicator_values(code)

        if not values_raw:
            logger.warning(f"No data for indicator: {code}")
            continue

        values_df = transform_indicator_values(values_raw)
        print(values_df.head(2))

        try:
            load_values(values_df)
            logger.info(f"Loaded indicator: {code}")
        except Exception as e:
            logger.error(f"Failed to load indicator: {code}. Error: {e}")

    logger.info("ETL process completed successfully.")
