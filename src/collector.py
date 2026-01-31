import os
import requests
import time
import redis
import json
import schedule
from dotenv import load_dotenv
from src.models import Site
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


POSTGRES_SERVER = os.getenv("POSTGRES_SERVER")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}"
    f"@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def db_get_sites():
    session = Session()
    sites = session.query(Site).all()
    session.close()
    return sites

def fetch_site(site):
    try:
        start = time.time()
        response = requests.get(site, timeout=10)
        latency = time.time() - start

        payload = {
            "site": site,
            "response_time": latency,
            "status_code": response.status_code,
            "error": None
        }

    except Exception as e:
        payload = {
            "site": site,
            "response_time": None,
            "status_code": None,
            "error": str(e)
        }

    print("Publishing:", payload)
    r.publish("latency", json.dumps(payload))

def execute_health_checks():
    sites = db_get_sites()
    for site in sites:
        fetch_site(site.url)
    print("Health checks executed for URLs:", [site.url for site in sites])



if __name__ == "__main__":
    schedule.every(15).seconds.do(execute_health_checks)

    while True:
        schedule.run_pending()
        time.sleep(1)