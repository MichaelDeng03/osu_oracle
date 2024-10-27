from db import crud
from db.orm import Session, models

from .client import ossapi_client


def get_user_scores(user_id: int, mode: str = 'osu', type: str = 'best'):
    """
    Gets and saves a user's top scores
    """
    top_scores = ossapi_client.user_scores(user_id, mode=mode, type=type, limit=100)
    for score in top_scores:
        score_data = {
            "id": score.id,
            "pp": score.pp,
            "beatmap_id": score.beatmap.id,
            "user_id": user_id,
            "set_at": score.created_at,
            "mods": score.mods.value,
        }
        with Session() as session:
            score = models.Score(**score_data)
            crud.create_or_ignore(session, score)
