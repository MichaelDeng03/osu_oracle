from flask import Flask, render_template, jsonify, request
import sys
from sklearn.neighbors import NearestNeighbors
import gensim
import numpy as np
from ossapi import Ossapi
import sqlite3

sys.path.insert(0, "../")
from data.classes import Score
from osu_access_token import client_id, client_secret

app = Flask(__name__)
api = Ossapi(client_id, client_secret)
# conn = sqlite3.connect("../data/osu.db")

word2vec_model = gensim.models.Word2Vec.load("../Models/w2v_model/w2v_model")
NN = NearestNeighbors(n_neighbors=100, algorithm="ball_tree").fit(
    word2vec_model.wv.vectors
)
mod_enums = [
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


def mod_enum_to_names(mod_enum):
    mod_enum = bin(mod_enum)[2:] + "0"
    mod_enum = mod_enum[::-1]
    mod_enum = list(mod_enum)
    mods = [mod_enums[i] for i in range(len(mod_enum)) if mod_enum[i] == "1"]
    mods = ", ".join(mods)

    return mods


def mod_names_to_enum(mod_names):
    mod_names = mod_names.split(", ")
    enum = 0
    for i, mod_name in enumerate(mod_enums):
        for mod in mod_names:
            if mod_name == mod:
                enum += 2**i

    return enum


@app.route("/wip")
def wip():
    return render_template("wip.html")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get_user_scores/<int:user_id>")
def get_user_scores(user_id):
    try:
        top_scores = api.user_scores(user_id, type="best", mode="osu", limit=100)
        scores = []
        for score in top_scores:
            try:
                score = Score(score)
                scores.append(score)
            except Exception as e:
                print(f"Error creating score object: {e}")
                continue

    except Exception as e:
        print(e)
        return None

    for score in scores:
        score.mods = mod_enum_to_names(score.mods)

    return jsonify(scores)


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
        NC = 512
        SD = 32
        SO = 4096
        PF = 16384
        mod_enum &= ~NC
        mod_enum &= ~SD
        mod_enum &= ~SO
        mod_enum &= ~PF
        user_scores.append(score)

    user_scores = [
        score for score in user_scores if score in word2vec_model.wv.index_to_key
    ]
    user_scores = [word2vec_model.wv[score] for score in user_scores]
    distances, indices = NN.kneighbors([np.mean(user_scores, axis=0)])
    beatmaps = [word2vec_model.wv.index_to_key[i] for i in indices[0]]

    beatmaps = [
        [beatmap.split("-")[0], mod_enum_to_names(int(beatmap.split("-")[1]))]
        for beatmap in beatmaps
    ]

    return jsonify(beatmaps)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
