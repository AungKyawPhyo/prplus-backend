from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EventBase(BaseModel):
    name: str
    contact: Optional[str]
    venue: Optional[str]
    description: Optional[str]
    event_date: datetime  # ✅ Replaces start_time and end_time

class EventCreate(EventBase):
    created_by: Optional[str] = None

class EventUpdate(EventBase):
    updated_by: Optional[str] = None

class EventOut(EventBase):
    id: int
    created_date: Optional[datetime]
    updated_date: Optional[datetime]
    created_by: Optional[str]
    updated_by: Optional[str]

    class Config:
        orm_mode = True