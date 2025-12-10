from sqlmodel import SQLModel, Field

# Refer to https://osu.ppy.sh/docs/#userextended
# Simplified version of UserExtended model.
class UserSQLModel(SQLModel, table=True):
    id: int = Field(primary_key=True, description="Unique identifier for the user")
    avatar_url: str = Field(..., description="URL to the user's avatar image")
    country_code: str = Field(..., description="ISO 3166-1 alpha-2 country code of the user")
    username: str = Field(..., description="The user's username")
