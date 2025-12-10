from dotenv import load_dotenv
import sqlite3
from sqlalchemy import create_engine
from models import * # Necessary to load metadata for sqlmodels
from sqlmodel import SQLModel

def create_db_and_tables():
	engine = create_engine('sqlite:///oracle-dev.db', echo=True)
	SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
	try:
		load_dotenv()
		create_db_and_tables()	
	except Exception as e:
		print(f"Error creating database and tables: {e}")
