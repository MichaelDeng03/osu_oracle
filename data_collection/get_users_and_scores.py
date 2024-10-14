from data_collection import ossapi_client


def get_user_and_scores(user_id: int, mode: str = 'osu', type: str = 'best'):
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
        }
        print(score_data)
