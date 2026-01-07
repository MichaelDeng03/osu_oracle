import sqlite3

from dotenv import load_dotenv
from models import *  # Necessary to load metadata for sqlmodels # noqa: F403, F401
from sqlalchemy import create_engine
from sqlmodel import SQLModel


def create_db_and_tables():
    engine = create_engine("sqlite:///oracle-dev.db", echo=True)
    SQLModel.metadata.create_all(engine)


def get_engine():
    engine = create_engine("sqlite:///oracle-dev.db", echo=True)
    return engine


def put_users(users: list[UserSQLModel]) -> None:
    """
    Saves a list of UserSQLModel to the database.
    """
    engine = get_engine()
    with Session(engine) as session:
        for user in users:
            session.add(user)
        session.commit()


if __name__ == "__main__":
    try:
        load_dotenv()
        create_db_and_tables()
    except Exception as e:
        print(f"Error creating database and tables: {e}")
