from pydantic import BaseModel
from datetime import date
from typing import Optional

class SprintCreate(BaseModel):
    name: str
    goal: Optional[str]
    start_date: date
    end_date: date
    project_id: int

class SprintUpdate(BaseModel):
    name: Optional[str]
    goal: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]

class SprintResponse(BaseModel):
    id: int
    name: str
    goal: Optional[str]
    status: str            # PLANNED | ACTIVE | CLOSED
    start_date: date
    end_date: date
    project_id: int


    class Config:
        from_attributes = True
