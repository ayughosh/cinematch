from app.user import User
from langchain.tools import tool
from langchain.agents import Tool
from datetime import date, timedelta


@tool
def get_mood_history(input_str: str) -> str:
    """
    Fetch mood history for a user. Input format: "<user_id>, this week"
    Currently supports only "this week".
    """
    try:
        user_id_str, date_range = input_str.split(",", 1)
        user_id = int(user_id_str.strip().strip('"').strip("'"))
        date_range = date_range.strip().lower()
        print(f"[DEBUG] Raw user_id_str: {user_id_str}")

        if date_range != "this week":
            return "❌ Only 'this week' is supported for now."

        today = date.today()
        start_date = today - timedelta(days=today.weekday())  # Monday
        end_date = start_date + timedelta(days=6)  # Sunday

        return User.fetch_user_mood_history(user_id, start_date, end_date)

    except Exception as e:
        return f"❌ Tool error: {e}"


mood_history_tool = Tool.from_function(
    func=get_mood_history,
    name="get_mood_history",
    description="Fetch the mood history of a user for this week. Input: '<user_id>, this week'",
)
