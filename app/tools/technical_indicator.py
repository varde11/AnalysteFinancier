import yfinance as yf
import pandas as pd
from typing import Dict, List, Literal
from pydantic import BaseModel, Field
from typing import Optional


class KeyNewsItem(BaseModel):
    claim: str
    evidence: str
    confidence: Literal["HIGH", "MEDIUM", "LOW"]


class NewsSummary(BaseModel):
    sentiment: Literal["POSITIVE", "NEGATIVE", "NEUTRAL"]
    key_news: List[KeyNewsItem]
    notes: Optional[str] = None


# ─────────────────────────────────────────────
# RSI WILDER — inchangé, il était correct
# ─────────────────────────────────────────────

def rsi_wilder(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


# ─────────────────────────────────────────────
# INDICATEURS TECHNIQUES — inchangé
# ─────────────────────────────────────────────

def get_technical_indicators(ticker: str) -> dict:
    if isinstance(ticker, list):
        ticker = ticker[0]
    ticker = str(ticker).upper()

    stock = yf.Ticker(ticker)
    df = stock.history(period="1y", interval="1d", auto_adjust=False)

    if df is None or df.empty:
        return {"error": f"No data found for ticker {ticker}."}

    close = df["Close"].dropna()

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
        "current_price": round(current_price, 3),
        "rsi_14": round(rsi_14, 3),
        "sma_50": round(float(sma_50), 3),
        "sma_200": round(float(sma_200), 3),
        "trend_sma": trend_sma,
    }


# ─────────────────────────────────────────────
# SCORING RSI
# Retourne (points, label explicatif)
# ─────────────────────────────────────────────

def _score_rsi(rsi: float):
    if rsi < 30:
        return +2, f"RSI {rsi:.2f} < 30 → Survendue (signal achat fort)"
    elif rsi < 45:
        return +1, f"RSI {rsi:.2f} entre 30–45 → Légère sous-pression (signal achat faible)"
    elif rsi <= 55:
        return  0, f"RSI {rsi:.2f} entre 45–55 → Zone neutre"
    elif rsi <= 70:
        return -1, f"RSI {rsi:.2f} entre 55–70 → Légèrement surachetée (signal vente faible)"
    else:
        return -2, f"RSI {rsi:.2f} > 70 → Surachetée (signal vente fort)"


# ─────────────────────────────────────────────
# SCORING TENDANCE SMA
# On regarde : SMA50 vs SMA200 ET prix vs SMA50
# ─────────────────────────────────────────────

def _score_trend(price: float, sma50: float, sma200: float):
    golden_cross = sma50 > sma200                 # tendance longue haussière
    price_above_sma50 = price > sma50             # prix au-dessus de la moyenne court terme

    cross_label = "Golden Cross (SMA50 > SMA200)" if golden_cross else "Death Cross (SMA50 < SMA200)"
    price_label = f"Prix ({price:.2f}$) {'>' if price_above_sma50 else '<'} SMA50 ({sma50:.2f}$)"

    if golden_cross and price_above_sma50:
        return +2, f"{cross_label} & {price_label} → Tendance forte haussière"
    elif golden_cross and not price_above_sma50:
        return +1, f"{cross_label} & {price_label} → Dip dans tendance haussière (opportunité potentielle)"
    elif not golden_cross and price_above_sma50:
        return -1, f"{cross_label} & {price_label} → Rebond technique dans tendance baissière (méfiance)"
    else:
        return -2, f"{cross_label} & {price_label} → Tendance forte baissière"


# ─────────────────────────────────────────────
# SCORING SENTIMENT
# On exploite la confidence dominante des news
# ─────────────────────────────────────────────

def _dominant_confidence(key_news: List[KeyNewsItem]) -> str:
    """Retourne la confidence la plus fréquente parmi les news HIGH > MEDIUM > LOW."""
    if not key_news:
        return "LOW"
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for item in key_news:
        counts[item.confidence] += 1
    return max(counts, key=counts.get)


def _score_sentiment(news: NewsSummary):
    sentiment = news.sentiment
    confidence = _dominant_confidence(news.key_news)

    if sentiment == "POSITIVE" and confidence == "HIGH":
        return +2, f"Sentiment POSITIF avec confiance dominante HIGH"
    elif sentiment == "POSITIVE":
        return +1, f"Sentiment POSITIF avec confiance dominante {confidence}"
    elif sentiment == "NEUTRAL":
        return  0, f"Sentiment NEUTRE — pas de signal clair des news"
    elif sentiment == "NEGATIVE" and confidence == "HIGH":
        return -2, f"Sentiment NÉGATIF avec confiance dominante HIGH"
    else:
        return -1, f"Sentiment NÉGATIF avec confiance dominante {confidence}"


# ─────────────────────────────────────────────
# RÈGLE DE SÉCURITÉ (cas krach)
# Si NEGATIVE HIGH + Death Cross → malus supplémentaire
# pour forcer SELL sur un krach confirmé
# ─────────────────────────────────────────────

def _safety_malus(news: NewsSummary, sma50: float, sma200: float) -> tuple:
    if (news.sentiment == "NEGATIVE"
            and _dominant_confidence(news.key_news) == "HIGH"
            and sma50 < sma200):
        return -1, "Règle de sécurité : Sentiment NÉGATIF HIGH + Death Cross → malus -1"
    return 0, None


# ─────────────────────────────────────────────
# DECIDE PORTFOLIO — scoring + report_detail structuré
# report_detail est un dict JSON-friendly
# que React consommera directement
# ─────────────────────────────────────────────

def decide_portfolio(tech: Dict, news: NewsSummary, use_trend_filter: bool = True) -> Dict:
    rsi    = float(tech["rsi_14"])
    price  = float(tech["current_price"])
    sma50  = float(tech["sma_50"])
    sma200 = float(tech["sma_200"])
    ticker = tech["ticker"]

    # ── Calcul des scores ──
    score_rsi,   label_rsi   = _score_rsi(rsi)
    score_trend, label_trend = _score_trend(price, sma50, sma200)
    score_sent,  label_sent  = _score_sentiment(news)
    score_safe,  label_safe  = _safety_malus(news, sma50, sma200)

    total = score_rsi + score_trend + score_sent + score_safe

    # ── Décision ──
    if total >= 3:
        decision = "BUY"
    elif total <= -3:
        decision = "SELL"
    else:
        decision = "HOLD"

    # ── Explication en langage naturel ──
    if decision == "BUY":
        explanation = (
            f"Les signaux convergent en faveur d'un achat sur {ticker}. "
            f"{'L action est en zone de survente' if score_rsi > 0 else 'Le RSI est acceptable'}, "
            f"la tendance {'long terme est haussière' if sma50 > sma200 else 'montre un rebond potentiel'}. "
            f"Le sentiment des analystes {'renforce cette conviction' if score_sent > 0 else 'ne contredit pas ce signal'}. "
            f"Score total : {total:+d}/6."
        )
    elif decision == "SELL":
        explanation = (
            f"Les signaux convergent vers une sortie de position sur {ticker}. "
            f"{'L action est en zone de surachat' if score_rsi < 0 else 'Le RSI pèse négativement'}. "
            f"{'La tendance longue est baissière (Death Cross)' if sma50 < sma200 else 'La tendance récente se dégrade'}. "
            f"Le sentiment des analystes {'confirme la pression vendeuse' if score_sent < 0 else 'ne soutient pas le titre'}. "
            f"Score total : {total:+d}/6."
        )
    else:
        explanation = (
            f"Les signaux sont trop mixtes pour recommander une action claire sur {ticker}. "
            f"Certains indicateurs sont positifs, d autres négatifs — la prudence s impose. "
            f"Attendre une convergence plus nette des signaux avant d agir. "
            f"Score total : {total:+d}/6."
        )

    dominant_conf = _dominant_confidence(news.key_news)

    # ── report_detail : structure JSON consommable directement par React ──
    # Chaque bloc correspond à une section de l'UI
    report_detail = {
        "decision": decision,                    # "BUY" | "SELL" | "HOLD"
        "total_score": total,                    # int  ex: +3
        "max_score": 6,                          # référence pour la barre de progression
        "explanation": explanation,              # phrase lisible pour l'utilisateur

        # Bloc indicateurs techniques — section "📊" dans l'UI
        "technicals": {
            "ticker": ticker,
            "current_price": round(price, 2),
            "rsi": round(rsi, 2),
            "sma50": round(sma50, 2),
            "sma200": round(sma200, 2),
            "golden_cross": sma50 > sma200,      # bool → badge vert/rouge dans React
            "price_above_sma50": price > sma50,  # bool → indique momentum court terme
        },

        # Bloc sentiment — section "📰" dans l'UI
        "news_summary": {
            "sentiment": news.sentiment,
            "dominant_confidence": dominant_conf,
            "items": [
                {
                    "claim": item.claim,
                    "evidence": item.evidence,
                    "confidence": item.confidence,
                }
                for item in news.key_news
            ],
        },

        # Bloc scores détaillés — section "🧮" dans l'UI
        # score est un int signé, label est la phrase explicative
        # React peut colorer chaque ligne en vert (>0), rouge (<0), gris (=0)
        "score_breakdown": [
            {
                "signal": "RSI",
                "score": score_rsi,
                "label": label_rsi,
            },
            {
                "signal": "Tendance SMA",
                "score": score_trend,
                "label": label_trend,
            },
            {
                "signal": "Sentiment",
                "score": score_sent,
                "label": label_sent,
            },
            *(
                [{"signal": "Règle sécurité", "score": score_safe, "label": label_safe}]
                if label_safe else []
            ),
        ],
    }

    # step_by_step_check conservé pour compatibilité DB existante
    step = (
        f"RSI={rsi:.2f}({score_rsi:+d}) | "
        f"Trend SMA50/200={sma50:.2f}/{sma200:.2f}({score_trend:+d}) | "
        f"Sentiment={news.sentiment}/{dominant_conf}({score_sent:+d}) | "
        f"Safety={score_safe:+d} | Total={total:+d} -> {decision}"
    )

    return {
        "step_by_step_check": step,
        "decision": decision,
        "reasoning": explanation,
        "report_detail": report_detail,
    }