from db import crud
from db.orm import Session, models

from .client import ossapi_client


def get_beatmap(beatmap_id: int):
    """
    Gets a beatmap
    """
    beatmap = ossapi_client.beatmap(beatmap_id)
    beatmap_data = {
        "id": beatmap.id,
        "mode": beatmap.mode.value,
        "beatmapset_id": beatmap.beatmapset_id,
        "difficulty_rating": beatmap.difficulty_rating,
        "bpm": beatmap.bpm,
        "cs": beatmap.cs,
        "od": beatmap.difficulty_rating,
        "ar": beatmap.ar,
        "length": beatmap.total_length,
        "version": beatmap.version,
    }

    with Session() as session:
        beatmap = models.Beatmap(**beatmap_data)
        crud.create_or_ignore(session, beatmap)


def get_beatmapset(beatmapset_id: int):
    beatmapset = ossapi_client.beatmapset(beatmapset_id)
    beatmapset_data = {
        "id": beatmapset.id,
        "ranked_date": beatmapset.ranked_date,
        "title": beatmapset.title,
        "artist": beatmapset.artist,
        "mapper_id": beatmapset.creator,
    }
    with Session() as session:
        beatmapset = models.Beatmapset(**beatmapset_data)
        crud.create_or_ignore(session, beatmapset)
