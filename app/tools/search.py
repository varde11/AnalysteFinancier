from langchain_community.tools import DuckDuckGoSearchRun

search_duck = DuckDuckGoSearchRun(description="This is a tool to search the web for news")

#print(search_duck.invoke("""TESLA (earnings OR "price target" OR upgrade OR downgrade OR regulatory OR antitrust OR "product launch" OR AI) last 7 days"""))


