from sqlalchemy import create_engine, text
from app.core.config import DATABASE_URL
from app.db.queries import (
    CREATE_WEBSITES_TABLE,
    CREATE_CRAWLED_PAGES_TABLE,
    CREATE_CRAWL_STATUS_TABLE,
    ADD_URLS_COLUMN,
    CREATE_BRAND_PROFILE_TABLE
)

engine = create_engine(DATABASE_URL)

def init_db():
    print("Initializing database tables...")
    with engine.connect() as conn:
        conn.execute(text(CREATE_WEBSITES_TABLE))
        conn.execute(text(CREATE_CRAWLED_PAGES_TABLE))
        conn.execute(text(CREATE_CRAWL_STATUS_TABLE))
        conn.execute(text(ADD_URLS_COLUMN))
        conn.execute(text(CREATE_BRAND_PROFILE_TABLE))
        conn.commit()
    print("Database tables initialized successfully.")

def get_connection():
    print("database connected")
    return engine.connect()
