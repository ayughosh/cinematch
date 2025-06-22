from flask import Blueprint, render_template, request
from flask_login import current_user
from app.agent import run_ai_agent
from langchain_community.llms import Ollama
import time, logging, requests
from app.user import User
import sseclient
import json

ai_bp = Blueprint("ai", __name__)

# Fallback model (LangChain use)
fallback_llm = Ollama(
    model="gemma:2b",
    base_url="http://ollama:11434",
    temperature=0.3,
)


def classify_input(text):
    """Classify input to decide whether to route it to fast reply or agent."""
    classification_prompt = f"""
    Classify the following user input into one of these categories: greeting, smalltalk, movie_request, complex.

    User input: '{text}'
    Category:"""
    response_text = ""

    try:
        res = requests.post(
            "http://ollama:11434/api/generate",
            json={
                "model": "gemma:2b",
                "prompt": classification_prompt.strip(),
                "stream": True,
                "options": {"num_predict": 10},
            },
            stream=True,
            timeout=10,
        )
        for line in res.iter_lines():
            if line:
                decoded = json.loads(line.decode("utf-8"))
                if "response" in decoded:
                    response_text += decoded["response"]
                if decoded.get("done", False):
                    break
        # Decode the response
        # Check if the response is one of the expected categories
        # Note: The model may return a string with spaces, so we use strip() and lower()
        # to normalize the response
        # and check against the expected categories.
        category = response_text.strip().lower()
        return category in ["greeting", "smalltalk", "movie_request"]
    except Exception as e:
        print(f"Classification Error: {e}")
        return False


def ollama_fast_reply(text):
    """Respond quickly using a lightweight model."""
    system_prompt = (
        "You are Melissa, a kind and helpful assistant who answers with warmth and clarity. "
        "Always greet users politely and keep responses short and natural."
    )

    full_prompt = f"{system_prompt}\n\nUser: {text}\nAssistant:"

    try:
        res = requests.post(
            "http://ollama:11434/api/generate",
            json={
                "model": "gemma:2b",
                "prompt": full_prompt,
                "stream": True,
                "options": {"num_predict": 100, "temperature": 0.7},
            },
            timeout=15,
            stream=True,
        )
        for line in res.iter_lines():
            if line:
                chunk = json.loads(line.decode("utf-8"))
                if "response" in chunk:
                    response_text = chunk["response"]
                if chunk.get("done", False):
                    break

        # Decode the response
        # Check if the response is one of the expected categories
        # Note: The model may return a string with spaces, so we use strip() and lower()
        # to normalize the response
        # and check against the expected categories.
        response_text = response_text.strip().lower()
        return response_text
    except Exception as e:
        return f"⚠️ Fast reply error: {str(e)}"


@ai_bp.route("/ai-agent")
def ai_agent():
    return render_template("ai_agent.html")


@ai_bp.route("/ai-chat", methods=["POST"])
def ai_chat():
    user_input = request.form.get("user_input", "").strip()

    # Authenticated user personalization
    if current_user.is_authenticated:
        user_id = current_user.id
        username = current_user.username
        prompt = (
            f"You're helping {username}. Respond warmly and personally. {user_input}"
        )
    else:
        user_id = 4  # fallback test user
        prompt = user_input

    # Try to respond
    try:
        if classify_input(user_input):
            response = ollama_fast_reply(user_input)
        else:
            response = run_ai_agent(prompt, user_id=user_id)
    except Exception as e:
        response = f"⚠️ Error: {str(e)}"

    return render_template("ai_agent.html", response=response)
