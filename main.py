import os

from dotenv import load_dotenv
from flask import Flask, request, wrappers

from utils.mongo import MongoConnection

load_dotenv()

db = MongoConnection(os.getenv("mongo_url"), "CopDetektor", "Logs")

app = Flask(__name__)


@app.errorhandler(404)
def response_404():
    return "404 - Page not found."


@app.route("/log", methods=["POST"])
def log():
    return db.log(request.get_json())


@app.route("/get/today")
def get_today():
    return db.get_todays_log()


@app.route("/get/week")
def get_week():
    return list(db.get_weeks_logs())


@app.route("/get/gap")
def get_gap():
    args = request.args
    try:
        x = int(args["x"])
        y = int(args["y"])
    except (ValueError, KeyError):
        return "Invalid"
    return db.get_from_gap(x=x, y=y)


@app.after_request
def add_header(response: wrappers.Response):
    response.headers["Cache-Control"] = "no-store"
    return response

# app.run()
