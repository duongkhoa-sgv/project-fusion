from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field



# ENUMS

class FeedbackStatus(str, Enum):
    NEW = "NEW"
    TRIAGED = "TRIAGED"
    CLOSED = "CLOSED"


class FeedbackPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class FeedbackSource(str, Enum):
    CUSTOMER = "CUSTOMER"
    INTERNAL = "INTERNAL"



# CREATE

class FeedbackCreate(BaseModel):
    project_id: int
    title: str = Field(..., max_length=255)
    content: str
    priority: FeedbackPriority = FeedbackPriority.MEDIUM
    source: FeedbackSource = FeedbackSource.CUSTOMER
    attachment_urls: List[str] = Field(default_factory=list)



# UPDATE

class FeedbackUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    priority: Optional[FeedbackPriority] = None
    status: Optional[FeedbackStatus] = None

    class Config:
        extra = "forbid"



# RESPONSE

class FeedbackResponse(BaseModel):
    id: int
    project_id: int
    title: str
    content: str
    source: FeedbackSource
    priority: FeedbackPriority
    status: FeedbackStatus
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    attachment_urls: List[str]

    class Config:
        from_attributes = True