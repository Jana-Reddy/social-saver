from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from enum import Enum


class Category(str, Enum):
    coding = "Coding"
    design = "Design"
    fitness = "Fitness"
    food = "Food"
    travel = "Travel"
    finance = "Finance"
    science = "Science"
    entertainment = "Entertainment"
    news = "News"
    other = "Other"


class LinkSource(str, Enum):
    instagram = "instagram"
    twitter = "twitter"
    web = "web"
    unknown = "unknown"


class LinkCreate(BaseModel):
    raw_url: str
    source: LinkSource = LinkSource.unknown
    sender_phone: Optional[str] = None


class LinkRecord(BaseModel):
    id: str
    raw_url: str
    source: LinkSource
    title: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[Category] = None
    tags: list[str] = []
    thumbnail_url: Optional[str] = None
    author: Optional[str] = None
    sender_phone: Optional[str] = None
    created_at: datetime
    processed: bool = False


class AIResult(BaseModel):
    title: str
    summary: str
    category: Category
    tags: list[str]


class WebhookMessage(BaseModel):
    sender: str
    body: str
    provider: str = "twilio"
