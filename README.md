# 🔮 osu!Oracle

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install required dependencies.

```bash
pip install -r requirements.txt
```
API Tokens should be stored as environment variables under
OSU_CLIENT_ID and OSU_CLIENT SECRET

## File structure

```bash
# Web application and user-input handling.
webpage/

# Model training and saved models.
Models/

# CRUD + db
db/

# Scripts for collecting data via osu's API
data_collector/
```

## Try it out

osu!Oracle is currently hosted live at osu-oracle.com.


### Training

osu!Oracle is based off of collaborative filtering via Item2Vec, implemented through Gensim's Word2Vec. User scores (beatmap-mod) are treated as words, and top scores are used to generate vector embeddings for each beatmap-mod. Predictions are made by clustering top scores (or any list of scores), and applying nearest neighbors to each cluster center. 

To train a model, use `Models/w2v_embeddings.ipynb`. Create a corpus consisting of [beatmap_id-mods, beatmap_id-mods, ... , beatmap_id-mods] for each player's top scores. Some mods are removed. Notably, NC and DT are combined into DT only, and mods such as SD are fully removed.

Train the word2vec model on this corpus, and save the model as `Models/w2v_model_x`. The currently deployed model has hyperparameters: vector_size=15, epochs=70, window=30, min_count=5, workers=16, sg=0, hs=0, negative=20, ns_exponent=0.9. No grid search or validation was performed, which is certainly a point of improvement.

### Deployment


## Disclaimer

This project is not associated or endorsed by osu.ppy.sh and peppy. If you have any questions or concerns please reach out to me on this repository.
