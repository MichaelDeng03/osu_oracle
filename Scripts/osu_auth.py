import os
from datetime import datetime, timedelta

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel


class AuthTokenResponseModel(BaseModel):
    access_token: str
    expires_at: datetime


_CACHED_TOKEN: AuthTokenResponseModel | None = None


def get_auth_token() -> AuthTokenResponseModel:
    """
    Goes through client credentials flow to get a dev auth token from osu api,
    caching the result until expiration.
    """
    global _CACHED_TOKEN

    if _CACHED_TOKEN and _CACHED_TOKEN.expires_at > datetime.now():
        return _CACHED_TOKEN

    load_dotenv()

    client_id: str | None = os.getenv("OSU_CLIENT_ID")
    client_secret: str | None = os.getenv("OSU_CLIENT_SECRET")
    endpoint = "https://osu.ppy.sh/oauth/token"

    if not client_id or not client_secret:
        raise ValueError(
            "Missing 'OSU_CLIENT_ID' or 'OSU_CLIENT_SECRET' environment variables."
        )

    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "public",
    }

    try:
        response = httpx.post(endpoint, json=params)
        response.raise_for_status()
        response_json: dict = response.json()
    except httpx.HTTPStatusError:
        # TODO: logger
        raise
    except httpx.RequestError:
        # TODO: logger
        raise

    expires_in: int = response_json.get("expires_in")
    access_token: str = response_json.get("access_token")

    # calculate absolute expiration time w/ 5min buffer buffer
    new_expires_at = (
        datetime.now() + timedelta(seconds=expires_in) - timedelta(seconds=300)
    )

    _CACHED_TOKEN = AuthTokenResponseModel(
        access_token=access_token,
        expires_at=new_expires_at,
    )

    return _CACHED_TOKEN
