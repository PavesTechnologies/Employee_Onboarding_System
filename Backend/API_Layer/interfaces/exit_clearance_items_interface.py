from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ExitClearanceItemCreate(BaseModel):
    clearance_uuid: str
    item_name: str


class ExitClearanceItemUpdate(BaseModel):

    clearance_item_uuid: str
    status: str
    remarks: Optional[str] = None
    approved_by: Optional[int] = None


class ExitClearanceItemResponse(BaseModel):

    clearance_item_uuid: str
    clearance_uuid: str
    item_name: str
    status: str
    remarks: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True