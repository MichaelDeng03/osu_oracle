import httpx
from db import get_engine
from models import UserSQLModel
from osu_auth import get_auth_token
from sqlmodel import Session


def get_user(id: int) -> UserSQLModel | None:
    """
    Attempts to fetch a user from osu api and reduce it to UserSQLModel.
    If the user does not exist, returns None.
    """
    endpoint = f"https://osu.ppy.sh/api/v2/users/{id}/osu"
    params = {"key": "id"}
    headers = {"Authorization": "Bearer " + get_auth_token().access_token}
    response = httpx.get(endpoint, params=params, headers=headers)

    response_json = response.json()
    user: UserSQLModel = UserSQLModel(
        id=response_json.get("id"),
        avatar_url=response_json.get("avatar_url"),
        country_code=response_json.get("country_code"),
        username=response_json.get("username"),
    )

    return user


def get_users(ids: list[int]) -> list[UserSQLModel]:
    """
    Attempts to fetch multiple users from osu api and reduce them to UserSQLModel.
    Users that do not exist are skipped, therefore len(ids) >= len(returned list).
    Returns a list of users.
    """
    endpoint = "https://osu.ppy.sh/api/v2/users"
    params = {"ids[]": ids}
    headers = {"Authorization": "Bearer " + get_auth_token().access_token}
    response = httpx.get(endpoint, params=params, headers=headers)
    response_json = response.json()
    users: list[UserSQLModel] = []
    for user_json in response_json.get("users"):
        user: UserSQLModel = UserSQLModel(
            id=user_json.get("id"),
            avatar_url=user_json.get("avatar_url"),
            country_code=user_json.get("country_code"),
            username=user_json.get("username"),
        )
        users.append(user)

    return users


def save_users(users: list[UserSQLModel]) -> None:
    """
    Saves a list of UserSQLModel to the database.
    """
    engine = get_engine()
    with Session(engine) as session:
        for user in users:
            session.add(user)
        session.commit()


if __name__ == "__main__":
    users = get_users([28956125, 289561251])
    save_users(users)
