import json
import time
from time import localtime, strftime

import requests
from bs4 import BeautifulSoup as bs
from dotenv import dotenv_values
from ossapi import Cursor, Ossapi

from db import crud
from db.orm import Session, models

config = dotenv_values(".env")
client_id = config.get("osu_client_id")
client_secret = config.get("osu_client_secret")

if not client_id or not client_secret:
    raise ValueError("osu! API credentials not found in .env file")


def get_user_ids_from_country_leaderboard(country: str):
    """
    Gets all user ids from osu! country leaderboards
    Saves them in db.
    """
    print(f'{strftime("%H:%M:%S", localtime(time.time()))}: Getting user ids from {country=} leaderboard')
    api = Ossapi(client_id, client_secret)
    lb_cursor = Cursor(page=1)
    while lb_cursor is not None:
        print(f'{strftime("%H:%M:%S", localtime(time.time()))}: Starting {lb_cursor.page=}')
        lb = api.ranking(mode='osu', type='performance', country=country, cursor=lb_cursor)
        lb_cursor = lb.cursor
        for user_stats in lb.ranking:
            user = models.User(id=user_stats.user.id)
            with Session() as session:
                crud.create_or_ignore(session, user)


def get_user_ids():
    """
    Gets all user ids from osu! leaderboards
    Saves them in db.
    """
    page_html = requests.get("https://osu.ppy.sh/rankings/osu/performance", timeout=3).text
    soup = bs(page_html, "html.parser")
    script = soup.find("script", {"id": "json-country-filter"})
    json_text = script.get_text()
    data = json.loads(json_text)
    country_codes = [country["id"] for country in data["items"]]

    for country_code in country_codes:
        get_user_ids_from_country_leaderboard(country_code)
