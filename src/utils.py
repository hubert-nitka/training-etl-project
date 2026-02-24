import psycopg
import os
from datetime import datetime
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_PORT, DB_HOST, LOG_PATH


def log(message, level="INFO", echo=False):
    """
    Write a timestamped message to the log file and optionally print it.

    Args:
        message (str): Text to be logged.
        echo (bool): If True, also print the message to the console.
    """

    timestamp = datetime.utcnow()

    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f'{timestamp} UTC: [{level}] {message}\n')

    if echo is True:
        print(f'{timestamp} UTC: [{level}] {message}\n')

def clear_screen():
    """
        Clears CLI window
    """
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def parse_rest_time(rest_string):
    """
    Parses string like:
    "90 - 120 sek." -> (90, 120)
    "120 sek."      -> (120, 120)

    Returns: (min_seconds, max_seconds) or (None, None)
    """
    if not rest_string or rest_string == "?":
        return (None, None)

    rest_string = rest_string.replace("sek.", "").replace("sek", "").strip()

    if "-" in rest_string:
        parts = rest_string.split("-")
        try:
            return int(parts[0].strip()), int(parts[1].strip())
        except ValueError:
            return (None, None)
    else:
        try:
            val = int(rest_string.strip())
            return (val, val)
        except ValueError:
            return (None, None)

import psycopg
from sqlalchemy import create_engine

def connect_to_database(return_cursor=True, return_engine=False):
    """
    Connects to DB
    return_cursor: True = returns (conn, cur), False = returns only conn
    return_engine: True = returns also SQLAlchemy engine for pandas
    """

    conn = psycopg.connect(f"host={DB_HOST} port={DB_PORT or '5432'} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD or ''}")
    
    engine = None
    if return_engine:
        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD or ''}@{DB_HOST}:{DB_PORT or '5432'}/{DB_NAME}"
        engine = create_engine(connection_string)
    
    if return_cursor:
        if return_engine:
            return conn, conn.cursor(), engine
        else:
            return conn, conn.cursor()
    else:
        if return_engine:
            return conn, engine
        else:
            return conn