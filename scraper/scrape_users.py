from ossapi import Ossapi
import sqlite3
from time import strftime, localtime
import time
from concurrent.futures import ThreadPoolExecutor
import sys
from numpy import array_split

sys.path.insert(0, "../") # I run this script from scraping sometimes so I need to add the parent directory to the path
from data.classes import User, Score
from osu_access_token import client_id, client_secret

api = Ossapi(client_id, client_secret)

conn = sqlite3.connect("../data/osu.db")
cursor = conn.cursor()
user_ids = cursor.execute("SELECT user_id FROM users").fetchall()
user_ids = [user_id[0] for user_id in user_ids]

completed_ids = cursor.execute(
    "SELECT user_id FROM users WHERE username IS NOT NULL"
).fetchall()
completed_ids = [user_id[0] for user_id in completed_ids]

user_ids = list(set(user_ids) - set(completed_ids))
num_partitions = 5
partitioned_user_ids = array_split(user_ids, num_partitions)

# Outside so threads can access
num_done = 0
last_time = time.time()


def scrape_users(ids):
    """
    Adds user data to users table and scores to scores in ../data/osu.db after scraping.
    ids: list of ids to scrape
    """
    global num_done
    global last_time
    conn = sqlite3.connect("../data/osu.db")  # Change to osu.db in the future
    cursor = conn.cursor()

    for user_id in ids:
        try:
            user = User(api.user(user_id, mode="osu", key="id"))
            top_scores = api.user_scores(user_id, type="best", mode="osu", limit=100)
            scores = []

            for score in top_scores:
                try:
                    score = Score(score)
                    scores.append(score)
                except Exception as e:
                    print(e)
                    print(f"Error creating score object: {e}")
                    continue

            try:
                user.insert(cursor)
            except Exception as e:
                print(e)
                print(f"Error inserting user {user} into db")
                continue

            for score in scores:
                try:
                    score.insert(cursor)
                except Exception as e:
                    print(e)
                    print(f"Error inserting score {score} into db")
                    continue

        except Exception as e:
            print(e)
            continue
        finally:
            conn.commit()

        num_done += 1
        if num_done % 100 == 0:
            print(
                str(num_done) + ": " + str(time.time() - last_time),
                strftime("%H:%M:%S", localtime(time.time())),
            )
            last_time = time.time()

    conn.close()


for user_ids in partitioned_user_ids:
    print(len(user_ids))

with ThreadPoolExecutor(max_workers=num_partitions) as executor:
    for user_ids in partitioned_user_ids:
        executor.submit(scrape_users, user_ids)