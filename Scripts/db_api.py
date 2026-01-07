from db_init import get_engine
from models import ScoreSQLModel, UserSQLModel
from sqlmodel import Session


def put_users(users: list[UserSQLModel]) -> None:
    """
    Saves a list of UserSQLModel to the database.
    """
    engine = get_engine()
    with Session(engine) as session:
        for user in users:
            session.add(user)
        session.commit()


def upsert_user(user: UserSQLModel) -> None:
    """
    Upserts a UserSQLModel to the database.
    """
    engine = get_engine()
    with Session(engine) as session:
        session.merge(user)
        session.commit()


def upsert_users(users: list[UserSQLModel]) -> None:
    """
    Upserts a list of UserSQLModel to the database.
    """
    engine = get_engine()
    with Session(engine) as session:
        for user in users:
            session.merge(user)
        session.commit()


def upsert_scores(scores: list["ScoreSQLModel"]) -> None:
    """
    Upserts a list of ScoreSQLModel to the database.
    """
    engine = get_engine()
    with Session(engine) as session:
        for score in scores:
            session.merge(score)
        session.commit()
