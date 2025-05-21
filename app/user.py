from flask_login import UserMixin
import psycopg2
from app.database_utils import get_db_connection


class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return User(id=row[0], username=row[1], email=row[2])
        return None

    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, email FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return User(id=row[0], username=row[1], email=row[2])
        return None

    @staticmethod
    def fetch_user_mood_history(user_id, start_date, end_date):
        """Return a user's past mood selections as a readable string."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT mood, timestamp
            FROM mood_logs
            WHERE user_id = %s AND timestamp BETWEEN %s AND %s
            ORDER BY timestamp DESC
            """,
            (user_id, start_date, end_date),
        )

        results = cursor.fetchall()
        cursor.close()
        conn.close()

        if not results:
            return f"No mood history found for user {user_id} this week."

        return "\n".join(
            f"🟡 Mood: {row[0]} on {row[1].strftime('%A, %d %b')}" for row in results
        )
