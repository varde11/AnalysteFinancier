# from langchain_groq import ChatGroq

# from tools.technical_indicator import decide_portfolio,get_technical_indicators
# from tools.search import search_duck
# from schema import State,NewsSummary
# import os
# from dotenv import load_dotenv
# load_dotenv()


# from langgraph.graph import StateGraph, START, END
# from langgraph.prebuilt import ToolNode, tools_condition
# from langchain_core.messages import SystemMessage
# from pydantic import BaseModel
# import json
# NEWS_SYSTEM = """You are a Senior Financial News Researcher.
# Find the most relevant news for the given stock ticker from the LAST 7 DAYS.

# Focus on: Earnings, Analyst rating changes, Product launches, Regulatory issues, Macro sector news.
# Ignore: gossip, memes, minor fluctuations.

# Return ONLY valid JSON:
# {
#   "sentiment": "POSITIVE|NEGATIVE|NEUTRAL",
#   "key_news": ["...", "..."]
# }
# """

# llm_groq = ChatGroq(api_key=os.getenv("myfirstApiKey"),model="qwen/qwen3-32b",temperature=0)
# llm = llm_groq.bind_tools([search_duck])

# # suppose que tu as NewsSummary et decide_portfolio importés

# sys_news = SystemMessage(content=NEWS_SYSTEM)

# def get_tech_node(state:State):
#     # Extract ticker from messages (state["messages"] should be a list of BaseMessages)
#     # If it's a string, use it directly; if it's a message, get the content
#     ticker = state["messages"]
#     if isinstance(ticker, list) and len(ticker) > 0:
#         ticker = ticker[0]
#     if hasattr(ticker, 'content'):  # It's a BaseMessage
#         ticker = ticker.content
#     ticker = str(ticker).strip().upper()
    
#     print(f"Fetching technical indicators for: {ticker}")
#     tech_result = get_technical_indicators(ticker)
#     print("tech", tech_result)
#     return {"tech": tech_result}

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


# def decision_node(state: State):
#     news_obj = NewsSummary(**state["news"])
#     decision = decide_portfolio(state["tech"], news_obj, use_trend_filter=True)
#     final = [state["news"], decision]
#     return {"final": final}



# def route_after_news_llm(state: State):
#     """Route to tools if there's a tool_call, otherwise to parse_news"""
#     last_message = state["messages"][-1]
    
#     if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
#         return "tools"
#     else:
#         return "parse_news"


# graph = StateGraph(State)
# graph.add_node("get_tech",get_tech_node)
# graph.add_node("news_llm", news_llm_node)
# graph.add_node("tools", ToolNode([search_duck]))
# graph.add_node("parse_news", parse_news_node)
# graph.add_node("decision", decision_node)

# graph.add_edge(START,"get_tech")
# graph.add_edge("get_tech", "news_llm")
# graph.add_conditional_edges("news_llm", route_after_news_llm)  
# graph.add_edge("tools", "news_llm")  

# # quand le LLM a produit son JSON news (sans tool call), on parse puis on décide
# graph.add_edge("news_llm","parse_news")
# graph.add_edge("parse_news", "decision")
# graph.add_edge("decision", END)

# agent = graph.compile()
# # Use a HumanMessage to properly format the input
# from langchain_core.messages import HumanMessage

# query = 'NVDA'

# events = agent.stream(
#     {"messages": [HumanMessage(content=query)]},
#     stream_mode="values"
# )

# for event in events:
#     print("--- EVENT keys:", list(event.keys()))
#     if "messages" in event and event["messages"]:
#         try:
#             event["messages"][-1].pretty_print()
#         except Exception:
#             print("LAST MESSAGE:", event["messages"][-1])
#     if "tech" in event:
#         print("TECH:", event["tech"])
#     if "news" in event:
#         print("NEWS:", event["news"])
#     if "final" in event:
#         print("FINAL:", event["final"])
