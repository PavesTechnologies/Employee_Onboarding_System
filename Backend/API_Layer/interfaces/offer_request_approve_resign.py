from pydantic import BaseModel
from typing import Optional


class OfferReassignApprovalRequest(BaseModel):
    user_uuid: str
    new_approver_id: int
    comments: Optional[str] = None


class OfferReassignApprovalResponse(BaseModel):
    id: int
    user_uuid: str
    previous_approver_id: int
    new_approver_id: int
    reassigned_by: int
    reassigned_by_name: Optional[str] = None
    action: str  # PENDING
