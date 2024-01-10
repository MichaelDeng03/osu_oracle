from ossapi import Ossapi
import sqlite3
from time import strftime, localtime
import time
from concurrent.futures import ThreadPoolExecutor
import sys
from numpy import array_split
from threading import Lock

sys.path.insert(0, "../")
from data.classes import Beatmap, Beatmapset
from osu_access_token import client_id, client_secret

api = Ossapi(client_id, client_secret)

num_beatmap_done = 0
num_beatmapset_done = 0

conn = sqlite3.connect("../data/osu.db")
cursor = conn.cursor()

api = Ossapi(client_id, client_secret)

beatmap_ids = cursor.execute("SELECT DISTINCT beatmap_id FROM scores").fetchall()
beatmap_ids = set([beatmap_id[0] for beatmap_id in beatmap_ids])

completed_beatmap_ids = cursor.execute("SELECT beatmap_id FROM beatmaps").fetchall()
completed_beatmap_ids = set([beatmap_id[0] for beatmap_id in completed_beatmap_ids])
conn.close()

beatmap_ids = list(beatmap_ids - completed_beatmap_ids)

num_partitions = 5
partitioned_beatmap_ids = array_split(beatmap_ids, num_partitions)

num_beatmap_done = len(completed_beatmap_ids)
lock = Lock()


def scrape_beatmaps(ids):
    global num_beatmap_done

    conn = sqlite3.connect("../data/osu.db")
    cursor = conn.cursor()

    for id in ids:
        try:
            beatmap = Beatmap(api.beatmap(id))
            lock.acquire()
            beatmap.insert(cursor)
            lock.release()

        except Exception as e:
            print(f"Error scraping beatmap {id}: {e}")
            continue
        finally:
            num_beatmap_done += 1
            time.sleep(0.06)
            if num_beatmap_done % 100 == 0:
                print(
                    f"Beatmaps done: {num_beatmap_done}/{len(beatmap_ids) + len(completed_beatmap_ids)} @ {strftime('%H:%M:%S', localtime(time.time()))}"
                )
            conn.commit()

    conn.close()


conn = sqlite3.connect("../data/osu.db")
cursor = conn.cursor()
beatmapset_ids = cursor.execute(
    "SELECT DISTINCT beatmapset_id FROM beatmaps"
).fetchall()
beatmapset_ids = set([beatmapset_id[0] for beatmapset_id in beatmapset_ids])

completed_beatmapset_ids = cursor.execute(
    "SELECT beatmapset_id FROM beatmapsets"
).fetchall()
completed_beatmapset_ids = set([beatmapset_id[0] for beatmapset_id in completed_beatmapset_ids])

beatmapset_ids = list(beatmapset_ids - completed_beatmapset_ids)
partitioned_beatmapset_ids = array_split(beatmapset_ids, num_partitions)

num_beatmapset_done = len(completed_beatmapset_ids)
conn.close()

def scrape_beatmapsets(ids):
    """
    Adds beatmapset data to osu.db after scraping
    """
    global num_beatmapset_done

    conn = sqlite3.connect("../data/osu.db")
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
            time.sleep(0.06)
            if num_beatmapset_done % 100 == 0:
                print(f"Beatmapsets done: {num_beatmapset_done}/{len(beatmapset_ids) + len(completed_beatmapset_ids)} @ {strftime('%H:%M:%S', localtime(time.time()))}")
            conn.commit()


with ThreadPoolExecutor(max_workers=num_partitions) as executor:
    for ids in partitioned_beatmap_ids:
        executor.submit(scrape_beatmaps, ids)

with ThreadPoolExecutor(max_workers=num_partitions) as executor:
    for ids in partitioned_beatmapset_ids:
        executor.submit(scrape_beatmapsets, ids)
