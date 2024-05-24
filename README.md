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

# Used to store UserScore data. Contains some deprecated files, including classes.py, and make_tables.ipynb. Also contains parquet files generated from score data.
data/

# Handy scripts to scrape osu! & store data.
scraping/
```

## Try it out

osu!Oracle is currently hosted live at osu-oracle.com.

### Data 

Database schema can be found here: <https://dbdiagram.io/d/osu-654e8e887d8bbd6465f40357>.

Please open an issue on github for a copy of the database, or scrape it yourself using the scripts provided in `/scraping`. Otherwise, all data necessary for training the model should be available in data/top_sentences_std.parquet

### Training
osu!Oracle is based off of collaborative filtering via Item2Vec, implemented through Gensim's Word2Vec. User scores (beatmap-mod) are treated as words, and top scores are used to generate vector embeddings for each beatmap-mod. Predictions are made by clustering top scores (or any list of scores), and applying nearest neighbors to each cluster center. 

To train a model, use `Models/w2v_embeddings.ipynb`. Create a corpus consisting of [beatmap_id-mods, beatmap_id-mods, ... , beatmap_id-mods] for each player's top scores. Some mods are removed. Notably, NC and DT are combined into DT only, and mods such as SD are fully removed.

Train the word2vec model on this corpus, and save the model as `Models/w2v_model_x`. The currently deployed model has hyperparameters: vector_size=15, epochs=70, window=30, min_count=5, workers=16, sg=0, hs=0, negative=20, ns_exponent=0.9. No grid search or validation was performed, which is certainly a point of improvement. 

### Deployment

Osu Oracle is hosted using Flask, a lightweight web framework, Gunicorn, a Python WSGI server for handling requests, and Nginx, a web server and reverse proxy. SSL certifactes were obtained with Certbot. Gunicorn and Nginx are not necessary for local development and model testing.

For local development, run `python3 app.py` after updating model names. The application can then be found at <http://127.0.0.1:8000>.

## Disclaimer

This project is not associated or endorsed by osu.ppy.sh and peppy. If you have any questions or concerns please reach out to me on this repository.
