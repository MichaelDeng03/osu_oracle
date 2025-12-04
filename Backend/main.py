import logging
from contextlib import asynccontextmanager
from os import getenv

from dotenv import load_dotenv
from fastapi import FastAPI

logger = logging.getLogger(__name__)


app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    OSU_CLIENT_SECRET = getenv("OSU_CLIENT_SECRET")
    OSU_CLIENT_ID = getenv("OSU_CLIENT_ID")
    if not OSU_CLIENT_SECRET and OSU_CLIENT_ID:
        logger.error("Missing osu! client credentials in environment variables.")
        raise EnvironmentError("Missing osu! client credentials.")

    yield


@app.get("/")
async def root():
    return {"message": "Hello World"}
