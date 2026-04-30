from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ExitFinalSettlementCreate(BaseModel):

    exit_uuid: str
    employee_uuid: str
    last_salary: float
    leave_encashment: float
    bonus: float
    deductions: float


class ExitFinalSettlementApprove(BaseModel):

    settlement_uuid: str
    remarks: Optional[str] = None


class ExitFinalSettlementPaid(BaseModel):

    settlement_uuid: str


class ExitFinalSettlementResponse(BaseModel):

    settlement_uuid: str
    exit_uuid: str
    employee_uuid: str
    last_salary: float
    leave_encashment: float
    bonus: float
    deductions: float
    net_payable: float
    status: str
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True