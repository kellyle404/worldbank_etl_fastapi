from src.models.models import SessionLocal, Topic, IndicatorMeta, Country, IndicatorValue
from utils.logger import logger

# needed 2 seprate since i choose to load the meta first, ind values depend on the meta like countries existing so...
def load_dimensions(topics_df, indicators_df, countries_df):
    session = SessionLocal()
    try:
        session.bulk_save_objects([Topic(id=row.id, name=row.name) for row in topics_df.itertuples()])
        session.commit()

        session.bulk_save_objects([IndicatorMeta(code=row.code, name=row.name, topic_id=row.topic_id, source_note=row.source_note) for row in indicators_df.itertuples()])
        session.commit()

        session.bulk_save_objects([Country(iso3=row.iso3, name=row.name, region=row.region) for row in countries_df.itertuples()])
        session.commit()

        logger.info("Dimensions loaded successfully.")

    except Exception as e:
        session.rollback()
        logger.error(f"Error during dimension load: {e}")
        raise

    finally:
        session.close()

def load_values(values_df):
    session = SessionLocal()
    try:
        indicator_map = {ind.code: ind.id for ind in session.query(IndicatorMeta).all()}
        country_map = {c.iso3: c.id for c in session.query(Country).all()}

        value_objs = []
        for row in values_df.itertuples():
            ind_id = indicator_map.get(row.indicator_code)
            ctry_id = country_map.get(row.iso3)
            if ind_id and ctry_id:
                value_objs.append(IndicatorValue(indicator_id=ind_id, country_id=ctry_id, date=row.date, value=row.value))
        session.bulk_save_objects(value_objs)
        session.commit()

    except Exception as e:
        session.rollback()
        logger.error(f"Error during values load: {e}")
        raise

    finally:
        session.close()
