import json
import os
import pickle
import time
from time import localtime, strftime

import requests
from bs4 import BeautifulSoup as bs
from ossapi import Cursor, Ossapi

CLIENT_ID = os.environ.get("OSU_CLIENT_ID")
CLIENT_SECRET = os.environ.get("OSU_CLIENT_SECRET")

ossapi = Ossapi(CLIENT_ID, CLIENT_SECRET)

# Get all country codes
page_html = requests.get("https://osu.ppy.sh/rankings/osu/performance").text
soup = bs(page_html, "html.parser")
script = soup.find("script", {"id": "json-country-filter"})
json_text = script.get_text()
data = json.loads(json_text)
country_codes = [country["id"] for country in data["items"]]

all_ids = set()

for country_code in country_codes:
    try:
        print(
            f"Getting user ids from {country_code}. Time: {strftime('%H:%M:%S', localtime(time.time()))}"
        )
        lb_cursor = Cursor(page=1)
        while lb_cursor is not None:
            lb = ossapi.ranking(
                mode="osu", type="performance", cursor=lb_cursor, country=country_code
            )
            lb_cursor = lb.cursor
            for user_stats in lb.ranking:
                if user_stats.pp < 500:
                    break
                all_ids.add(user_stats.user.id)
    except Exception as e:
        print(e)


with open("pickle.leaderboard_ids", "wb") as handle:
    pickle.dump(all_ids, handle, protocol=pickle.HIGHEST_PROTOCOL)
