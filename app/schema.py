from pydantic import BaseModel,Field
from langgraph.graph.message import add_messages
from typing import Annotated,Literal,List,Optional
from typing_extensions import TypedDict


class Technical_Indicator_Schema(BaseModel):
    Technical_Analysis_for: str = Field(description="The ticker symbol, e.g. TSLA")
    Current_Price: str = Field(description="The current price with currency")
    RSI_14: str = Field(description="The RSI value")
    SMA_50: str
    SMA_200: str
    Trend: str = Field(description="Bullish or Bearish")


class KeyNewsItem(BaseModel):
    claim: str
    evidence: str
    confidence: Literal["HIGH","MEDIUM","LOW"]

class NewsSummary(BaseModel):
    sentiment: Literal["POSITIVE","NEGATIVE","NEUTRAL"]
    key_news: List[KeyNewsItem]
    notes: Optional[str] = None

class State(TypedDict):
    messages: Annotated[list,add_messages]
    news : NewsSummary
    tech : dict
    final : list





