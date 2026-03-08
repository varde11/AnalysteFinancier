from langchain_groq import ChatGroq

from tools.technical_indicator import decide_portfolio,get_technical_indicators
from tools.search import search_duck
from schema import State,NewsSummary
import os
import re
from dotenv import load_dotenv
load_dotenv()


from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage,ToolMessage,AIMessage
from pydantic import BaseModel
import json


NEWS_SYSTEM = """You are a Senior Financial News Researcher.

You will work in TWO STEPS:
STEP 1: Call the DuckDuckGo search tool to get RAW_TEXT.
STEP 2: Extract news ONLY from RAW_TEXT and output JSON.

STRICT RULES FOR STEP 2:
- Only use facts explicitly present in RAW_TEXT.
- Each item MUST include 'evidence' copied EXACTLY from RAW_TEXT.
- If you cannot copy evidence from RAW_TEXT, do not include the claim.

Output ONLY JSON:
{
  "sentiment": "POSITIVE|NEGATIVE|NEUTRAL",
  "key_news": [{"claim": "...", "evidence": "...", "confidence": "HIGH|MEDIUM|LOW"}],
  "notes": null
}
"""



llm_groq = ChatGroq(api_key=os.getenv("myfirstApiKey"),model="qwen/qwen3-32b",temperature=0)
llm = llm_groq.bind_tools([search_duck])


sys_news = SystemMessage(content=NEWS_SYSTEM)


def build_query(ticker: str) -> str:
    return  f'{ticker} (earnings OR "price target" OR upgrade OR downgrade OR antitrust OR regulatory) (site:reuters.com OR site:bloomberg.com OR site:wsj.com OR site:cnbc.com OR site:finance.yahoo.com) last 7 days'

def get_tech_node(state:State):
    
    ticker = state["messages"]
    if isinstance(ticker, list) and len(ticker) > 0:
        ticker = ticker[0]
    
    if hasattr(ticker, 'content'):  # It's a BaseMessage
        ticker = ticker.content
        
    ticker = str(ticker).strip().upper()
    
    #print(f"Fetching technical indicators for: {ticker}")
    tech_result = get_technical_indicators(ticker)
    
    return {"tech": tech_result}

def extract_last_tool_text(state):
    for m in reversed(state["messages"]):
        if isinstance(m, ToolMessage):
            # DuckDuckGoSearchRun name varie selon versions : on prend le dernier ToolMessage
            return str(m.content)
    return None




def news_llm_node(state: State):
    ticker = state["tech"]["ticker"] 
    print("new_llms:",ticker) # idéalement tu le stockes dans state, sinon extrait dernier HumanMessage
    raw_text = extract_last_tool_text(state)

    if raw_text is None:
        # STEP 1: tool call only
        query = build_query(ticker)
        msg = llm.invoke([
            SystemMessage(content=NEWS_SYSTEM),
            HumanMessage(content=f"STEP 1 ONLY: use the search tool now. Query: {query}")
        ])
        return {"messages": state["messages"] + [msg]}

    # STEP 2: extraction strict JSON
    msg = llm.invoke([
        SystemMessage(content=NEWS_SYSTEM),
        HumanMessage(content=f"TICKER: {ticker}\nRAW_TEXT:\n{raw_text}\n\nSTEP 2 ONLY: return JSON now.")
    ])
    return {"messages": state["messages"] + [msg]}



def norm(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    # normalise apostrophes et guillemets
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    s = s.replace("\\'", "'")  # parfois l'evidence contient des échappements
    # compresse les espaces
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_news_node(state: State):
    raw_text = extract_last_tool_text(state) or ""
    raw = state["messages"][-1].content
    news = json.loads(raw)

    cleaned = []
    for item in news.get("key_news", []):
        ev = item.get("evidence", "")
        if ev and norm(ev) in norm(raw_text):
            cleaned.append(item)

    news["key_news"] = cleaned

    if not cleaned:
        news["sentiment"] = "NEUTRAL"
        news["notes"] = "No verifiable evidence found in RAW_TEXT (tool output too noisy or irrelevant)."

    return {"news": news}

# def news_llm_node(state: State):
#     # LLM + tool search_duck (bind_tools)
#     msg = llm.invoke([sys_news] + state["messages"])
   
#     return {"messages": state["messages"] + [msg]}

# def parse_news_node(state:State):
#     # Ici, on parse le dernier message LLM en dict
#     # Si besoin, tu peux être plus robuste (try/except + fallback)
#     raw = state["messages"][-1].content
#     news_dict = json.loads(raw)
#     return {"news": news_dict}


def decision_node(state: State):
    news_obj = NewsSummary(**state["news"])
    decision = decide_portfolio(state["tech"], news_obj, use_trend_filter=True)
    final = [state["news"], decision]
    return {"final": final}



def route_after_news_llm(state: State):
    last_message = state["messages"][-1]
    
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    else:
        return "parse_news"


graph = StateGraph(State)
graph.add_node("get_tech",get_tech_node)
graph.add_node("news_llm", news_llm_node)
graph.add_node("tools", ToolNode([search_duck]))
graph.add_node("parse_news", parse_news_node)
graph.add_node("decision", decision_node)

graph.add_edge(START,"get_tech")
graph.add_edge("get_tech", "news_llm")
graph.add_conditional_edges("news_llm", route_after_news_llm)  
graph.add_edge("tools", "news_llm")  

# quand le LLM a produit son JSON news (sans tool call), on parse puis on décide
#graph.add_edge("news_llm","parse_news")
graph.add_edge("parse_news", "decision")
graph.add_edge("decision", END)

agent = graph.compile()
# Use a HumanMessage to properly format the input
from langchain_core.messages import HumanMessage

query = 'MSFT'

events = agent.stream(
    {"messages": [HumanMessage(content=query)]},
    stream_mode="values"
)

# for event in events:
#    event["messages"][-1].pretty_print()

for event in events:
    msg = event["messages"] if "messages" in event and event["messages"] else None
    tch = event["tech"] if "tech" in event and event["tech"] else None
    nw = event["news"] if "news" in event and event["news"] else None
    fl = event["final"] if "final" in event and event["final"] else None
        
print("messages:",msg)
print("-----------------")
print("-----------------")
print("tech:",tch)
print("-----------------")
print("-----------------")
print("nw:",nw)
print("-----------------")
print("-----------------")
print("final:",fl)































# NEWS_SYSTEM = """You are a Senior Financial News Researcher.
# Find the most relevant news for the given stock ticker from the LAST 7 DAYS.

# Focus on: Earnings, Analyst rating changes, Product launches, Regulatory issues, Macro sector news.
# Ignore: gossip, memes, minor fluctuations.

# Create ONLY valid JSON matching this schema:
 
#   "sentiment": "POSITIVE|NEGATIVE|NEUTRAL",
#   "key_news": ["...", "..."]


# Next, you will use the `decide_portfolio` function, with the parameters `tech = {tech}`, `news = json_new` and `use_trend_filter = True`.
# Return ONLY the function output provide by decide_portfolio, here's its schema:
#  "step_by_step_check": step,
#  "decision": BUY|SELL|HOLD,
#  "reasoning": reasoning

# Combine all elements you have created into a list and return it as the final output

# """
# llm_groq = ChatGroq(api_key=os.getenv("myfirstApiKey"),model="qwen/qwen3-32b",temperature=0)
# llm = llm_groq.bind_tools([decide_portfolio,search_duck])

# template = ChatPromptTemplate.from_messages([
#     ("system", NEWS_SYSTEM),
#     ("human", "Return List only.")
# ])
# #tech = get_technical_indicators('TSLA')
# # prompt = template.invoke({"tech":tech})

# tech = {}
# def llm_node(state:State):
    
#     prompt = template.invoke({"tech":tech})
#     return {"messages": llm.invoke(prompt.to_messages() + state["messages"])}

# def make_agent(tech_value:dict):
    
#     global tech
#     tech = tech_value
#     tools_node = ToolNode([decide_portfolio,search_duck])
#     graph = StateGraph(State)

#     graph.add_node("llm_node", llm_node)
#     graph.add_node("tools", tools_node)

#     graph.add_edge(START,"llm_node")
#     graph.add_conditional_edges("llm_node",tools_condition)
#     graph.add_edge("tools","llm_node")

#     return graph



# query ="Perform the system's instruction"
#agent = graph.compile()
# events = agent.stream(
#     {"messages":["users",query]},
#     stream_mode="values"
# )

# for event in events:
#     event["messages"][-1].pretty_print()













# sys1 = SystemMessage(content="""You must strictly provide the dictionary that the function returns,adds nothing more.""")
# sys2 =SystemMessage(content = """You are a Senior Financial News Researcher.
# Your goal is to find the most relevant news for a given stock ticker from the LAST 7 DAYS.

# GUIDELINES:
# 1. Search specifically for: Earnings reports, Analyst upgrades/downgrades, Product launches, Regulatory issues, or Macro-economic news affecting the sector.
# 2. IGNORE: Gossip, memes, or minor daily fluctuations.
# 3. SYNTHESIZE: Do not just list links. Group the information to determine the general sentiment.

# OUTPUT FORMAT in JSON format:
# Return a concise summary of the key events and explicitly state the sentiment:
# - SENTIMENT: [POSITIVE / NEGATIVE / NEUTRAL]
# - KEY NEWS: [Bullet points of main events]
# """)

# llm_groq1 = ChatGroq(api_key=os.getenv("myfirstApiKey"),model="qwen/qwen3-32b",temperature=0)
# llm_analyst = llm_groq1.bind_tools([get_technical_indicators])
# llm_news = llm_groq1.bind_tools([search_duck])


# def analyst(state:State):
#     return {"messages":llm_analyst.invoke([sys1]+state["messages"])}

# def news(state: State):
#     return {"messages":llm_news.invoke([sys2]+state["messages"])}

# def make_agent():

#     tool_node_analyst = ToolNode([get_technical_indicators])
#     graph_analyst = StateGraph(State)

#     graph_analyst.add_node("analyst",analyst)
#     graph_analyst.add_node("tools",tool_node_analyst)

#     graph_analyst.add_edge(START,"analyst")
#     graph_analyst.add_conditional_edges("analyst",tools_condition)
#     graph_analyst.add_edge("tools","analyst")
#     #graph_analyst.add_edge(END,"analyst")


#     tool_node_news = ToolNode([search_duck])
#     graph_news = StateGraph(State)

#     graph_news.add_node("news",news)
#     graph_news.add_node("tools",tool_node_news)

#     graph_news.add_edge(START,"news")
#     graph_news.add_conditional_edges("news",tools_condition)
#     graph_news.add_edge("tools","news")
#     #graph_news.add_edge(END,"news")

#     return {"graph_analyst":graph_analyst,"graph_news":graph_news}


# result = make_agent()
# agent1 = result["graph_news"].compile()

# r=agent1.invoke({"messages":"TESLA"})
# print(r["messages"][-1].content)
# print("----------------------------------------")
# print("-------------------------------------------")
# agent2 = result["graph_analyst"].compile()

# r=agent2.invoke({"messages":"TESLA"})
# print(r["messages"][-1].content)










# print(agent_croq)

# result = agent_croq.invoke({"messages":"Donne moi les indicateur technique pour TSLA"})

# print(result["messages"][-1].content)







