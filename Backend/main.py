import logging
import sys
from contextlib import asynccontextmanager
from os import getenv

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

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
    OSU_API_ENDPOINT = "https://osu.ppy.sh/api/v2"
    if not OSU_CLIENT_ID or not OSU_CLIENT_SECRET:
        logger.error("Missing osu! client credentials in environment variables.")
        raise EnvironmentError("Missing osu! client credentials.")
    logger.info("Environment variables loaded successfully.")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def main():
    logger.info("GET /")
    return "ok"


@app.get("/oauth2")
async def oauth2():
    # Base authorization endpoint
    endpoint = "https://osu.ppy.sh/oauth/authorize"

    # Parameters for the authorization URL
    redirect_uri = (
        "http://localhost:8000/oauth2/callback"  # TODO: Change to actual redirect URI
    )
    response_type = "code"
    scope = "public"
    state = "foobar"  # TODO: CSRF protection
    client_id = getenv("OSU_CLIENT_ID")

    auth_url = (
        f"{endpoint}"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type={response_type}"
        f"&scope={scope}"
        f"&state={state}"
    )

    return RedirectResponse(url=auth_url)


@app.get("/oauth2/callback")
async def oauth2_callback(code: str, state: str):
    token_endpoint = "https://osu.ppy.sh/oauth/token"
    redirect_uri = (
        "http://localhost:8000/oauth2/callback"  # TODO: Change to actual redirect URI
    )
    client_id = getenv("OSU_CLIENT_ID")
    client_secret = getenv("OSU_CLIENT_SECRET")

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_endpoint, data=data)
        response.raise_for_status()
        token_data = response.json()

    access_token = token_data.get("access_token")
    return {"access_token": access_token}


if __name__ == "__main__":
    uvicorn.run(app, log_level="trace")
