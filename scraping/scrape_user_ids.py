from ossapi import Ossapi
from ossapi import Cursor
import sqlite3
import requests
from bs4 import BeautifulSoup as bs
import json
from time import strftime, localtime
import time
import sys

sys.path.insert(
    0, "../" # I run this script from scraping sometimes so I need to add the parent directory to the path
)  # To import osu_access_token and classes from parent directory
from osu_access_token import client_id, client_secret

api = Ossapi(client_id, client_secret)


# Get all country codes
page_html = requests.get("https://osu.ppy.sh/rankings/osu/performance").text
soup = bs(page_html, "html.parser")
script = soup.find("script", {"id": "json-country-filter"})
json_text = script.get_text()
data = json.loads(json_text)
country_codes = [country["id"] for country in data["items"]]


def get_user_ids_from_lb(country_code):
    """
    Gets user ids from that countries leaderboards
    country_code: alpha_2 ISO3166 code
    """
    try:
        formatted_time = strftime("%H:%M:%S", localtime(time.time()))
        print(f"Getting user ids from {country_code}. Time: {formatted_time}", end="")
        ids = []
        lb_cursor = Cursor(
            page=1
        )  # page cursor for lb. api call returns next page cursor. no next page = none
        while lb_cursor is not None:
            lb = api.ranking(
                mode="osu", type="performance", cursor=lb_cursor, country=country_code
            )
            lb_cursor = lb.cursor
            for user_stats in lb.ranking:
                if (
                    user_stats.pp < 500
                ):  # Stop when we get to users with less than 500pp
                    break
                ids.append(user_stats.user.id)

    except Exception as e:
        print("\nError getting user ids from lb")
        print(e)

    finally:
        formatted_time = strftime("%H:%M:%S", localtime(time.time()))
        print(f"\nDone with {country_code}. Time: {formatted_time}")
        return ids


def insert_ids(ids, conn):
    """
    Inserts user ids into database if not already in database.
    ids: Iterable of user_ids to insert
    conn: SQLite3 connection object
    """
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    existing_ids = {row[0] for row in cursor.fetchall()}
    new_ids = [(user_id,) for user_id in ids if user_id not in existing_ids]

    if new_ids:
        cursor.executemany("INSERT OR IGNORE INTO users (user_id) VALUES (?)", new_ids)
        conn.commit()
        print(f"Inserted {len(new_ids)} new ids")
    else:
        print("No new ids to insert")


conn = sqlite3.connect("../data/osu.db") 
for country_code in country_codes:
    ids = get_user_ids_from_lb(country_code)
    insert_ids(ids, conn)