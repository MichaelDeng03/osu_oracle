from dotenv import dotenv_values
from ossapi import Ossapi

config = dotenv_values()
client_id = config.get('osu_client_id')
client_secret = config.get('osu_client_secret')

if not client_id or not client_secret:
    raise ValueError('osu! API credentials not found in .env file')

ossapi_client = Ossapi(client_id, client_secret)
