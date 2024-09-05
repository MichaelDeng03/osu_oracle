""" Basically the same thing as the jupyter notebook. Not really necessary, nor updated"""

# import sqlite3
import sys

import gensim
import numpy as np
from dotenv import dotenv_values
from ossapi import Ossapi
from sklearn.neighbors import NearestNeighbors

from osu_oracle.classes import Score

config = dotenv_values("../.env")
client_id = config["osu_client_id"]
client_secret = config["osu_client_secret"]


def predict_beatmaps(user_id):
    """
    Uses the word2vec encoding created in nearest_neighbors.ipynb to find the nearest neighbors
    of provided beatmaps.
    """
    word2vec_model = gensim.models.Word2Vec.load("w2v-pp")
    NN = NearestNeighbors(n_neighbors=5, algorithm="ball_tree").fit(word2vec_model.wv.vectors)

    # Pull top play data from ossapi
    api = Ossapi(client_id, client_secret)
    top_scores = api.user_scores(user_id, type="best", mode="osu", limit=100)
    top_scores = [Score(score) for score in top_scores]

    user_scores = [str(score.beatmap_id) + "-" + str(score.mods) for score in top_scores]
    user_scores = [score for score in user_scores if score in word2vec_model.wv.index_to_key]
    user_scores = [word2vec_model.wv[score] for score in user_scores]

    # Find the nearest neighbors of the mean of the top plays
    distances, indices = NN.kneighbors([np.mean(user_scores, axis=0)])
    beatmaps = [word2vec_model.wv.index_to_key[i] for i in indices[0]]

    return beatmaps


def main():
    args = sys.argv[1:]
    if args:
        user_id = args[0]

    print(predict_beatmaps(user_id))


if __name__ == "__main__":
    main()
