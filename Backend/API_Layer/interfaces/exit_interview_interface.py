from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ExitInterviewCreate(BaseModel):
    exit_uuid: str
    employee_uuid: str
    reason_for_leaving: Optional[str] = None
    company_feedback: Optional[str] = None
    manager_feedback: Optional[str] = None
    rating: Optional[int] = None


class ExitInterviewUpdate(BaseModel):
    reason_for_leaving: Optional[str] = None
    company_feedback: Optional[str] = None
    manager_feedback: Optional[str] = None
    rating: Optional[int] = None


class ExitInterviewResponse(BaseModel):
    interview_uuid: str
    exit_uuid: str
    employee_uuid: str
    reason_for_leaving: Optional[str] = None
    company_feedback: Optional[str] = None
    manager_feedback: Optional[str] = None
    manager_feedback: Optional[str] = None
    rating: Optional[int] = None
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True