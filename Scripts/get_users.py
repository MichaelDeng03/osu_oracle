import httpx
from models import ScoreSQLModel, UserSQLModel
from osu_auth import get_auth_token
from sqlmodel import Session

# from Scripts.db_init import get_engine


def get_user(id: int, httpx_client: httpx.Client) -> UserSQLModel | None:
    """
    Attempts to fetch a user from osu api and reduce it to UserSQLModel.
    If the user does not exist, returns None.
    """
    endpoint = f"https://osu.ppy.sh/api/v2/users/{id}/osu"
    params = {"key": "id"}
    headers = {"Authorization": "Bearer " + get_auth_token().access_token}
    response: httpx.Response = httpx_client.get(
        endpoint, params=params, headers=headers
    )

    response_json = response.json()
    user: UserSQLModel = UserSQLModel(
        id=response_json.get("id"),
        avatar_url=response_json.get("avatar_url"),
        country_code=response_json.get("country_code"),
        username=response_json.get("username"),
    )

    return user


async def get_users(
    ids: list[int], httpx_client: httpx.AsyncClient
) -> list[UserSQLModel]:
    """
    Attempts to fetch multiple users from osu api and reduce them to UserSQLModel.
    Users that do not exist are skipped, therefore len(ids) >= len(returned list).
    Returns a list of users.
    """
    endpoint = "https://osu.ppy.sh/api/v2/users"
    params = {"ids[]": ids}
    headers = {"Authorization": "Bearer " + get_auth_token().access_token}
    users: list[UserSQLModel] = []
    response = await httpx_client.get(endpoint, params=params, headers=headers)
    response_json = response.json()
    if not response_json.get("users"):
        return []
    for user_json in response_json.get("users"):
        user: UserSQLModel = UserSQLModel(
            id=user_json.get("id"),
            avatar_url=user_json.get("avatar_url"),
            country_code=user_json.get("country_code"),
            username=user_json.get("username"),
        )
        users.append(user)

    return users


async def get_users_sem(sem, httpx_client, ids: list[int]) -> list[UserSQLModel]:
    async with sem:
        return await get_users(ids, httpx_client)


async def get_user_scores(
    id: int,
    httpx_client: httpx.AsyncClient,
    type: str = "best",
    mode: str = "osu",
    limit: int = 100,
    offset: int = 0,
) -> list[ScoreSQLModel]:
    """
    Fetches the top scores of a user from osu api.
    Returns a list of scores.
    """
    if limit + offset > 200:
        raise ValueError("Limit + offset cannot be greater than 200.")

    endpoint = f"https://osu.ppy.sh/api/v2/users/{id}/scores/{type}"
    headers = {"Authorization": "Bearer " + get_auth_token().access_token}
    scores: list[ScoreSQLModel] = []

    attempted = 0
    while attempted < limit:
        query_params = {
            "mode": mode,
            "limit": limit,
            "offset": offset + attempted,
        }
        response = await httpx_client.get(
            endpoint, headers=headers, params=query_params
        )
        response_json = response.json()

        if not response_json:
            return scores

        for score_json in response_json:
            statistics = score_json.get("statistics")
            beatmap = score_json.get("beatmap")
            score: ScoreSQLModel = ScoreSQLModel(
                id=score_json.get("id"),
                accuracy=score_json.get("accuracy"),
                created_at=score_json.get("created_at"),
                max_combo=score_json.get("max_combo"),
                mode=score_json.get("mode"),
                mods=" ".join(score_json.get("mods")),
                passed=score_json.get("passed"),
                pp=score_json.get("pp"),
                score=score_json.get("score"),
                count_100=statistics.get("count_100"),
                count_300=statistics.get("count_300"),
                count_50=statistics.get("count_50"),
                count_miss=statistics.get("count_miss"),
                user_id=score_json.get("user_id"),
                beatmap_id=beatmap.get("id"),
                beatmapset_id=beatmap.get("beatmapset_id"),
            )
            scores.append(score)

        if len(response_json) < 100:  # 100 is max page size.
            break

        attempted += 100

    return scores


if __name__ == "__main__":
    pass
