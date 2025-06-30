import requests
from app.utils.logger import logger

def fetch_indicator_metadata():
    indicators = []
    page = 1
    while True:
        url = f"http://api.worldbank.org/v2/indicator?format=json&per_page=1000&page={page}"
        res = requests.get(url)
        if res.status_code != 200: break
        data = res.json()
        if not data or len(data) < 2: break
        indicators.extend(data[1])
        if page >= data[0]['pages']: break
        page += 1
    logger.info(f"Fetched {len(indicators)} indicators")
    return indicators

def fetch_indicator_values(indicator_code):
    all_data = []
    page = 1
    while True:
        url = f"http://api.worldbank.org/v2/country/all/indicator/{indicator_code}?format=json&per_page=1000&page={page}"
        res = requests.get(url)
        if res.status_code != 200: break
        data = res.json()
        if not data or len(data) < 2: break
        all_data.extend(data[1])
        if page >= data[0]['pages']: break
        page += 1
    # logger.info(f"Fetched {len(all_data)} indicator values for {indicator_code}")
    return all_data

def fetch_all_countries():
    countries = []
    page = 1
    while True:
        url = f"http://api.worldbank.org/v2/country?format=json&per_page=1000&page={page}"
        res = requests.get(url)
        if res.status_code != 200: break
        data = res.json()
        if not data or len(data) < 2: break
        countries.extend(data[1])
        if page >= data[0]['pages']: break
        page += 1
    logger.info(f"Fetched {len(countries)} countries")
    return countries

def fetch_all_topics():
    url = "http://api.worldbank.org/v2/topic?format=json"
    res = requests.get(url)
    if res.status_code != 200: return []
    data = res.json()
    topics = data[1] if data and len(data) > 1 else []
    logger.info(f"Fetched {len(topics)} topics")
    return topics
