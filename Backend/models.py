from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OSU_CLIENT_ID: str = Field(..., env="OSU_CLIENT_ID")
    OSU_CLIENT_SECRET: SecretStr = Field(..., env="OSU_CLIENT_SECRET")
    REDIRECT_URI: str = Field(
        "http://localhost:8000/oauth2/callback", env="REDIRECT_URI"
    )
