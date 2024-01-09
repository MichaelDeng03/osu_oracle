import sqlite3
from ossapi import Ossapi
from time import strftime, localtime
from classes import Beatmap, Beatmapset
from concurrent.futures import ThreadPoolExecutor
from osu_access_token import client_id, client_secret
from numpy import array_split
import time
from scrape_users import create_tables

num_beatmap_done = 0
num_beatmapset_done = 0


def main():
    """
    This script is used to scrape beatmap and beatmap data.
    Should be run after scrape_users.py is complete.
    """

    conn = sqlite3.connect("data/osu.db")
    cursor = conn.cursor()

    api = Ossapi(client_id, client_secret)

    # beatmap_ids = cursor.execute("SELECT DISTINCT beatmap_id FROM score").fetchall()
    # beatmap_ids = set([beatmap_id[0] for beatmap_id in beatmap_ids])
    beatmapset_ids = cursor.execute(
        "SELECT DISTINCT beatmapset_id FROM score"
    ).fetchall()
    beatmapset_ids = set([beatmapset_id[0] for beatmapset_id in beatmapset_ids])
    # completed_beatmap_ids = cursor.execute("SELECT id FROM beatmap").fetchall()
    # completed_beatmap_ids = set([beatmap_id[0] for beatmap_id in completed_beatmap_ids])
    completed_beatmapset_ids = cursor.execute("SELECT id FROM beatmapset").fetchall()
    completed_beatmapset_ids = set(
        [beatmapset_id[0] for beatmapset_id in completed_beatmapset_ids]
    )

    # beatmap_ids = [
    #     beatmap_id
    #     for beatmap_id in beatmap_ids
    #     if beatmap_id not in completed_beatmap_ids
    # ]
    beatmapset_ids = [
        beatmapset_id
        for beatmapset_id in beatmapset_ids
        if beatmapset_id not in completed_beatmapset_ids
    ]

    num_partitions = 5
    # partitioned_beatmap_ids = array_split(beatmap_ids, num_partitions)
    partitioned_beatmapset_ids = array_split(beatmapset_ids, num_partitions)

    conn.close()

    # global num_beatmap_done
    global num_beatmapset_done
    # num_beatmap_done += len(completed_beatmap_ids)
    num_beatmapset_done += len(completed_beatmapset_ids)

    def scrape_beatmaps(ids):
        """
        Adds beatmap data to osu.db after scraping
        """
        global num_beatmap_done

        conn = sqlite3.connect("data/osu.db")
        cursor = conn.cursor()

        for id in ids:
            try:
                beatmap = Beatmap(api.beatmap(id))
                beatmap.insert(cursor)
            except Exception as e:
                print(f"Error scraping beatmap {id}: {e}")
                continue
            finally:
                num_beatmap_done += 1
                time.sleep(0.1)
                if num_beatmap_done % 100 == 0:
                    print(f"Beatmaps done: {num_beatmap_done}/{len(beatmap_ids)}")
                conn.commit()

        conn.close()

    def scrape_beatmapsets(ids):
        """
        Adds beatmapset data to osu.db after scraping
        """
        global num_beatmapset_done

        conn = sqlite3.connect("data/osu.db")
        cursor = conn.cursor()

        for id in ids:
            try:
                beatmapset = Beatmapset(api.beatmapset(id))
                beatmapset.insert(cursor)
            except Exception as e:
                print(f"Error scraping beatmapset {id}: {e}")
                continue
            finally:
                num_beatmapset_done += 1
                time.sleep(0.1)
                if num_beatmapset_done % 100 == 0:
                    print(
                        f"Beatmapsets done: {num_beatmapset_done}/{len(beatmapset_ids)}"
                    )
                conn.commit()

    # with ThreadPoolExecutor(max_workers=num_partitions) as executor:
    #     for ids in partitioned_beatmap_ids:
    #         executor.submit(scrape_beatmaps, ids)

    with ThreadPoolExecutor(max_workers=num_partitions) as executor:
        for ids in partitioned_beatmapset_ids:
            executor.submit(scrape_beatmapsets, ids)


if __name__ == "__main__":
    main()
