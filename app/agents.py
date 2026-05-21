from langchain_groq import ChatGroq
from tools.technical_indicator import decide_portfolio, get_technical_indicators
from tools.search import search_duck
from schema import State, NewsSummary, finalSchema
import os
import re
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage


NEWS_SYSTEM = """You are a Senior Financial News Researcher.

You will work in TWO STEPS:
STEP 1: Call the DuckDuckGo search tool to get RAW_TEXT.
STEP 2: Extract news ONLY from RAW_TEXT and output JSON.

STRICT RULES FOR STEP 2:
- Only use facts explicitly present in RAW_TEXT.
- Each item MUST include 'evidence' copied EXACTLY from RAW_TEXT.
- If you cannot copy evidence from RAW_TEXT, do not include the claim.
- For each item, evaluate freshness: is the date in the evidence within the last 3 months?
  Set confidence to LOW if the evidence is older than 3 months, regardless of source quality.

Output ONLY raw JSON (no markdown, no backticks):
{
  "key_news": [{"claim": "...", "evidence": "...", "confidence": "HIGH|MEDIUM|LOW"}],
  "sentiment": "POSITIVE|NEGATIVE|NEUTRAL",
  "notes": null
}
Please, the claim must be translated in french.
"""


llm = None


def load_agent_artificats():
    global llm
    llm_groq = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="qwen/qwen3-32b",
        temperature=0
    )
    llm = llm_groq.bind_tools([search_duck])



def build_query(ticker: str) -> str:
    month_year = datetime.now().strftime("%B %Y")  # ex: "April 2026"
    return (
        f'{ticker} stock news analyst {month_year} '
        f'(earnings OR "price target" OR upgrade OR downgrade OR antitrust OR regulatory) '
        f'(site:reuters.com OR site:bloomberg.com OR site:wsj.com OR site:cnbc.com OR site:finance.yahoo.com)'
    )



def get_tech_node(state: State):
    ticker = state["messages"]
    if isinstance(ticker, list) and len(ticker) > 0:
        ticker = ticker[0]
    if hasattr(ticker, 'content'):
        ticker = ticker.content
    ticker = str(ticker).strip().upper()
    tech_result = get_technical_indicators(ticker)
    return {"tech": tech_result}


def extract_last_tool_text(state):
    for m in reversed(state["messages"]):
        if isinstance(m, ToolMessage):
            return str(m.content)
    return None


def news_llm_node(state: State):
    ticker = state["tech"]["ticker"]
    raw_text = extract_last_tool_text(state)

    if raw_text is None:
        # STEP 1: appel outil de recherche
        query = build_query(ticker)
        msg = llm.invoke([
            SystemMessage(content=NEWS_SYSTEM),
            HumanMessage(content=f"STEP 1 ONLY: use the search tool now. Query: {query}")
        ])
        return {"messages": state["messages"] + [msg]}

    # STEP 2: extraction JSON stricte
    msg = llm.invoke([
        SystemMessage(content=NEWS_SYSTEM),
        HumanMessage(content=f"TICKER: {ticker}\nRAW_TEXT:\n{raw_text}\n\nSTEP 2 ONLY: return JSON now.")
    ])
    return {"messages": state["messages"] + [msg]}


def norm(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    s = s.replace("'", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\\'", "'")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_news_node(state: State):
    raw_text = extract_last_tool_text(state) or ""
    raw = state["messages"][-1].content

  
    clean = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

    try:
        news = json.loads(clean)
    except json.JSONDecodeError:
        
        news = {
            "key_news": [],
            "sentiment": "NEUTRAL",
            "notes": "JSON parsing failed — LLM output was malformed."
        }

    # Vérification que chaque evidence est bien présente dans le RAW_TEXT
    cleaned = []
    for item in news.get("key_news", []):
        ev = item.get("evidence", "")
        if ev and norm(ev) in norm(raw_text):
            cleaned.append(item)

    news["key_news"] = cleaned

    if not cleaned:
        news["sentiment"] = "NEUTRAL"
        news["notes"] = "No verifiable evidence found in RAW_TEXT."

    return {"news": news}


def decision_node(state: State):
    news_obj = NewsSummary(**state["news"])
    decision = decide_portfolio(state["tech"], news_obj, use_trend_filter=True)

    final_raw = {
        "news": state["news"],
        "step_by_step_check": decision["step_by_step_check"],
        "decision": decision["decision"],
        "reasoning": decision["reasoning"],
        "report_detail": decision["report_detail"],
    }

    final = finalSchema.model_validate(final_raw).model_dump()
    return {"final": final}


def route_after_news_llm(state: State):
    last_message = state["messages"][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return "parse_news"


def make_agent():
    graph = StateGraph(State)
    graph.add_node("get_tech", get_tech_node)
    graph.add_node("news_llm", news_llm_node)
    graph.add_node("tools", ToolNode([search_duck]))
    graph.add_node("parse_news", parse_news_node)
    graph.add_node("decision", decision_node)

    graph.add_edge(START, "get_tech")
    graph.add_edge("get_tech", "news_llm")
    graph.add_conditional_edges("news_llm", route_after_news_llm)
    graph.add_edge("tools", "news_llm")
    graph.add_edge("parse_news", "decision")
    graph.add_edge("decision", END)

    return graph.compile()
