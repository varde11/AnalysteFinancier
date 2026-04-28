from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from typing import Annotated, Literal, List, Optional, Dict, Any
from typing_extensions import TypedDict
from enum import Enum
from datetime import datetime


class KeyNewsItem(BaseModel):
    claim: str
    evidence: str
    confidence: Literal["HIGH", "MEDIUM", "LOW"]


class NewsSummary(BaseModel):
    sentiment: Literal["POSITIVE", "NEGATIVE", "NEUTRAL"]
    key_news: List[KeyNewsItem]
    notes: Optional[str] = None


class finalSchema(BaseModel):
    news: NewsSummary
    step_by_step_check: str
    decision: Literal["HOLD", "BUY", "SELL"]
    reasoning: str
    report_detail: Dict[str, Any]        # structure JSON consommable par React


class State(TypedDict):
    messages: Annotated[list, add_messages]
    news: NewsSummary
    tech: dict
    final: finalSchema


class enumTicket(str, Enum):
    # Mega-caps originales
    TSLA = "TSLA"
    AMZN = "AMZN"
    GOOG = "GOOG"
    MSFT = "MSFT"
    AAPL = "AAPL"
    # Ajouts — profils variés pour tester les 3 décisions
    NVDA = "NVDA"   # Nvidia  — très volatile, souvent overbought
    META = "META"   # Meta    — tendance forte, bon benchmark
    NFLX = "NFLX"   # Netflix — récemment en forte baisse, potentiel oversold
    BA   = "BA"     # Boeing  — en crise longue, RSI souvent bas
    ZS   = "ZS"     # Zscaler — cybersécurité, a perdu ~30% fin 2025
    JPM  = "JPM"    # JPMorgan — bancaire stable, bon indicateur macro
    GLD  = "GLD"    # Gold ETF — or en forte hausse, potentiel overbought
    MO   = "MO"     # Altria  — tabac, valeur défensive souvent survendue
    MC_PA = "MC.PA"
    TTE = "TTE"
    AIR_PA = "AIR.PA"
    ASML = "ASML"
    SAP = "SAP"
    SPOT = "SPOT"
    SAMSUNG = "005930.KS"


class enumDecision(str,Enum):
    HOLD = "HOLD" 
    BUY= "BUY"
    SELL= "SELL"


class Client_Out(BaseModel):
    id_client: str= Field(...,min_length=3,max_length=10)
    nom: str = Field(...,max_length=20,min_length=3)

class Client_In(BaseModel):
    id_client:str = Field(...,min_length=3,max_length=10)
    nom:str = Field(...,max_length=20,min_length=3)
    password : str = Field(...,max_length=20,min_length=3)

class Client_Login(BaseModel):
    id_client:str = Field(...,min_length=3,max_length=10)
    password : str = Field(...,max_length=20,min_length=3)

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PredictionSchema(BaseModel):
    id_prediction: int = Field(ge=1)
    id_client:str = Field(...,min_length=3,max_length=10)
    ticket: str
    time_stamp: datetime
    key_news: List[KeyNewsItem]
    sentiment: Literal["POSITIVE", "NEGATIVE", "NEUTRAL"]
    notes: Optional[str] = None
    step_by_step_check: str
    decision: Literal["HOLD", "BUY", "SELL"]
    reasoning: str
    report_detail: Dict[str, Any]        

    model_config = {"from_attributes":True}

