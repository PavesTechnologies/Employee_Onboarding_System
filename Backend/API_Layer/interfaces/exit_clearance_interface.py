from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ExitClearanceResponse(BaseModel):

    clearance_uuid: str
    exit_uuid: str
    employee_uuid: str
    department: str
    status: str
    remarks: Optional[str] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExitClearanceUpdate(BaseModel):

    clearance_uuid: str
    status: str
    remarks: Optional[str] = None