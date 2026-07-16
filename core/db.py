import sqlite3
import pandas as pd
from functools import lru_cache
from pathlib import Path

# Resolve db_path relative to project root, not cwd
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_DB_PATH = str(_PROJECT_ROOT / "data" / "incidents.db")


@lru_cache(maxsize=4)
def get_db_connection(db_path=_DEFAULT_DB_PATH):
    """
    Creates and caches a SQLite database connection.
    Pure Python — no Streamlit dependency.
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return conn


def execute_query(query, params=(), db_path=_DEFAULT_DB_PATH):
    """
    Executes a query and returns a pandas DataFrame.
    """
    conn = get_db_connection(db_path)
    return pd.read_sql_query(query, conn, params=params)
