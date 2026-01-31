#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, HealthCheck, Site
import redis

r = redis.Redis(host="localhost", port=6379)
r.set("ping", "pong")

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

app = Flask(__name__)


def init_db():
    Base.metadata.create_all(engine)

def fetch_sites():
    pass

def db_add_site(url):
    session = Session()
    site = Site(url=url)
    try:
        #lookup if site already exists
        if session.query(Site).filter_by(url=url).first():
            return "Site already exists"
        session.add(site)
        session.commit()
    except Exception as e:
        session.rollback()
        return "Error adding site: " + str(e)
    finally:
        session.close()
    return "Site added successfully"

def db_get_dashboard_data():
    session = Session()
    sites = session.query(Site).all()
    checks = session.query(HealthCheck).order_by(HealthCheck.created_at.desc()).limit(20).all()
    session.close()
    return sites, checks

@app.route("/")
def main():
    sites, checks = db_get_dashboard_data()
    return render_template("index.html", sites=sites, checks=checks)

@app.route("/", methods=["POST"])
def add_site():
    input_text = request.form.get("site", "")
    if not input_text:
        return "No site provided"
    result = db_add_site(input_text)
    sites, checks = db_get_dashboard_data()
    return render_template("index.html", sites=sites, checks=checks)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)