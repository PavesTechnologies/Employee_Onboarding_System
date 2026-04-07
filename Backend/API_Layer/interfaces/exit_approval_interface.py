from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ExitApprovalCreate(BaseModel):

    exit_uuid: str
    approval_type: str
    remarks: Optional[str] = None
    approved_by: Optional[int] = None


class ExitApprovalResponse(BaseModel):

    approval_uuid: str
    exit_uuid: str
    approval_type: str
    status: str
    remarks: Optional[str] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True