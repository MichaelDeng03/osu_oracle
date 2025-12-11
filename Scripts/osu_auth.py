import os
from datetime import datetime, timedelta

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel


class AuthTokenResponseModel(BaseModel):
    access_token: str
    expires_at: datetime


# TODO: token caching
def get_auth_token() -> AuthTokenResponseModel:
    """
    from pydantic import Field, SecretStr
        Goes through client credentials flow to get a dev auth token from osu api.
    """
    load_dotenv()
    client_id: str = os.getenv("OSU_CLIENT_ID")  # TODO: Unify models
    client_secret: str = os.getenv("OSU_CLIENT_SECRET")
    endpoint = "https://osu.ppy.sh/oauth/token"

    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "public",
    }

    response = httpx.post(endpoint, json=params)
    response_json: dict = response.json()

    expires_in: int = response_json.get("expires_in")
    access_token: str = response_json.get("access_token")

    return AuthTokenResponseModel(
        access_token=access_token,
        expires_at=datetime.now()
        + timedelta(seconds=expires_in)
        - timedelta(seconds=300),
    )
