from flask import Flask, render_template, jsonify, request
import sys
from sklearn.neighbors import NearestNeighbors
import gensim
import numpy as np
from ossapi import Ossapi
import sqlite3
import threading

sys.path.insert(0, "../")
from data.classes import Score, Beatmap, Beatmapset
from osu_access_token import client_id, client_secret

app = Flask(__name__)
api = Ossapi(client_id, client_secret)
conn = sqlite3.connect(
    "../data/osu.db", check_same_thread=False
)  # DANGER DANGER: need to lock acquire manually
lock = threading.Lock()

word2vec_model_std = gensim.models.Word2Vec.load("../Models/w2v_model/w2v_model")
NN_std = NearestNeighbors(n_neighbors=100, algorithm="ball_tree").fit(
    word2vec_model_std.wv.vectors
)

word2vec_model_noHD = gensim.models.Word2Vec.load(
    "../Models/w2v_model_noHD_200d/w2v_model_noHD_200d"
)
NN_noHD = NearestNeighbors(n_neighbors=100, algorithm="ball_tree").fit(
    word2vec_model_noHD.wv.vectors
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


@app.route("/")
def home():
    return render_template("index.html")


def get_beatmap_name(beatmap_id):
    conn = sqlite3.connect("../data/osu.db")
    cursor = conn.cursor()
    try:
        query = f"SELECT version, beatmapset_id FROM beatmaps WHERE beatmap_id = {beatmap_id}"
        cursor.execute(query)
        version, beatmapset_id = cursor.fetchone()
        query = f"SELECT title FROM beatmapsets WHERE beatmapset_id = {beatmapset_id}"
        title = cursor.execute(query).fetchone()[0]
    except Exception as e:
        print(e)
        beatmap = Beatmap(api.beatmap(beatmap_id))
        beatmapset = Beatmapset(api.beatmapset(beatmap.beatmapset_id))

        lock.acquire()
        beatmap.insert(cursor)
        beatmapset.insert(cursor)
        conn.commit()
        lock.release()
        title = beatmapset.title
        version = beatmap.version

    finally:
        return f"{title} [{version}]"


def get_beatmap_link(beatmap_id):
    conn = sqlite3.connect("../data/osu.db")
    cursor = conn.cursor()
    try:
        query = f"SELECT beatmapset_id FROM beatmaps WHERE beatmap_id = {beatmap_id}"
        beatmapset_id = cursor.execute(query).fetchone()[0]
        query = f"SELECT beatmapset_link FFROM beatmapsets WHERE beatmapset_id = {beatmapset_id}"
    except Exception as e:
        print(e)
        beatmap = Beatmap(api.beatmap(beatmap_id))
        beatmapset = Beatmapset(api.beatmapset(beatmap.beatmapset_id))
        beatmapset_id = beatmap.beatmapset_id

        lock.acquire()
        beatmap.insert(cursor)
        beatmapset.insert(cursor)
        conn.commit()
        lock.release()
    finally:
        return f"https://osu.ppy.sh/beatmapsets/{beatmapset_id}#osu/{beatmap_id}"


def get_beatmap_stars(beatmap_id):
    try:
        conn = sqlite3.connect("../data/osu.db")
        cursor = conn.cursor()
        query = (
            f"SELECT difficulty_rating FROM beatmaps WHERE beatmap_id = {beatmap_id}"
        )
        stars = cursor.execute(query).fetchone()[0]
    except Exception as e:
        print(e)
        beatmap = Beatmap(api.beatmap(beatmap_id))
        beatmapset = Beatmapset(api.beatmapset(beatmap.beatmapset_id))

        lock.acquire()
        beatmap.insert(cursor)
        beatmapset.insert(cursor)
        conn.commit()
        lock.release()
        stars = beatmap.difficulty_rating
    finally:
        return stars


@app.route("/get_user_scores/<int:user_id>")
def get_user_scores(user_id):
    try:
        top_scores = api.user_scores(user_id, type="best", mode="osu", limit=100)
        scores = []
        for score in top_scores:
            try:
                score = Score(score)
                scores.append(score)
                score.name = get_beatmap_name(score.beatmap_id)
            except Exception as e:
                print(f"Error creating score object: {e}")
                continue

    except Exception as e:
        print(e)
        return None

    for score in scores:
        score.mods = mod_enum_to_names(score.mods)

    rows = []
    for score in scores:
        rows.append(
            {
                "score_id": score.score_id,
                "beatmap_id": score.beatmap_id,
                "beatmap_link": get_beatmap_link(score.beatmap_id),
                "beatmap_name": score.name,
                "mods": score.mods,
                "rank": score.rank,
            }
        )

    return jsonify(rows)


@app.route("/get_user_score/<int:score_id>")
def get_user_score(score_id):
    score = Score(api.score("osu", score_id))
    score.mods = mod_enum_to_names(score.mods)

    return jsonify(score)


@app.route("/predict_beatmaps/", methods=["POST"])
def predict_beatmaps():
    """
    input: user_scores = list of bm_id-mods_enum
    returns: beatmaps = jsonified list of bm_ids-mods_enum
    """
    data = request.json
    noHD = data.get("noHD")
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

    user_scores = [word2vec_model.wv[score] for score in user_scores]

    distances, indices = NN.kneighbors([np.mean(user_scores, axis=0)])
    beatmaps_and_mods = [word2vec_model.wv.index_to_key[i] for i in indices[0]]

    rows = []
    for beatmap_and_mods in beatmaps_and_mods:
        beatmap_id, mods = beatmap_and_mods.split("-")
        mods = int(mods)
        mods = mod_enum_to_names(mods)
        title = get_beatmap_name(beatmap_id)

        rows.append(
            {
                "beatmap_id": beatmap_id,
                "mods": mods,
                "title": title,
                "beatmap_link": get_beatmap_link(beatmap_id),
                "stars": get_beatmap_stars(beatmap_id),
            }
        )

    return jsonify(rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
