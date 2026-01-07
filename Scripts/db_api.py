from db_init import get_engine
from models import UserSQLModel
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
