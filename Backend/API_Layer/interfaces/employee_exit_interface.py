from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class EmployeeExitCreate(BaseModel):

    employee_uuid: str
    employee_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department_uuid: Optional[str] = None
    designation_uuid: Optional[str] = None

    exit_type: str
    resignation_date: Optional[date] = None
    last_working_day: Optional[date] = None
    notice_period: Optional[int] = None
    notice_start_date: Optional[date] = None
    notice_end_date: Optional[date] = None
    reason: Optional[str] = None
    remarks: Optional[str] = None


class EmployeeExitResponse(BaseModel):

    exit_uuid: str
    employee_uuid: str
    exit_type: str
    status: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True