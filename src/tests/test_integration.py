import pytest
import json
import time
import redis
import os
from src.analyzer import analyze_health_check
from src.models import Base, HealthCheck
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

def test_analyze_health_check():
    payload = {
        "site": "https://example.com",
        "response_time": 0.5,
        "status_code": 200,
        "error": None
    }
    analyze_health_check(payload)
    session = Session()
    health_check = session.query(HealthCheck).filter_by(site="https://example.com").first()
    assert health_check is not None
    assert health_check.response_time > 0
    assert health_check.status_code == 200
    assert health_check.error is None