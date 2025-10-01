from pydantic import BaseModel
from typing import Optional


class ProfileCreate(BaseModel):
    handle: str
    platform: Optional[str] = "mock"
    alert_threshold: Optional[int] = None
    telegram_chat_id: Optional[str] = None


class ProfileRead(ProfileCreate):
    id: int


class AlertSettings(BaseModel):
    alert_threshold: Optional[int]
    telegram_chat_id: Optional[str]


class Insight(BaseModel):
    handle: str
    latest_count: int
    delta_24h: Optional[int] = None
