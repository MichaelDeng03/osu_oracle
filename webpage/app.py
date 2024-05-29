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

word2vec_model_std = gensim.models.Word2Vec.load("../Models/recent_word2vec_1.model")

NN_std = NearestNeighbors(n_neighbors=200, algorithm="ball_tree").fit(
    word2vec_model_std.wv.vectors
)


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


@app.route("/help")
def help():
    return render_template("help.html")


@app.route("/")
def home():
    return render_template("index.html")


def get_beatmap_info(beatmap_id):
    """
    Returns a dictionary containing beatmap info for version, title, bpm, ar, total_length, and difficulty_rating, beatmapset_id, list_2x_url, and link
    """
    conn = sqlite3.connect("../data/UserScores.db")
    cursor = conn.cursor()
    try:
        query = f"SELECT version, bpm, ar, total_length, difficulty_rating, beatmapset_id FROM beatmaps_std WHERE beatmap_id = {beatmap_id}"
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            version, bpm, ar, total_length, difficulty_rating, beatmapset_id = result
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

        query = f"SELECT title, list_2x_url, artist, creator, language, genre FROM beatmapsets_std WHERE beatmapset_id = {beatmapset_id}"
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            title, list_2x_url, artist, creator, language, genre = result
        else:
            # If not found, fetch from API and insert
            beatmapset = api.beatmapset(beatmapset_id)
            artist = getattr(beatmapset, "artist", None)
            creator = getattr(beatmapset, "creator", None)
            genre = getattr(beatmapset, "genre", None)
            genre = getattr(genre, "name", None)

            language = getattr(beatmapset, "language", None)
            language = getattr(language, "name", None)

            covers = getattr(beatmapset, "covers", None)
            list_2x_url = getattr(covers, "list_2x", None) if covers else None

            preview_url = getattr(beatmapset, "preview_url", None)
            title = getattr(beatmapset, "title", None)

            beatmapset = (
                int(beatmapset_id),
                artist,
                creator,
                genre,
                language,
                list_2x_url,
                preview_url,
                title,
            )

            query = """
            INSERT INTO beatmapsets_std 
            (beatmapset_id, artist, creator, genre, language, list_2x_url, preview_url, title) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

            lock.acquire()
            cursor.execute(query, beatmapset)
            conn.commit()
            lock.release()

    except Exception as e:
        print(f"Error retrieving beatmapset information: {e}")
        return None

    finally:
        conn.close()
        return {
            "title": title,
            "version": version,
            "bpm": bpm,
            "ar": ar,
            "total_length": total_length,
            "difficulty_rating": difficulty_rating,
            "beatmapset_id": beatmapset_id,
            "link": f"https://osu.ppy.sh/beatmapsets/{beatmapset_id}#osu/{beatmap_id}",
            "list_2x_url": list_2x_url,
            "artist": artist,
            "creator": creator,
            "language": language,
            "genre": genre,
        }


@app.route("/get_image_url_from_mods_enum/<int:mods_enum>")
def mods_enum_to_image_url(mods_enum):
    """
    Returns a list of image urls for the mods_enum
    """
    mods = str(bin(mods_enum))[2:][::-1]
    image_names = [
        "no-fail",
        "easy",
        "touchdevice",
        "hidden",
        "hard-rock",
        "sudden-death",
        "double-time",
        "relax",
        "half",
        "nightcore",
        "flashlight",
        "spun-out",
        "autopilot",
        "perfect",
    ]

    base_url = "https://raw.githubusercontent.com/ppy/osu-web/master/public/images/badges/mods/mod_"

    mod_image_names = [image_names[i] for i in range(len(mods)) if mods[i] == "1"]

    images = [base_url + mod + ".png" for mod in mod_image_names]
    return images


def update_mods(mods_enum, keepHD=True):
    """
    Returns a mods_enum with some mods removed.
    """
    NF = 1
    HD = 8  # Removed only for no HD
    SD = 32
    DT = 64
    NC = 512
    SO = 4096
    PF = 16384
    SV2 = 536870912
    if keepHD:
        mods_removed = NF | SD | SO | PF | SV2 | NC
    else:
        mods_removed = NF | SD | HD | SO | PF | SV2 | NC

    return mods_enum & ~mods_removed


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

            score = {
                "user_id": user_id,
                "beatmap_id": beatmap_id,
                "beatmapset_id": beatmapset_id,
                "pp": pp,
                "mods": mods,
                "created_at": created_at,
                "link": f"https://osu.ppy.sh/beatmapsets/{beatmapset_id}#osu/{beatmap_id}",
            }

            scores.append(score)

        except Exception as e:
            print(e)
            continue

    for score in scores:
        score.update(get_beatmap_info(score["beatmap_id"]))

    for score in scores:
        score["mods"] = update_mods(score["mods"])

    for score in scores:
        score["mods_images"] = mods_enum_to_image_url(score["mods"])

    return jsonify(scores)


@app.route("/get_beatmap/<int:beatmap_id>")
def get_beatmap(beatmap_id):
    mods_enum = request.args.get(
        "modsEnum", default=0, type=int
    )  # Get mods_enum from query parameters

    beatmap = api.beatmap(beatmap_id)
    beatmapset = getattr(beatmap, "_beatmapset", None)
    title = getattr(beatmapset, "title_unicode", None) if beatmapset else None
    covers = getattr(beatmapset, "covers", None)
    list_2x_url = getattr(covers, "list_2x", None) if covers else None
    version = getattr(beatmap, "version", None)
    mods_images = mods_enum_to_image_url(mods_enum)

    return jsonify(
        {
            "title": title,
            "version": version,
            "mods_images": mods_images,
            "list_2x_url": list_2x_url,
            "link": f"https://osu.ppy.sh/beatmapsets/{beatmapset.id}#osu/{beatmap_id}",
            "mods": update_mods(mods_enum),
        }
    )


@app.route("/predict_beatmaps/", methods=["POST"])
def predict_beatmaps():
    """
    input: user_scores = list of bm_id-mods_enum
    returns: beatmaps = jsonified list of bm_ids-mods_enum
    """
    data = request.json
    user_scores = data.get("user_scores")

    model = word2vec_model_std
    NN = NN_std

    top_scores_vec = [model.wv[score] for score in user_scores if score in model.wv]

    # Clustering the score vectors
    # num_clusters = min(10, len(top_scores_vec))
    num_clusters = (len(top_scores_vec) // 8) + 1
    if num_clusters > 1:
        kmeans = KMeans(n_clusters=num_clusters, n_init=40, random_state=0)
        kmeans.fit(top_scores_vec)
        cluster_centers = kmeans.cluster_centers_
    else:
        cluster_centers = [
            np.mean(top_scores_vec, axis=0)
        ]  # Use mean if too few for clustering

    # Calculate the number of results per cluster to meet the 200 total result requirement
    results_per_cluster = 250 // num_clusters

    # Set the number of neighbors dynamically based on the number of results needed per cluster
    NN.set_params(n_neighbors=results_per_cluster)

    beatmaps = []
    beatmaps_set = set()
    for center in cluster_centers:
        neighbors = NN.kneighbors([center])[1][0]
        for i in neighbors:
            beatmap_id = model.wv.index_to_key[i]
            if beatmap_id not in user_scores and beatmap_id not in beatmaps_set:
                beatmaps.append((beatmap_id, model.wv[beatmap_id] - center))
                beatmaps_set.add(beatmap_id)

    beatmaps = sorted(beatmaps, key=lambda x: np.linalg.norm(x[1]), reverse=False)
    beatmaps = [beatmap[0] for beatmap in beatmaps]

    # Retrieve beatmap info and add mod images
    beatmap_info = [get_beatmap_info(beatmap.split("-")[0]) for beatmap in beatmaps]
    for i, beatmap in enumerate(beatmap_info):
        mods = int(beatmaps[i].split("-")[1])
        beatmap["mods_images"] = mods_enum_to_image_url(mods)

    return jsonify(beatmap_info)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
