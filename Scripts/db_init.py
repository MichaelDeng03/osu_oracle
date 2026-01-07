import sqlite3

from dotenv import load_dotenv
from models import *  # Necessary to load metadata for sqlmodels # noqa: F403, F401
from sqlalchemy import create_engine
from sqlmodel import SQLModel


def create_db_and_tables():
    engine = create_engine("sqlite:///oracle-dev.db", echo=True)
    SQLModel.metadata.create_all(engine)


def get_engine():
    engine = create_engine("sqlite:///oracle-dev.db", echo=False)
    return engine


if __name__ == "__main__":
    try:
        load_dotenv()
        create_db_and_tables()
    except Exception as e:
        print(f"Error creating database and tables: {e}")
