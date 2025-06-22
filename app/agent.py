from langchain_community.llms import Ollama
from langchain.agents import initialize_agent, Tool, AgentType
from flask_login import current_user
from .tools import get_mood_history
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemma LLM via Ollama
llm = Ollama(model="gemma:2b", base_url="http://ollama:11434", temperature=0.3)


# Define LangChain tool(s)
tools = [
    Tool.from_function(
        func=get_mood_history,
        name="get_mood_history",
        description="Get mood history for a user. Input format: '<user_id>, this week'",
    )
]

# Create the agent that can both chat and call tools
agent = initialize_agent(
    tools=tools, llm=llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=False
)


def run_ai_agent(user_input: str, user_id: int) -> str:
    context = f"The current user has ID {user_id}. If the question is about mood history or something you need tools for, use them. Otherwise, reply conversationally."
    print("RUN_AI_AGENT USING:", llm)
    return agent.run(f"{context}\n{user_input}")
