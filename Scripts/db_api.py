from db_init import get_engine
from models import ScoreSQLModel, UserSQLModel
from sqlalchemy import text
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


def fetch_user_ids(page_size: int = 100, offset: int = 0):
    engine = get_engine()
    offset = offset
    while True:
        with Session(engine) as session:
            statement = text(
                "SELECT id FROM usersqlmodel ORDER BY id LIMIT :limit OFFSET :offset"
            )
            results = session.execute(statement, {"limit": page_size, "offset": offset})

            user_ids = [row[0] for row in results.all()]

            if not user_ids:
                break

            yield user_ids

            offset += page_size


def find_offset(user_id: int, page_size: int = 100) -> int:
    engine = get_engine()
    with Session(engine) as session:
        statement = text("SELECT COUNT(*) FROM usersqlmodel WHERE id < :user_id")
        result = session.execute(statement, {"user_id": user_id})
        count = result.scalar_one()
        offset = (count // page_size) * page_size
        return offset
