from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ExitApprovalCreate(BaseModel):

    exit_uuid: str
    


class ExitApprovalResponse(BaseModel):

    approval_uuid: str
    exit_uuid: str
    approval_type: str
    status: str
    remarks: Optional[str] = None
    approved_by: Optional[int] = None
    approved_by_name: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class ManagerApprovalRequest(BaseModel):
    approval_uuid: str
    status: str
    remarks: Optional[str] = None

class HRApprovalRequest(BaseModel):
    approval_uuid: str
    status: str
    remarks: Optional[str] = None

    class Config:
        from_attributes = True