from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.models import Phase, Priority


class SkillResponse(BaseModel):
    name: str
    description: str
    when_to_use: str
    key_steps: Optional[List[str]] = None


class TodoBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    phase: Phase
    priority: Priority
    due_date: Optional[date] = None


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    phase: Optional[Phase] = None
    priority: Optional[Priority] = None
    due_date: Optional[date] = None
    completed: Optional[bool] = None


class TodoResponse(TodoBase):
    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime
    recommended_skills: List[SkillResponse] = []

    class Config:
        from_attributes = True


class PhaseResponse(BaseModel):
    name: str
    skills: List[SkillResponse]
