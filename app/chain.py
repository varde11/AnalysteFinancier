from langchain_core.runnables import RunnableLambda,RunnableParallel
from agents import make_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import json
from dotenv import load_dotenv
from tools.technical_indicator import get_technical_indicators

tech = get_technical_indicators('NVDA')

graph = make_agent(tech)

query ="Perform the system's instruction"
agent = graph.compile()


events = agent.stream(
    {"messages":["users",query]},
    stream_mode="values"
)

for event in events:
    last_message = event["messages"][-1]
    #event["messages"][-1].pretty_print()

print("-----------------------------------")
print("--------------------------------------")
print(last_message.content)

# print("-----------------------------------")
# print("--------------------------------------")

# le = [{"sentiment": "POSITIVE", "key_news": ["Tesla beats Wall Street's earnings estimates, driving after-hours stock gains", "Scheduled analyst call to discuss financial results and future strategy", "Vehicle deliveries declined again, raising concerns about growth momentum", "Analysts highlight upcoming catalysts: autonomous vehicle expansion, regulatory approvals for self-driving tech, and AI product rollouts"]}, {"step_by_step_check": "1. Technical analysis shows bullish trend (SMA 50 > 200) with RSI in neutral territory. 2. Positive earnings surprise and strong after-hours reaction indicate short-term momentum. 3. Analysts identify key growth catalysts in autonomous tech and AI products. 4. Delivery concerns partially offset by regulatory and product development progress.", "decision": "BUY", "reasoning": "Bullish technical indicators align with positive earnings surprise and multiple growth catalysts on the horizon. While delivery declines are concerning, the stock's strong technical position and analyst-driven catalysts suggest a buying opportunity with trend-following validation."}]
# print(le[0])

# print("-----------------------------------")
# print("--------------------------------------")

#print(last_message.content)
# myson=json.loads(last_message)

# print(type(myson))
# print(myson)













# def parseoutput(input:dict):
    
#     try :
#         analyst_expert = input["branches"]["analyst"]["messages"][-1].content
#         news_expert = input["branches"]["news"]["messages"][-1].content

#     except ValueError as e :
#         print(f"Erreur dans les dictionnaire: {e}")
   
#     return {"analyst_expert":analyst_expert,"news_expert":news_expert}


# parseoutput_runnable = RunnableLambda(parseoutput)
# decision_prompt = ChatPromptTemplate.from_template("""
# Tu es un Gestionnaire de Portefeuille Senior algorithmique.
# Ta mission est d'appliquer STRICTEMENT des règles mathématiques. Tu n'as pas le droit d'interpréter les chiffres, tu dois les comparer.

# --- RAPPORT TECHNIQUE ---
# {analyst_expert}

# --- RAPPORT NEWS ---
# {news_expert}

# --- RÈGLES DE DÉCISION (NON NÉGOCIABLES) ---
# A. ACHAT (BUY) : SI (RSI < 30) ET (Sentiment == POSITIF)
# B. VENTE (SELL) : SI (RSI > 70) ET (Sentiment == NÉGATIF)
# C. ATTENTE (HOLD) : Dans tous les autres cas (RSI entre 30 et 70, ou signaux contradictoires).

# --- TA MÉTHODE DE RÉFLEXION ---
# Avant de décider, tu dois faire ce check exact :
# 1. Quelle est la valeur exacte du RSI ?
# 2. Est-ce que ce RSI est strictement inférieur à 30 ? (OUI/NON)
# 3. Est-ce que ce RSI est strictement supérieur à 70 ? (OUI/NON)
# 4. Quel est le sentiment des news ? (POSITIF/NÉGATIF/NEUTRE)
# 5. Application de la règle A, B ou C.

# DÉCISION FINALE (JSON) :
# {{
#   "step_by_step_check": "RSI=43 (Non < 30), Sentiment=Positif -> Règle C s'applique",
#   "decision": "BUY/SELL/HOLD",
#   "reasoning": "Explication basée sur le respect strict des seuils."
# }}
# """)
# load_dotenv()
# llm_decision = ChatGroq(api_key=os.getenv("myfirstApiKey"),model="llama-3.3-70b-versatile", temperature=0)
# str_parse = StrOutputParser()
# def make_chain():

#     agents = make_agent()
#     agent_news = agents["graph_news"].compile()
#     agent_analyst = agents["graph_analyst"].compile()

#     chain = RunnableParallel(branches={"analyst":agent_analyst,"news":agent_news}) | parseoutput_runnable | decision_prompt | llm_decision | str_parse

#     return chain

# chain = make_chain()
# result = chain.invoke({"messages":[("user","Nvidia")]})
# print(result)
    




#r["messages"][-1].content)

# test={'analyst': {'messages': [HumanMessage(content='TESLA', additional_kwargs={}, response_metadata={}, id='589ecd50-ffcd-48f2-89e3-ffd871253b38'), AIMessage(content='', additional_kwargs={'reasoning_content': 'Okay, the user mentioned "TESLA," so I need to figure out what they\'re looking for. Since there\'s a function called get_technical_indicators that fetches stock data, I should check if they want information on Tesla\'s stock. The function requires a ticker symbol. Tesla\'s ticker is TSLA. The user might not know the ticker and used "TESLA" instead. I should use the function with the correct ticker TSLA. Let me call the function with TSLA as the argument.\n', 'tool_calls': [{'id': '8eptxbvgh', 'function': {'arguments': '{"ticker":"TSLA"}', 'name': 'get_technical_indicators'}, 'type': 'function'}]}, response_metadata={'token_usage': {'completion_tokens': 137, 'prompt_tokens': 215, 'total_tokens': 352, 'completion_time': 0.26130028, 'completion_tokens_details': {'reasoning_tokens': 107}, 'prompt_time': 0.009819958, 'prompt_tokens_details': None, 'queue_time': 0.091355366, 'total_time': 0.271120238}, 'model_name': 'qwen/qwen3-32b', 'system_fingerprint': 'fp_5cf921caa2', 'service_tier': 'on_demand', 'finish_reason': 'tool_calls', 'logprobs': None, 'model_provider': 'groq'}, id='lc_run--019c09e0-c98a-7bc3-848c-d77bc31ad370-0', tool_calls=[{'name': 'get_technical_indicators', 'args': {'ticker': 'TSLA'}, 'id': '8eptxbvgh', 'type': 'tool_call'}], invalid_tool_calls=[], usage_metadata={'input_tokens': 215, 'output_tokens': 137, 'total_tokens': 352, 'output_token_details': {'reasoning': 107}}), ToolMessage(content='{"Technical_Analysis_for": "TSLA", "Current_Price": "$431.46", "RSI_14": "50.03", "SMA_50": "$442.90", "SMA_200": "$375.51", "Trend": "Bearish (Price vs SMA50)"}', name='get_technical_indicators', id='4c94976a-8eee-4f0d-8b67-746427ab26f5', tool_call_id='8eptxbvgh'), AIMessage(content='```json\n{\n  "TSLA_Technical_Analysis": {\n    "Current_Price": "$431.46",\n    "RSI_14": "50.03 (Neutral)",\n    "SMA_50": "$442.90",\n    "SMA_200": "$375.51",\n    "Trend": "Bearish (Price below SMA 50)"\n  }\n}\n```', additional_kwargs={'reasoning_content': "Okay, let's see. The user asked for TESLA's technical indicators. I called the function with the ticker TSLA. The response came back with the current price, RSI, SMA 50 and 200, and the trend. Now I need to present this information clearly.\n\nFirst, I'll start by stating the current price. Then list the RSI and SMAs. The trend is bearish compared to SMA 50. I should explain what that means in simple terms. Maybe mention that RSI is around 50, which is neutral. The SMA 50 is higher than the current price, indicating a bearish trend. Also, the SMA 200 is even lower. I should make sure the user understands the implications of these values. Keep it concise but informative.\n"}, response_metadata={'token_usage': {'completion_tokens': 274, 'prompt_tokens': 336, 'total_tokens': 610, 'completion_time': 0.48040119, 'completion_tokens_details': {'reasoning_tokens': 169}, 'prompt_time': 0.014770246, 'prompt_tokens_details': None, 'queue_time': 0.090039665, 'total_time': 0.495171436}, 'model_name': 'qwen/qwen3-32b', 'system_fingerprint': 'fp_5cf921caa2', 'service_tier': 'on_demand', 'finish_reason': 'stop', 'logprobs': None, 'model_provider': 'groq'}, id='lc_run--019c09e0-d013-7483-839a-08515eaeed87-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 336, 'output_tokens': 274, 'total_tokens': 610, 'output_token_details': {'reasoning': 169}})]}, 'news': {'messages': [HumanMessage(content='TESLA', additional_kwargs={}, response_metadata={}, id='0b775a60-8114-4349-a40d-26268afdaf2e'), AIMessage(content='', additional_kwargs={'reasoning_content': 'Okay, I need to find the most relevant news for Tesla from the last 7 days. Let me start by recalling the guidelines. The user wants earnings reports, analyst upgrades/downgrades, product launches, regulatory issues, or macroeconomic news affecting the sector. I should ignore gossip, memes, or minor fluctuations. Also, I need to synthesize the information and determine the overall sentiment.\n\nFirst, I\'ll use the duckduckgo_search function to look up recent Tesla news. The query should be specific. Let me think of the right keywords. Maybe "Tesla news last 7 days earnings analyst product regulatory". That should cover the main areas. I\'ll use the function with that query.\n\nAfter getting the search results, I\'ll go through each link to see what\'s relevant. Let\'s say the search returns articles about Q2 earnings, an analyst upgrade from Goldman Sachs, a new product launch like the Cybertruck, and a regulatory issue in Europe. I need to check each of these.\n\nFor the earnings report, if Tesla beat expectations, that\'s positive. The analyst upgrade would be positive too. The Cybertruck launch is a product launch, which is positive. The regulatory issue might be negative if it\'s a fine or restriction. But I need to check the details. If the regulatory issue is just a routine inspection, maybe it\'s neutral. Also, look for macroeconomic factors, like interest rates affecting the auto sector.\n\nWait, the user mentioned macroeconomic news affecting the sector. If there\'s news about interest rates or supply chain issues that impact the auto industry, that\'s relevant. Let me see if any of the search results mention that.\n\nOnce I have all the relevant points, I need to group them and assess the sentiment. If there are three positive points and one neutral, the overall sentiment would be positive. If there\'s a mix of positive and negative, I need to weigh them. For example, a strong earnings report and an analyst upgrade would be positive, while a regulatory issue might be negative. But if the regulatory issue isn\'t too severe, maybe it\'s neutral.\n\nI should also check the dates to ensure all news is within the last 7 days. Let me make sure each article is from that timeframe. If an article is older, I should exclude it.\n\nPutting it all together, the key news points would be the earnings report, analyst upgrade, product launch, and regulatory issue. The sentiment would depend on the balance between positive and negative news. If the positives outweigh the negatives, the sentiment is positive. If there\'s a significant negative, it might be negative. Otherwise, neutral.\n', 'tool_calls': [{'id': '46kbcf6jb', 'function': {'arguments': '{"query":"Tesla recent news last 7 days earnings analyst upgrades product launches regulatory issues"}', 'name': 'duckduckgo_search'}, 'type': 'function'}]}, response_metadata={'token_usage': {'completion_tokens': 567, 'prompt_tokens': 306, 'total_tokens': 873, 'completion_time': 1.150463023, 'completion_tokens_details': {'reasoning_tokens': 528}, 'prompt_time': 0.013241581, 'prompt_tokens_details': None, 'queue_time': 0.090730325, 'total_time': 1.163704604}, 'model_name': 'qwen/qwen3-32b', 'system_fingerprint': 'fp_5cf921caa2', 'service_tier': 'on_demand', 'finish_reason': 'tool_calls', 'logprobs': None, 'model_provider': 'groq'}, id='lc_run--019c09e0-c98b-7411-9fd8-3f092c71abbd-0', tool_calls=[{'name': 'duckduckgo_search', 'args': {'query': 'Tesla recent news last 7 days earnings analyst upgrades product launches regulatory issues'}, 'id': '46kbcf6jb', 'type': 'tool_call'}], invalid_tool_calls=[], usage_metadata={'input_tokens': 306, 'output_tokens': 567, 'total_tokens': 873, 'output_token_details': {'reasoning': 528}}), ToolMessage(content='Tuesday, Tesla announced their profits plummeted 70%, missing analyst expectations in revenue and earnings per share. So it ’ s fair to ask: will recent regulatory changes threaten Tesla ’ s earnings outlook? In short, we think the answer is no, at least ... ... will try to argue that it’s a one-time thing, and the issue will be, is that really the case? Will the SEC come forward with evidence from Tesla ... ... policies, a persistent question has followed Tesla : when is this multi-billion-dollar revenue stream going to dry up? Before the Q2 2025 Earnings ... Tesla remains optimistic about its future, with plans to launch its Robotaxi in Austin in June and ongoing development of its Optimus humanoid robot.', name='duckduckgo_search', id='714383d7-3a77-47b4-85b8-aaaf74878525', tool_call_id='46kbcf6jb'), AIMessage(content='- SENTIMENT: NEGATIVE  \n- KEY NEWS:  \n  - Tesla reported a **70% profit decline** in Q2 2025, missing both revenue and earnings per share expectations.  \n  - Regulatory uncertainty persists as questions arise about potential SEC investigations into Tesla’s policies, though analysts argue this may not immediately threaten earnings.  \n  - The company remains optimistic about future growth, planning to launch its **Robotaxi in Austin (June 2025)** and continuing development of the **Optimus humanoid robot**.  \n  - Analysts debate whether the earnings slump is a one-time issue or a sign of long-term challenges for Tesla’s revenue sustainability.', additional_kwargs={'reasoning_content': 'Okay, let\'s break down the user\'s query. They want the most relevant news about Tesla from the last 7 days, focusing on earnings, analyst changes, product launches, regulatory issues, or macroeconomic factors. The guidelines say to ignore minor stuff and synthesize the info.\n\nFirst, I need to check the tool response. The search result mentions Tesla\'s profits dropped 70%, missing earnings and revenue expectations. That\'s a key earnings report point. The user also mentioned regulatory changes possibly affecting earnings, but the response says the answer is "no" for now. However, there\'s a mention of the SEC possibly investigating, which is a regulatory issue. Then there\'s the Robotaxi launch in June and Optimus robot development as product news.\n\nSo, the key points are the earnings miss, the regulatory question about SEC, and the product launches. The sentiment here seems negative because of the profit drop and missing expectations. But Tesla is optimistic about future products. Need to balance that. The regulatory part is a potential risk but not confirmed yet. \n\nGrouping the info: Earnings down, regulatory uncertainty, upcoming products. The sentiment is negative due to the earnings report, but there\'s some positive future outlook. However, the main focus is on the recent negative earnings and regulatory concerns. So overall sentiment is negative. The key news points should list the earnings miss, regulatory questions, and product plans.\n'}, response_metadata={'token_usage': {'completion_tokens': 429, 'prompt_tokens': 506, 'total_tokens': 935, 'completion_time': 0.96994393, 'completion_tokens_details': {'reasoning_tokens': 285}, 'prompt_time': 0.026358214, 'prompt_tokens_details': None, 'queue_time': 0.09438129, 'total_time': 0.996302144}, 'model_name': 'qwen/qwen3-32b', 'system_fingerprint': 'fp_5cf921caa2', 'service_tier': 'on_demand', 'finish_reason': 'stop', 'logprobs': None, 'model_provider': 'groq'}, id='lc_run--019c09e0-d8e1-7290-a97f-f69979c0e03a-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 506, 'output_tokens': 429, 'total_tokens': 935, 'output_token_details': {'reasoning': 285}})]}}

# print(parseoutput(test))

# test = """{'analyst_expert': '```json\n{\n  "TSLA_Technical_Analysis": {\n    "Current_Price": "$431.46",\n    "RSI_14": "50.03 (Neutral)",\n    "SMA_50": "$442.90 (Price below SMA50 - Bearish)",\n    "SMA_200": "$375.51 (Long-term support level)",\n    "Trend": "Bearish (Price < SMA50) with oversold conditions unlikely (RSI near 50)"\n  }\n}\n```', 'news_expert': '- SENTIMENT: NEGATIVE  \n- KEY NEWS:  \n  - **Earnings Disappointment**: Tesla reported a 16% decline in Q4 2025 deliveries and a 5.5% drop in production compared to the same period last year, missing lowered internal benchmarks.  \n  - **Regulatory Hurdles**: Full approval for Tesla’s autonomous driving technology in California may be delayed until 2027, raising concerns about growth projections.  \n  - **Product Progress**: First-generation production lines for the Optimus robot are being installed, signaling progress toward volume production.  \n\nThe earnings shortfall and regulatory delays outweigh the positive product development, leading to an overall negative sentiment.'}"""
# test = repair_json(test)

# print(json.loads(test))