from pydantic import BaseModel
from typing import Optional
class OfferApproveActionRequest(BaseModel):
    user_uuid: str
    action: str  # e.g., "approve" or "reject"
    comments: str | None = None

class OfferApproveActionResponse(BaseModel):
    id: int
    user_uuid: str
    request_by: int
    requested_by_name: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    mail: str
    designation: str
    action: str

    
