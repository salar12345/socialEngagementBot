from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class Profile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    handle: str
    platform: str = "mock"
    monitor: bool = True
    alert_threshold: Optional[int] = None
    telegram_chat_id: Optional[str] = None
    histories: List["FollowerHistory"] = Relationship(back_populates="profile")


class FollowerHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profile_id: int = Field(foreign_key="profile.id")
    count: int
    ts: datetime = Field(default_factory=datetime.utcnow)
    profile: Optional[Profile] = Relationship(back_populates="histories")


class AlertLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profile_id: int
    threshold: int
    message: str
    ts: datetime = Field(default_factory=datetime.utcnow)
