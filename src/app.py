#!/usr/bin/env python3

from flask import Flask, request
import requests
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, User
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

def fetch_users():
    print(r.get("ping"))
    url = "https://jsonplaceholder.typicode.com/users"
    response = requests.get(url)
    users = response.json()

    session = Session()

    for u in users:
        user = User(
            id=u["id"],
            name=u["name"],
            email=u["email"]
        )
        session.merge(user)

    session.commit()
    session.close()

@app.route("/")
def main():
    fetch_users()
    return '''
     <form action="/echo_user_input" method="POST">
         <input name="user_input">
         <input type="submit" value="Submit!">
     </form>
     '''

@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    input_text = request.form.get("user_input", "")
    return "You entered: " + input_text

if __name__ == "__main__":
    init_db()
    app.run(debug=True)