from sqlalchemy.dialects.postgresql import insert
from app.db.db import SessionLocal
from app.models.models import Topic, IndicatorMeta, Country
from app.utils.logger import logger
from app.models.models import IndicatorValue

def load_dimensions(topics_df, indicators_df, countries_df):
    session = SessionLocal()
    try:
        for row in topics_df.itertuples():
            stmt = insert(Topic).values(
                id=row.id,
                name=row.name
            ).on_conflict_do_update(
                index_elements=['id'],
                set_={'name': row.name}
            )
            session.execute(stmt)
        session.commit()
        for row in indicators_df.itertuples():
            stmt = insert(IndicatorMeta).values(
                code=row.code,
                name=row.name,
                topic_id=row.topic_id,
                source_note=row.source_note
            ).on_conflict_do_update(
                index_elements=['code'],
                set_={
                    'name': row.name,
                    'topic_id': row.topic_id,
                    'source_note': row.source_note
                }
            )
            session.execute(stmt)
        session.commit()

        for row in countries_df.itertuples():
            stmt = insert(Country).values(
                iso3=row.iso3,
                name=row.name,
                region=row.region
            ).on_conflict_do_update(
                index_elements=['iso3'],
                set_={
                    'name': row.name,
                    'region': row.region
                }
            )
            session.execute(stmt)
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

        for row in values_df.itertuples():
            ind_id = indicator_map.get(row.indicator_code)
            ctry_id = country_map.get(row.iso3)
            if not ind_id or not ctry_id:
                continue

            existing = session.query(IndicatorValue).filter_by(
                indicator_id=ind_id,
                country_id=ctry_id,
                date=row.date
            ).first()

            if existing:
                if existing.value != row.value:
                    logger.warning(
                        f"Overwriting IndicatorValue for indicator_id={ind_id}, country_id={ctry_id}, date={row.date} "
                        f"from {existing.value} to {row.value}"
                    )
                else:
                    continue

            stmt = insert(IndicatorValue).values(
                indicator_id=ind_id,
                country_id=ctry_id,
                date=row.date,
                value=row.value
            ).on_conflict_do_update(
                index_elements=['indicator_id', 'country_id', 'date'],
                set_={'value': row.value}
            )

            session.execute(stmt)

        session.commit()

    except Exception as e:
        session.rollback()
        logger.error(f"Error during values load: {e}")
        raise

    finally:
        session.close()
