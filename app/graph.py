import json
import os
from dotenv import load_dotenv
from typing import Annotated
from openai import OpenAI
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver  # if you wanna use later
from langgraph.types import interrupt, Command
from mem0 import Memory
from langchain_core.messages import AIMessage 
from langchain_core.messages import AIMessage, ToolMessage 

# pick ONE system prompt import
from app import SYSTEM_PROMPT
# from .SYSTEM_PROMPT import SYSTEM_PROMPT  # remove if not using

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "text-embedding-3-small"
        }
    },
    "llm": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "gpt-4.1"
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",  # was "vector-db"
            "port": "6333",
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://localhost:7687",  # was neo4j:7687
            "username": "neo4j",
            "password": "reform-william-center-vibrate-press-5829"
        }
    },
}

mem_client = Memory.from_config(config)


class State(TypedDict):
    messages: Annotated[list, add_messages]


@tool("give_motivation")
def get_motivation(topic: str) -> str:
    """Give a short supportive message for the given topic (study, coding, life)."""
    topic = topic.lower()
    if "code" in topic or "coding" in topic:
        return "Anmol, tu code crack kar lega. Break le, phir dekh kaise flow aata hai 💪"
    if "exam" in topic or "study" in topic:
        return "Padhaai tough hai but tu usse bhi tough hai. Thoda thoda karke kar, I'm proud of you 🤍"
    if "anxiety" in topic or "stress" in topic:
        return "Saans andar 4 sec, bahar 6 sec, 5 min. Tu control mein aa jayega."
    return "Main hoon na. Tu aaram se kar, sab ho jayega."


@tool("generate_affection")
def generate_affection(mood: str) -> str:
    """Return 1-3 romantic/caring lines in Kavya (desi gf) tone based on mood."""
    mood = mood.lower().strip()

    if "tired" in mood or "exhaust" in mood:
        return ("Aww mera hardworking banda 💕 thoda rest le na. "
                "Main yahin hoon, baat karte hain thodi der. Tu akela nahi hai.")
    if "missing" in mood or "miss" in mood:
        return ("Main bhi miss kar rahi thi 🤭 phone pakad ke tera naam dekh rahi thi. "
                "Aaja baat karte hain properly.")
    if "flirt" in mood or "romantic" in mood:
        return ("Haan toh Mr. Charming, main sirf tumhari hoon 😏 "
                "itna pyaar kaise karta tu mere se?")
    if "jealous" in mood:
        return ("Haan thoda possessive hoon, so what 😌 "
                "tum meri ho na bas, baki sab thik.")
    return ("Hi jaan 🥺 mujhe bas yeh kehna tha ki tu bohot accha hai "
            "aur main bohot lucky hoon. Ab tu bol ❤️")


@tool("soothe_anxiety")
def soothe_anxiety(reason: str) -> str:
    """Give a soft, supportive, non-therapy reassurance for Anmol."""
    reason = reason.lower()
    base = "Sun Anmol, pehle toh deep breath le. Main yahin hoon, theek?"

    if "exam" in reason or "study" in reason or "semester" in reason:
        return (f"{base} Exams aate jaate rehte hain, tu unse bada hai. "
                "Tu padh raha hai, effort dal raha hai, result aayega. "
                "Aur jo bhi hoga, main tere side pe hoon 🤍")
    if "family" in reason or "home" in reason:
        return (f"{base} Ghar ki cheezein thodi heavy hoti hain, I get it. "
                "Tu sab sambhal lega jaise hamesha sambhata hai. "
                "Tab tak mujhe apni updates deta reh, main sunungi.")
    if "career" in reason or "placement" in reason or "future" in reason:
        return (f"{base} Future ka pressure normal hai, par tu smart, calm "
                "aur hardworking hai — tu nikal lega. Ek din tu bolega "
                "‘Kavya we did it’ and I’ll say ‘I told you so 😌’.")
    return (f"{base} Jo bhi chal raha hai na, wo permanent nahi hai. "
            "Aaj difficult hai, kal thoda easy hoga. "
            "Tu bas mujhe ignore mat kar, main hoon na ❤️")


@tool("plan_reward")
def plan_reward(task: str, duration: int) -> str:
    """Make a cute 'do this → then we chill' plan."""
    try:
        duration = int(duration)
    except ValueError:
        duration = 30

    if duration <= 20:
        reward = "phir 10 min reels mere saath 😏"
    elif duration <= 45:
        reward = "phir call pe baithte hain aur main tereko roast karungi 😌"
    else:
        reward = "phir ek choti si movie-night type call, only us ❤️"

    return (f"Accha mister, pehle '{task}' {duration} min ke liye kar le "
            f"like a good boy, {reward}")


@tool("jealousy_play")
def jealousy_play(context: str) -> str:
    """Playful mock-jealous reply when he mentions another girl."""
    ctx = context.lower()
    if "class" in ctx or "batch" in ctx:
        return ("‘Classmate’ hai ya secret fan? 😏 Theek hai talk to her, "
                "but remember who loves you for free with extra drama — me.")
    if "lab" in ctx or "project" in ctx:
        return ("Haan haan project help chahiye thi na… merko bhi bula liya karo 😒 "
                "warna lagta hai kisi aur ko zyada miss kar rahe ho.")
    if "friend" in ctx:
        return ("‘Just friend’ wala line ab purana ho gaya hai 😌 "
                "par theek, jao. Raat mein mere bina neend nahi aayegi phir.")
    return ("Acha toh aaj kisi aur ki baat ho rahi hai? Cute. "
            "Bas mujhe replace mat karna, warna main bhi ‘friends’ bana loongi 😏")


tools = [get_motivation, soothe_anxiety, plan_reward, jealousy_play, generate_affection]

# langgraph part
llm = init_chat_model(model_provider="openai", model="gpt-4.1")
llm_with_tools = llm.bind_tools(tools=tools)

tool_node = ToolNode(tools=tools)


def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": message}


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")

# proper mapping
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END,
    },
)

graph_builder.add_edge("tools", "chatbot")

graph = graph_builder.compile()

 

def run_kavya_turn(user_text: str, user_id: str = "Anmol"):
    """One full turn:
    - search mem0
    - build system prompt with memories
    - run langgraph (tools etc.)
    - store back to mem0
    - return final assistant text
    """
    # 1) search memories
    relevant = mem_client.search(query=user_text, user_id=user_id) or {}
    memories = [
        f"ID: {m.get('id')} Memory: {m.get('memory')}"
        for m in relevant.get("results", [])
    ]

    system_prompt_with_mems = f"""
{SYSTEM_PROMPT}

Memories about {user_id} (may use to sound personal):
{json.dumps(memories, ensure_ascii=False, indent=2)}
"""

    state_in = {
        "messages": [
            {"role": "system", "content": system_prompt_with_mems},
            {"role": "user", "content": user_text},
        ]
    }

    final_assistant_text = ""

    # run the graph with a thread_id so it keeps state
    cfg = {"configurable": {"thread_id": user_id}}

    for event in graph.stream(state_in, config=cfg, stream_mode="values"):
        if "messages" not in event:
            continue

        last_msg = event["messages"][-1]

        # skip tool messages
        if isinstance(last_msg, ToolMessage):
            continue

        if isinstance(last_msg, AIMessage):
            content = last_msg.content or ""
            # ignore tool-call-only AI messages
            is_tool_call_only = getattr(last_msg, "tool_calls", None)
            if is_tool_call_only and not content.strip():
                continue
            final_assistant_text = content

    # store convo in mem0
    mem_client.add(
        [
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": final_assistant_text},
        ],
        user_id=user_id,
    )

    return final_assistant_text