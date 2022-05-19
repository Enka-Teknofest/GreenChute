from motor.motor_asyncio import AsyncIOMotorClient
import os
import time
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime, timedelta


class Log(BaseModel):
    password: str
    values: list[int]


db = AsyncIOMotorClient(os.getenv("MONGO_URI"))["GreenChute"]["logs"]
app = FastAPI(docs_url=None, redoc_url="/docs")
log_pwd = os.getenv("LOG_PWD")

app.mount("/static", StaticFiles(directory="app/static"), name="app/static")
templates = Jinja2Templates(directory="app/templates")


def midnight_ts() -> int:
    ts = int(time.time())
    return ts - (ts % 86400)


def week_start_end_ts() -> tuple[int, int]:
    date_obj = datetime.utcnow().date()
    start_of_week = date_obj - timedelta(days=date_obj.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return int(time.mktime(start_of_week.timetuple())), int(time.mktime(end_of_week.timetuple()))


async def get_week_logs() -> list[list[int]]:
    start, end = week_start_end_ts()
    week = [day["values"] async for day in db.find({"_id": {"$gte": start, "$lte": end}}).sort("_id", 1)]
    while len(week) < 7:
        week.append([0, 0, 0])
    return week


@app.get("/favicon.ico", response_class=FileResponse, include_in_schema=False)
async def favicon() -> FileResponse:
    return FileResponse("app/static/favicon.ico")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    today = await db.find_one({"_id": midnight_ts()}, {"_id": 0})
    today = [0, 0, 0] if today is None else today["values"]
    week = await get_week_logs()
    week_sum = [0, 0, 0]
    for day in week:
        week_sum = [cur + add for cur, add in zip(week_sum, day)]
    return templates.TemplateResponse("index.jinja2", {"t": today, "w": week_sum, "request": request})


@app.get("/haftalik_rapor", response_class=HTMLResponse)
async def haftalik_rapor(request: Request):
    week = await get_week_logs()
    return templates.TemplateResponse("week_log.jinja2", {"w": week, "request": request, "zip": zip})


@app.post("/api/v1/log")
async def _log(log: Log) -> dict[str, int | str]:
    if log.password != log:
        return {"code": 401, "message": "Invalid password."}
    if len(log.values) != 3:
        return {"code": 400, "message": "Lists must have 3 values."}
    today = midnight_ts()
    result = await db.find_one({"_id": today}, {"_id": 0})
    if result is None:
        await db.insert_one({"_id": today, "values": log.values})
    else:
        updated = [cur + add for cur, add in zip(result["values"], log.values)]
        await db.update_one({"_id": today}, {"$set": {"values": updated}})
    return {"code": 200, "message": "Logged"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)  # type: ignore
