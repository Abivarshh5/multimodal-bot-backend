from sqlalchemy import create_engine
from app.core.config import DATABASE_URL

engine = None

def _get_engine():
    global engine
    if engine is None:
        engine = create_engine(DATABASE_URL)
    return engine

def get_connection():
    print("database connected")
    return _get_engine().connect()
