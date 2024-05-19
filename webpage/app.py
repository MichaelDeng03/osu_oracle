import sqlite3
import sys
import threading
from datetime import datetime
from time import gmtime, strftime

import gensim
import numpy as np
from flask import Flask, jsonify, render_template, request
from ossapi import Ossapi

# from pyclustering.cluster.xmeans import xmeans
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors

sys.path.insert(0, "../")
import os

from data.classes import Beatmap, Beatmapset, Score, User

OSU_CLIENT_ID = os.environ.get("OSU_CLIENT_ID")
OSU_CLIENT_SECRET = os.environ.get("OSU_CLIENT_SECRET")

app = Flask(__name__)
api = Ossapi(OSU_CLIENT_ID, OSU_CLIENT_SECRET)
conn = sqlite3.connect(
    "../data/UserScores.db", check_same_thread=False
)  # DANGER DANGER: need to lock acquire manually
lock = threading.Lock()

word2vec_model_std = gensim.models.Word2Vec.load("../Models/word2vec_1.model")
NN_std = NearestNeighbors(n_neighbors=200, algorithm="ball_tree").fit(
    word2vec_model_std.wv.vectors
)

# word2vec_model_noHD = gensim.models.Word2Vec.load(
#     "../Models/w2v_model_noHD_15d_50e/w2v_model_noHD_15d_50e"
# )
# NN_noHD = NearestNeighbors(n_neighbors=200, algorithm="ball_tree").fit(
#     word2vec_model_noHD.wv.vectors
# )


mod_enums_list = [
    "None",  # 0
    "NoFail",  # 1
    "Easy",  # 2
    "Touch Device",  # 4
    "Hidden",
    "Hard Rock",
    "Sudden Death",
    "Double Time",
    "Relax",
    "Half Time",
    "Nightcore",
    "Flashlight",
    "Autoplay",
    "Spun Out",
    "Relax2",
    "Perfect",
    "Key4",
    "Key5",
    "Key6",
    "Key7",
    "Key8",
    "FadeIn",
    "Random",
    "Cinema",
    "Target",
    "Key9",
    "KeyCoop",
    "Key1",
    "Key3",
    "Key2",
    "ScoreV2",
    "Mirror",
]
mod_enums = {mod: 2 ** (i - 1) for i, mod in enumerate(mod_enums_list)}

NF = 1
HD = 8  # Removed only for no HD
SD = 32
NC = 512
SO = 4096
PF = 16384
SV2 = 536870912
standard_removed_mods = NF | SD | NC | SO | PF | SV2
noHD_removed_mods = NF | SD | NC | SO | PF | SV2 | HD


def mod_enum_to_names(mod_enum):
    mod_enum = bin(mod_enum)[2:] + "0"
    mod_enum = mod_enum[::-1]
    mod_enum = list(mod_enum)
    mods = [mod_enums_list[i] for i in range(len(mod_enum)) if mod_enum[i] == "1"]
    mods = ", ".join(mods)

    return mods


def mod_names_to_enum(mod_names):
    mod_names = mod_names.split(", ")
    if "" in mod_names:
        mod_names.remove("")

    enum = 0
    for mod_name in mod_names:
        enum += mod_enums[mod_name]

    return enum


@app.route("/wip")
def wip():
    return render_template("wip.html")


@app.route("/")
def home():
    return render_template("index.html")


def get_beatmap_attr(beatmap_id, attr):
    """
    attr: list of attributes to get
    returns: dictionary of attributes
    """
    conn = sqlite3.connect("../data/osu.db")
    cursor = conn.cursor()
    try:
        query = f"SELECT {','.join(attr)} FROM beatmaps WHERE beatmap_id = {beatmap_id}"
        attr_res = cursor.execute(query).fetchone()
        attr_res = {attr[i]: attr_res[i] for i in range(len(attr))}
    except Exception as e:
        print(e)
        beatmap = Beatmap(api.beatmap(beatmap_id))
        beatmapset = Beatmapset(api.beatmapset(beatmap.beatmapset_id))

        lock.acquire()
        beatmap.insert(cursor)
        beatmapset.insert(cursor)
        conn.commit()
        lock.release()

        query = f"SELECT {','.join(attr)} FROM beatmaps WHERE beatmap_id = {beatmap_id}"
        attr_res = cursor.execute(query).fetchone()
        attr_res = {attr[i]: attr_res[i] for i in range(len(attr))}
    finally:
        return attr_res


def get_beatmap_title_and_version(beatmap_id):
    """
    Returns (title, version)
    """
    conn = sqlite3.connect("../data/UserScores.db")
    cursor = conn.cursor()
    try:
        query = f"SELECT version, beatmapset_id FROM beatmaps_std WHERE beatmap_id = {beatmap_id}"
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            version, beatmapset_id = result
        else:
            # If not found, fetch from API and insert
            beatmap = api.beatmap(beatmap_id)

            accuracy = getattr(beatmap, "accuracy", None)
            ar = getattr(beatmap, "ar", None)
            beatmap_id = beatmap_id  # no shit
            beatmapset_id = getattr(beatmap, "beatmapset_id", None)
            bpm = getattr(beatmap, "bpm", None)
            cs = getattr(beatmap, "cs", None)
            difficulty_rating = getattr(beatmap, "difficulty_rating", None)
            drain = getattr(beatmap, "drain", None)
            max_combo = getattr(beatmap, "max_combo", None)
            owner_user_id = getattr(beatmap, "owner_user_id", None)
            total_length = getattr(beatmap, "total_length", None)
            url = getattr(beatmap, "url", None)
            version = getattr(beatmap, "version", None)

            beatmap = (
                accuracy,
                ar,
                beatmap_id,
                beatmapset_id,
                bpm,
                cs,
                difficulty_rating,
                drain,
                max_combo,
                owner_user_id,
                total_length,
                url,
                version,
            )

            lock.acquire()
            cursor.execute(
                """
                INSERT INTO beatmaps_std (
                accuracy, ar, beatmap_id, beatmapset_id, bpm, cs, 
                difficulty_rating, drain, max_combo, owner_user_id, 
                total_length, url, version) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                beatmap,
            )
            conn.commit()
            lock.release()

        query = (
            f"SELECT title FROM beatmapsets_std WHERE beatmapset_id = {beatmapset_id}"
        )
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            title = result[0]
        else:
            # If not found, fetch from API and insert
            beatmapset = api.beatmapset(beatmapset_id)

            lock.acquire()
            beatmapset.insert(cursor)
            conn.commit()
            lock.release()

            title = beatmapset.title

    except Exception as e:
        print(f"Error retrieving beatmap/beatmapset information: {e}")
        return None, None

    finally:
        conn.close()
        return title, version


@app.route("/get_user_top_scores/<int:user_id>")
def get_user_top_scores(user_id):
    """
    Gets top 100 scores for user_id, returns a jsonified list of dictionaries for frontend
    """
    try:
        top_scores = api.user_scores(user_id, type="best", mode="osu", limit=100)
        scores = []
    except Exception as e:
        print(e)

    for score in top_scores:
        try:
            beatmap = getattr(score, "beatmap", None)
            beatmap_id = getattr(beatmap, "id", None) if beatmap else None

            beatmapset_id = getattr(beatmap, "beatmapset_id", None) if beatmap else None

            mods = getattr(score, "mods", None)
            mods = getattr(mods, "value", None) if mods else None

            pp = getattr(score, "pp", None)

            created_at = getattr(score, "created_at", None)
            created_at = (
                datetime.strftime(created_at, "%Y-%m-%d %H:%M:%S")
                if created_at
                else None
            )

            title, version = get_beatmap_title_and_version(beatmap_id)

            score = {
                "user_id": user_id,
                "beatmap_id": beatmap_id,
                "beatmapset_id": beatmapset_id,
                "pp": pp,
                "mods": mods,
                "created_at": created_at,
                "link": f"https://osu.ppy.sh/beatmapsets/{beatmapset_id}#osu/{beatmap_id}",
                "title": title,
                "version": version,
            }

            scores.append(score)

        except Exception as e:
            print(e)
            continue

    rows = []
    for score in scores:
        rows.append(
            {
                "score_id": score.score_id,
                "beatmap_id": score.beatmap_id,
                "mods": mod_enum_to_names(score.mods),
                "rank": score.rank,
            }
        )
        rows[-1].update(get_beatmap_title_and_link(score.beatmap_id))

    try:
        for score in scores:
            cursor = conn.cursor()
            score.insert(cursor)
            conn.commit()
    except Exception as e:
        print(e)
        print("Error inserting scores into db")

    return jsonify(rows)


@app.route("/get_user_score/<int:score_id>")
def get_user_score(score_id):
    """
    Gets score info for score_id, returns a jsonified dictionary for frontend. Almost the same as get_user_scores, but only one score.
    """
    score = Score(api.score("osu", score_id))

    row = {
        "score_id": score.score_id,
        "mods": mod_enum_to_names(score.mods),
        "rank": score.rank,
    }
    row.update(get_beatmap_title_and_link(score.beatmap_id))

    cursor = conn.cursor()
    score.insert(cursor)
    conn.commit()

    return jsonify(row)


@app.route("/predict_beatmaps/", methods=["POST"])
def predict_beatmaps():
    """
    input: user_scores = list of bm_id-mods_enum
    returns: beatmaps = jsonified list of bm_ids-mods_enum
    """
    data = request.json
    noHD = data.get("noHD")
    detect_skillsets = data.get("detectSkillsets")
    num_skillsets = int(data.get("numSkillsets"))
    user_scores = data.get("user_scores")
    # Need to decode mod names back to enum

    scores = [
        score.split("-")[0] + "-" + str(mod_names_to_enum(score.split("-")[1]))
        for score in user_scores
    ]
    user_scores = []

    for score in scores:
        bm_id, mod_enum = score.split("-")
        mod_enum = int(mod_enum)
        if noHD:
            mod_enum &= ~noHD_removed_mods
        else:
            mod_enum &= ~standard_removed_mods

        user_scores.append(f"{bm_id}-{mod_enum}")

    if noHD:
        word2vec_model = word2vec_model_noHD  # CHANGE LATER
        NN = NN_noHD  # CHANGE LATER
    else:
        word2vec_model = word2vec_model_std
        NN = NN_std

    user_scores = [
        score for score in user_scores if score in word2vec_model.wv.index_to_key
    ]

    user_scores = [tuple(word2vec_model.wv[score]) for score in user_scores]
    num_skillsets = min(len(user_scores), num_skillsets)

    if detect_skillsets:
        kmeans = KMeans(n_clusters=num_skillsets, n_init=2, max_iter=50)
        kmeans.fit(user_scores)
        centers = kmeans.cluster_centers_
    else:
        centers = [np.mean(user_scores, axis=0)]

    rows = []

    for center in centers:
        rows_partition = []
        center = [np.array(center)]
        _, indices = NN.kneighbors(center)
        beatmaps_and_mods = [word2vec_model.wv.index_to_key[i] for i in indices[0]][
            : int(200 / len(centers))
        ]  # Remove a couple of recommendations to make space for other clusters

        for beatmap_and_mods in beatmaps_and_mods:
            beatmap_id, mods = beatmap_and_mods.split("-")
            row = {
                "mods": mod_enum_to_names(int(mods)),
            }
            row.update(get_beatmap_title_and_link(beatmap_id))
            row.update(
                get_beatmap_attr(
                    beatmap_id,
                    ["bpm", "ar", "length_seconds", "difficulty_rating"],
                )
            )

            row["length_seconds"] = strftime(
                "%M:%S", gmtime(row["length_seconds"])
            )  # Not really an accurate name for it, but MM:SS is more readable, and I would rather do it here than in the JS where I don't know what i'm doing.

            rows_partition.append(row)

        rows.append(rows_partition)

    return jsonify(rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
