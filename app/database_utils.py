import psycopg2
import os

def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        return psycopg2.connect(db_url)
    return psycopg2.connect(
        dbname="cinematch",
        user="postgres",
        password="Ayushi11",
        host="localhost",
        port="5432"
    )
