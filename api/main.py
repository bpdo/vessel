from fastapi import FastAPI
import logging

from .routers import models, versions
from .utils import db

# configure logging for info level
logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.include_router(models.router, prefix="/models")
app.include_router(versions.router, prefix="/versions")


@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()
