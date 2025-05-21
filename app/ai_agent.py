from flask import Blueprint, render_template, request
from flask_login import current_user
from app.agent import run_ai_agent
from langchain_community.llms import Ollama
import time, logging, requests
from app.user import User

fallback_llm = Ollama(
    model="mistral",
    base_url="http://ollama:11434",  # IMPORTANT: ensures it doesn’t use localhost from inside the container
    temperature=0.3,
)

# fallback_llm = Ollama(model="mistral", temperature=0.3)

ai_bp = Blueprint("ai", __name__)


def ollama_fast_reply(user_input):
    system_prompt = (
        "You are Melissa, a kind and helpful assistant who answers with warmth and clarity. "
        "Always greet users politely and keep responses short and natural."
    )

    full_prompt = f"{system_prompt}\n\nUser: {user_input}\nAssistant:"

    res = requests.post(
        "http://ollama:11434/api/generate",
        json={
            "model": "tinyllama",  # use a stronger model for better response
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "num_predict": 100,
                "temperature": 0.7,
            },
        },
    )
    return res.json()["response"]


def is_simple_query(user_input):
    classification_prompt = f"""
Classify the following user input into one of these categories: greeting, smalltalk, movie_request, complex.

User input: '{user_input}'
Category:"""

    res = requests.post(
        "http://ollama:11434/api/generate",
        json={
            "model": "tinyllama",
            "prompt": classification_prompt.strip(),
            "stream": False,
            "options": {"num_predict": 10},
        },
    )

    category = res.json()["response"].strip().lower()
    return category in ["greeting", "smalltalk", "movie_request"]


@ai_bp.route("/ai-agent")
def ai_agent():
    return render_template("ai_agent.html")


@ai_bp.route("/ai-chat", methods=["POST"])
def ai_chat():
    user_input = request.form.get("user_input", "").strip()

    # Handle missing or unauthenticated users
    if current_user.is_authenticated:
        print("Current user authenticated:", current_user.is_authenticated)
        print("Current user ID:", current_user.id)
        user_id = current_user.id
        username = current_user.username
        prompt = (
            f"You're helping {username}. Respond warmly and personally. {user_input}"
        )
    else:
        user_id = 4  # fallback to a known test user in the database
        prompt = user_input

    # response = run_ai_agent(user_input, user_id=user_id)
    # start_time = time.time()

    try:
        if is_simple_query(prompt):
            response = ollama_fast_reply(prompt)
            query_type = "simple"
        else:
            response = run_ai_agent(prompt, user_id=int(user_id))
            query_type = "agent"

    except Exception as e:
        response = f"⚠️ Error: {str(e)}"
        query_type = "error"
    # duration = round(time.time() - start_time, 2)

    # 📝 Log query type, user ID, time taken, and truncated response
    # logging.info(
    # f"User {user_id} | Type: {query_type} | Time: {duration}s | Input: {user_input} | Response: {response[:200]}"
    # )
    # return f"<p>{response}</p>"
    return render_template("ai_agent.html", response=response)


# return fallback_llm.invoke(user_input)
