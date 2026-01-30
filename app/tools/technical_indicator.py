import yfinance as yf
import pandas as pd
from langchain_core.tools import tool
from typing import Dict,List,Literal
from pydantic import BaseModel,Field


class NewsSummary(BaseModel):
    sentiment: Literal["POSITIVE", "NEGATIVE", "NEUTRAL"] = Field(...)
    key_news: List[str] = Field(default_factory=list)


def rsi_wilder(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/window, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi



def get_technical_indicators(ticker: str) -> dict:
    """
    Deterministic technical indicators from yfinance (daily close).
    Returns floats (no "$", no text tags).
    """
    # Handle case where ticker comes as a list from LLM tool calls
    if isinstance(ticker, list):
        ticker = ticker[0]
    
    # Ensure ticker is a string
    ticker = str(ticker).upper()
    
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y", interval="1d", auto_adjust=False)

    if df is None or df.empty:
        return {"error": f"No data found for ticker {ticker}."}

    close = df["Close"].dropna()

    # Option stabilité: on ignore la dernière bougie si tu suspectes qu'elle bouge intraday
    # (simple: on la retire toujours; tu peux commenter si tu veux)
    if len(close) > 250:
        close = close.iloc[:-1]

    sma_50 = close.rolling(50).mean().iloc[-1]
    sma_200 = close.rolling(200).mean().iloc[-1]

    rsi_series = rsi_wilder(close, 14)
    rsi_14 = float(rsi_series.iloc[-1])

    current_price = float(close.iloc[-1])

    trend_sma = "Bullish" if sma_50 > sma_200 else "Bearish"

    return {
        "ticker": ticker,
        "current_price": round(current_price,3),
        "rsi_14": round(rsi_14,3),
        "sma_50": round(float(sma_50),3),
        "sma_200": round(float(sma_200),3),
        "trend_sma": trend_sma,  # basé SMA50 vs SMA200 (plus cohérent que price vs SMA50)
    }



def decide_portfolio(tech: Dict, news: NewsSummary, use_trend_filter: bool = True) -> Dict:
    """
    Docstring for decide_portfolio
    
    :param tech:
    :type tech: Dict
    :param news: 
    :type news: NewsSummary
    :param use_trend_filter: 
    :type use_trend_filter: bool
    :return: 
    :rtype: Dict | JSON
    """
    
    rsi = float(tech["rsi_14"])
    sentiment = news.sentiment

    sma50 = float(tech["sma_50"])
    sma200 = float(tech["sma_200"])
    trend_ok_buy = sma50 > sma200
    trend_ok_sell = sma50 < sma200

    cond_rsi_buy = rsi < 30
    cond_rsi_sell = rsi > 70
    cond_sent_buy = sentiment == "POSITIVE"
    cond_sent_sell = sentiment == "NEGATIVE"

    # Règle simple (originale)
    simple_buy = cond_rsi_buy and cond_sent_buy
    simple_sell = cond_rsi_sell and cond_sent_sell

    # Règle filtrée (utilise SMA50/SMA200 comme confirmation)
    buy = simple_buy and (trend_ok_buy if use_trend_filter else True)
    sell = simple_sell and (trend_ok_sell if use_trend_filter else True)

    if buy:
        decision = "BUY"
        rule = "A(+TrendFilter)" if use_trend_filter else "A"
    elif sell:
        decision = "SELL"
        rule = "B(+TrendFilter)" if use_trend_filter else "B"
    else:
        decision = "HOLD"
        rule = "C"

    step = (
        f"RSI={rsi:.2f} | (<30? {'OUI' if cond_rsi_buy else 'NON'}) "
        f"(>70? {'OUI' if cond_rsi_sell else 'NON'}) | "
        f"Sentiment={sentiment} | "
        f"SMA50={sma50:.2f} vs SMA200={sma200:.2f} "
        f"(SMA50>SMA200? {'OUI' if trend_ok_buy else 'NON'}) "
        f"(SMA50<SMA200? {'OUI' if trend_ok_sell else 'NON'}) "
        f"-> Rule {rule}"
    )

    reasoning = (
        "Décision strictement déterministe basée sur comparaisons de seuils. "
        "RSI+Sentiment déclenchent BUY/SELL, et SMA50/SMA200 sert de confirmation mécanique "
        "pour éviter un signal RSI contre la tendance."
        if use_trend_filter else
        "Décision strictement déterministe basée uniquement sur RSI+Sentiment (règle simple)."
    )

    return {
        "step_by_step_check": step,
        "decision": decision,
        "reasoning": reasoning
    }













# import yfinance as yf
# from langchain_core.tools import tool

# @tool
# def get_technical_indicators(ticker: str):
#     """
#     Fetches historical stock data for the given ticker (e.g., 'AAPL', 'TSLA') 
#     and calculates technical indicators: Current Price, RSI (14), and SMA (50, 200).
#     Returns a summary string with the calculated values.
#     """
#     try:
#         # 1. Récupération des données (1 an d'historique pour avoir assez de data pour la SMA 200)
#         stock = yf.Ticker(ticker)
#         df = stock.history(period="1y")
        
#         if df.empty:
#             return f"Error: No data found for ticker {ticker}."

#         current_price = df['Close'].iloc[-1]

#         # 2. Calcul SMA (Moyenne Mobile Simple)
#         # On calcule la moyenne des 50 et 200 derniers jours
#         sma_50 = df['Close'].rolling(window=50).mean().iloc[-1]
#         sma_200 = df['Close'].rolling(window=200).mean().iloc[-1]

#         # 3. Calcul RSI (Relative Strength Index) - Formule standard
#         delta = df['Close'].diff()
#         gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
#         loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
#         rs = gain / loss
#         rsi = 100 - (100 / (1 + rs)).iloc[-1]

#         # 4. Formatage de la réponse pour le LLM
#         # On arrondit pour que ce soit lisible
#         return {
#             "Technical_Analysis_for": ticker,
#             "Current_Price": f"${current_price:.2f}",
#             "RSI_14": f"{rsi:.2f}",
#             "SMA_50": f"${sma_50:.2f}",
#             "SMA_200": f"${sma_200:.2f}",
#             "Trend" : f"{'Bullish' if current_price > sma_50 else 'Bearish'} (Price vs SMA50)"
#         }

#     except Exception as e:
#         return f"Error analyzing {ticker}: {str(e)}"

# #print(get_technical_indicators.invoke("TSLA"))
