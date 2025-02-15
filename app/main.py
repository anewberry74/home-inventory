from typing import Annotated
import uuid

from fastapi import FastAPI, Depends, HTTPException, Query, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import models
import db_conn
from inventory_api import inventory_api
from inventory_ui import inventory_ui


templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(inventory_api)
app.include_router(inventory_ui)


# Create Database Tables on Startup
# ToDO - This is not the best way to create tables
# look at using Alembic for migrations
@app.on_event("startup")
def on_startup():
    db_conn.create_db_and_tables()


# Home Page
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})
