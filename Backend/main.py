import logging
import sys
from contextlib import asynccontextmanager
from os import getenv

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from models import Settings
from pydantic import ValidationError

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    logger.info("Loading environment variables from .env file.")
    try:
        settings = Settings()
        app.state.settings = settings
        logger.info(
            "Environment variables loaded successfully using Pydantic Settings."
        )
    except ValidationError as e:
        logger.error(f"Environment variable validation error: {e}")
        raise e

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def main():
    return "ok"


@app.get("/oauth2")
async def oauth2():
    settings: Settings = app.state.settings
    auth_endpoint: str = "https://osu.ppy.sh/oauth/authorize"

    redirect_uri: str = settings.REDIRECT_URI
    response_type = "code"
    scope = "public"
    state = "foobar"  # TODO: CSRF protection
    client_id = getenv("OSU_CLIENT_ID")

    auth_url = (
        f"{auth_endpoint}"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type={response_type}"
        f"&scope={scope}"
        f"&state={state}"
    )

    return RedirectResponse(url=auth_url)


@app.get("/oauth2/callback")
async def oauth2_callback(code: str, state: str):
    settings: Settings = app.state.settings
    token_endpoint = "https://osu.ppy.sh/oauth/token"

    data = {
        "client_id": settings.OSU_CLIENT_ID,
        "client_secret": settings.OSU_CLIENT_SECRET.get_secret_value(),
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_endpoint, data=data)
        response.raise_for_status()
        token_data = response.json()

    access_token = token_data.get("access_token")
    return {"access_token": access_token}


if __name__ == "__main__":
    uvicorn.run(app, log_level="trace")
