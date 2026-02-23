import psycopg
from datetime import datetime
from config import LOG_PATH


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

def connect_to_database(host, db_name, user, password="", port="5432"):
    
    conn = psycopg.connect(f"host={host} port={port} dbname={db_name} user={user} password={password}")
    cur = conn.cursor()

    return(conn,cur)