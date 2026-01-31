import os
import redis
import json
import time
from src.models import HealthCheck
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
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


def analyze_health_check(payload):
    session = Session()
    health_check = HealthCheck(
        site=payload["site"],
        response_time=payload["response_time"],
        status_code=payload["status_code"],
        error=payload["error"]
    )
    session.add(health_check)
    session.commit()
    session.close()

if __name__ == "__main__":
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)

    pubsub = r.pubsub()
    pubsub.subscribe("latency")

    for message in pubsub.listen():
        print("Message:", message)
        if message["type"] == "message":
            payload = json.loads(message["data"])
            print("Received:", payload)
            analyze_health_check(payload)
            print("stored:", payload)