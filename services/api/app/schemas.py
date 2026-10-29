from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TokenType = Literal["url", "pixel", "document", "aws", "kubeconfig"]
AlertStatus = Literal["New", "Investigating", "False Positive", "Resolved"]


class TokenCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    type: TokenType = "url"
    decoy_url: str | None = None
    external_key: str | None = Field(default=None, max_length=200)


class TokenUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    status: Literal["active", "disabled"] | None = None


class TokenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    type: TokenType
    status: str
    value: str  # URL that fires the canary
    decoy_url: str | None
    created_at: datetime
    alert_count: int


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    token_id: str
    token_name: str
    timestamp: datetime
    ip: str
    city: str
    country: str
    lat: float
    lon: float
    user_agent: str
    request_path: str
    request_headers: dict[str, str]
    notes: str
    status: AlertStatus


class AlertUpdate(BaseModel):
    notes: str | None = Field(default=None, max_length=10_000)
    status: AlertStatus | None = None


class HitIn(BaseModel):
    hit_id: str | None = Field(default=None, max_length=64)
    token_id: str = Field(max_length=64)
    ip: str = Field(max_length=64)
    user_agent: str = Field(default="", max_length=2000)
    path: str = Field(default="", max_length=2000)
    headers: dict[str, str] = Field(default_factory=dict)


class GenerateUrlsIn(BaseModel):
    prompt: str = Field(min_length=1, max_length=500)
