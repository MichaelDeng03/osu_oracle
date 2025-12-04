import logging
import sys
from contextlib import asynccontextmanager
from os import getenv

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"
)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
file_handler = logging.FileHandler("info.log")
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

logger.info("API is starting up")


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    logger.info("Loading environment variables from .env file.")
    OSU_CLIENT_SECRET = getenv("OSU_CLIENT_SECRET")
    OSU_CLIENT_ID = getenv("OSU_CLIENT_ID")
    if not OSU_CLIENT_SECRET and OSU_CLIENT_ID:
        logger.error("Missing osu! client credentials in environment variables.")
        raise EnvironmentError("Missing osu! client credentials.")
    logger.info("Environment variables loaded successfully.")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def main():
    logger.info("GET /")
    return "ok"


if __name__ == "__main__":
    uvicorn.run(app, log_level="trace")
