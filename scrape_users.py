import sqlite3
from ossapi import Ossapi
from time import strftime, localtime

from concurrent.futures import ThreadPoolExecutor
from osu_access_token import client_id, client_secret
from numpy import array_split
from classes import User, Score
num_done = 0


def create_tables():
    """
    Makes tables required for this script if they don't already exist.
    Table specifications found here. https://dbdiagram.io/d/osu-654e8e887d8bbd6465f40357
    """
    conn = sqlite3.connect("data/osu.db")
    cursor = conn.cursor()

    # user table
    query = """
    CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    total_pp INTEGER,
    hit_acc REAL,
    ranked_score INTEGER,
    play_count INTEGER,
    playtime INTEGER,
    count_50 INTEGER,
    count_100 INTEGER,
    count_300 INTEGER,
    count_miss INTEGER,
    total_hits INTEGER,
    country TEXT,
    join_date TEXT,
    update_date TEXT
    );
    """
    cursor.execute(query)

    # score table
    query = """
    CREATE TABLE IF NOT EXISTS score (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    beatmap_id INTEGER,
    beatmapset_id INTEGER,
    mods INTEGER,
    score INTEGER,
    max_combo INTEGER,
    perfect BOOLEAN,
    count_50 INTEGER,
    count_100 INTEGER,
    count_300 INTEGER,
    count_geki INTEGER,
    count_katu INTEGER,
    count_miss INTEGER,
    pp REAL,
    rank TEXT,
    created_at TEXT,
    mode INTEGER,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (beatmap_id) REFERENCES beatmap(id),
    FOREIGN KEY (beatmapset_id) REFERENCES beatmapset(id)
    );
    """
    cursor.execute(query)

    # beatmap table
    query = """
    CREATE TABLE IF NOT EXISTS beatmap (
    id INTEGER PRIMARY KEY,
    beatmapset_id INTEGER,
    difficulty_rating REAL,
    bpm REAL,
    count_circles INTEGER,
    count_sliders INTEGER,
    count_spinners INTEGER,
    cs REAL,
    drain REAL,
    accuracy REAL,
    ar REAL,
    max_combo INTEGER,
    length_seconds INTEGER,
    author_id INTEGER,
    mode_int INTEGER,
    FOREIGN KEY (beatmapset_id) REFERENCES beatmapset(id),
    FOREIGN KEY (author_id) REFERENCES user(id)
    );
    """
    cursor.execute(query)

    # beatmapset table
    query = """
    CREATE TABLE IF NOT EXISTS beatmapset (
    id INTEGER PRIMARY KEY,
    language TEXT,
    nsfw BOOLEAN,
    play_count INTEGER,
    ranked_date TEXT,
    tags TEXT,
    title TEXT,
    artist TEXT,
    author_id INTEGER,
    FOREIGN KEY (author_id) REFERENCES user(id)
    );
    """
    cursor.execute(query)
    conn.commit()
    conn.close()


def main():
    """
    This script is used to scrape user data.
    It collects user data based on user_ids in lb_user of osu.db.
    Collected attributes are in classes.py
    Two api calls per user are required, one for user data, and one for user top scores.
    """
    create_tables()

    conn = sqlite3.connect("data/osu.db")
    cursor = conn.cursor()

    api = Ossapi(client_id, client_secret)

    user_ids = cursor.execute("SELECT id FROM lb_user")
    user_ids = set([user_id[0] for user_id in user_ids])
    completed_ids = cursor.execute("SELECT id FROM user")
    completed_ids = set([user_id[0] for user_id in completed_ids])
    partitioned_user_ids = list(user_ids - completed_ids)
    num_partitions = 5
    partitioned_user_ids = array_split(partitioned_user_ids, num_partitions)
        
    conn.close()
    global num_done
    num_done += len(completed_ids)

    def scrape_ids(ids):
        """
        Adds user and score data to osu.db after scraping from osuapi.
        ids: list of ids to process
        """
        global num_done

        conn = sqlite3.connect("data/osu.db")
        cursor = conn.cursor()

        for id in ids:
            try:
                user = User(api.user(id, mode="osu", key="id"))
                top_scores = api.user_scores(id, type="best", mode="osu", limit=100)
                top_scores = [Score(score) for score in top_scores]

                user.insert(cursor)
                for score in top_scores:
                    score.insert(cursor)
            except Exception as e:
                print(f"Error scraping user {id}")
                print(e)
                # Remove user from lb_user so we don't try again
                cursor.execute("DELETE FROM lb_user WHERE id = ?", (id,))
            finally:
                num_done += 1
                if num_done % 100 == 0:
                    print(
                        f"Done with {num_done}/{len(user_ids)} ids at {strftime('%H:%M:%S', localtime())}"
                    )
                conn.commit()

        conn.close()

    with ThreadPoolExecutor(max_workers=num_partitions) as executor:
        for ids in partitioned_user_ids:
            executor.submit(scrape_ids, ids)

    conn.close()


if __name__ == "__main__":
    main()
