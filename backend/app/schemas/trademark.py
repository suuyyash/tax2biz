from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class TrademarkSearchQuery(BaseModel):
    q: str = Field(..., min_length=1, max_length=100, description="Wordmark or brand name to search")
    target_class: Optional[str] = Field("all", description="Nice Classification (1-45) or 'all'")

class TrademarkItemSchema(BaseModel):
    appNo: str
    wordmark: str
    classNum: int
    classLabel: str
    status: str
    statusClass: str
    proprietor: str
    filingDate: str
    validUpto: str
    goods: str
    source: str = "TradeMarx Official IP India API"

class TrademarkSearchResponse(BaseModel):
    status: str
    query: str
    targetClass: str
    totalMatches: int
    verdict: Dict[str, Any]
    records: List[TrademarkItemSchema]
    source: str = "TradeMarx Official IP India API"
