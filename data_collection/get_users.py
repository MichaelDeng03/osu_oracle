import json
import time
from time import localtime, strftime

import requests
from bs4 import BeautifulSoup as bs
from ossapi import Cursor

from db import crud
from db.orm import Session, models

from .client import ossapi_client


def get_user_ids_from_country_leaderboard(country: str):
    """
    Gets all user ids & usernames from osu! country leaderboards
    Saves them in db.
    """
    # api = Ossapi(client_id, client_secret)
    lb_cursor = Cursor(page=1)
    while lb_cursor is not None:
        print(
            f"{strftime('%H:%M:%S', localtime(time.time()))}: Starting {lb_cursor.page=}"
        )
        lb = ossapi_client.ranking(
            mode="osu", type="performance", country=country, cursor=lb_cursor
        )
        lb_cursor = lb.cursor
        for user_stats in lb.ranking:
            user = models.User(id=user_stats.user.id, username=user_stats.user.username)
            with Session() as session:
                crud.create_or_ignore(session, user)


def get_users():
    """
    Gets all user ids & usernames from osu! leaderboards
    Saves them in db.
    """
    page_html = requests.get(
        "https://osu.ppy.sh/rankings/osu/performance", timeout=3
    ).text
    soup = bs(page_html, "html.parser")
    script = soup.find("script", {"id": "json-country-filter"})
    json_text = script.get_text()
    data = json.loads(json_text)
    country_codes = [country["id"] for country in data["items"]]

    for i, country_code in enumerate(country_codes):
        print(
            f"{i}/{len(country_codes)} {strftime('%H:%M:%S', localtime(time.time()))}:",
            f"Getting user ids from {country_code=} leaderboard",
        )
        get_user_ids_from_country_leaderboard(country_code)


def get_user(user_id: int):
    """
    Gets a user
    """
    user = ossapi_client.user(user_id)
    user_data = {
        "id": user.id,
        "username": user.username,
    }

    with Session() as session:
        user = models.User(**user_data)
        crud.create_or_ignore(session, user)


if __name__ == "__main__":
    get_users()
