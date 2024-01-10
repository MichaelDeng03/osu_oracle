# 🔮 osu!Oracle

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install required dependencies.

```bash
pip install -r requirements.txt
```

Until oAuth authentication with osu! is implemented, API credentials are stored in a file named `osu_access_token.py` which must be created in `data/` and `scraping/`.

An example file looks like the following:
```python
client_id = 13337
client_secret = "supersecretrandomstringfromosu"
```

## File structure

```bash
# Web application and user-input handling.
backend/

# TODO
Models/

# Used to store osu! data, notebook is for creating the schema.
data/

# Handy scripts to scrape osu! & store data.
scraping/
```

## Try it out

osu!Oracle is currently hosted live at [http://75.101.182.162:5001/](http://75.101.182.162:5001/).

## Contributing?
Database schema can be found here: https://dbdiagram.io/d/osu-654e8e887d8bbd6465f40357.
You may message u/EggTofu on Reddit for a copy of the database, or scrape it yourself using the scripts provided in /scraping.

## Disclaimer

This project is not associated or endorsed by osu.ppy.sh. If you have any questions or concerns reach out to @ u/EggTofu on Reddit.
