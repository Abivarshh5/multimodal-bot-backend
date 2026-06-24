from sqlalchemy import text
from app.db.database import get_connection

def execute_query(query: str, params: dict = None, commit: bool = True):
    with get_connection() as connection:
        result = connection.execute(text(query), params or {})
        if commit:
            connection.commit()
            print("query executed")
        return result

def fetch_one(query: str, params: dict = None):
    with get_connection() as connection:
        result = connection.execute(text(query), params or {})
        print("fetched one row")
        return result.fetchone()

def fetch_all(query: str, params: dict = None):
    with get_connection() as connection:
        result = connection.execute(text(query), params or {})
        print("fetched all")
        return result.fetchall()

def fetch_scalar(query: str, params: dict = None):
    with get_connection() as connection:
        result = connection.execute(text(query), params or {})
        print("fetched scalar")
        return result.scalar()

def execute_returning_id(query: str, params: dict = None):
    with get_connection() as connection:
        result = connection.execute(text(query), params or {})
        connection.commit()
        print("returning id")
        return result.scalar()
