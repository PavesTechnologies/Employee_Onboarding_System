from pydantic import BaseModel
from typing import Optional

class OfferActionAdminResponse(BaseModel):
    user_uuid: str
    user_first_name: str
    user_middle_name: Optional[str] = None
    user_last_name: str
    request_id: str
    requested_name: str
    action : str
    message: str
