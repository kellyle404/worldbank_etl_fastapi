import pandas as pd
from config.config import MIN_YEAR, MAX_YEAR
from utils.logger import logger

def transform_topics(topics_raw):
    df = pd.DataFrame([{
        "id": int(t["id"]),
        "name": t["value"],
    } for t in topics_raw])
    return df

def transform_indicators_meta(indicators_raw):
    df = pd.DataFrame([{
        "code": i["id"],
        "name": i["name"],
        "topic_id": int(i["topics"][0]["id"]) if (
            i.get("topics") and len(i["topics"]) > 0 and i["topics"][0].get("id") is not None
        ) else None,
        "source_note": i.get("sourceNote", "")
    } for i in indicators_raw])
    df.drop_duplicates(subset=["code"], inplace=True)
    df = df[df["topic_id"].notna()].copy()
    df["topic_id"] = df["topic_id"].astype(int)
    return df

def transform_countries(countries_raw):
    df = pd.DataFrame([{
        "iso3": c["id"],
        "name": c["name"],
        "region": c["region"]["value"] if c.get("region") else None,
    } for c in countries_raw])
    df.drop_duplicates(subset=["iso3"], inplace=True)
    return df

def transform_indicator_values(values_raw):
    rows = []
    for d in values_raw:
        date_str = d["date"]
        try:
            year = int(date_str)
        except ValueError:
            continue

        if d.get("value") is None:
            continue

        if year < MIN_YEAR or year > MAX_YEAR:
            continue

        rows.append({
            "indicator_code": d["indicator"]["id"],
            "iso3": d["countryiso3code"],
            "date": year,
            "value": float(d["value"])
        })

    df = pd.DataFrame(rows)
    print(df.head())
    return df