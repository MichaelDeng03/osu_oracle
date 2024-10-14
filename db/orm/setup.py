from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker
from sqlmodel import Session as SQLModelSession
from sqlmodel import SQLModel, create_engine

# Necessary for sqlmodel metadata
from db.orm import models  # noqa

DATABASE_URL = 'sqlite:///./osu.db'
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SQLModel.metadata.create_all(engine)


@contextmanager
def Session():
    session = SQLModelSession(engine)
    try:
        yield session
    finally:
        session.close()
