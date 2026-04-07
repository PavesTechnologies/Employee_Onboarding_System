from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class BulkJoinRequest(BaseModel):
    user_emails_list: List[str]
    joining_date: date
    location: str
    reporting_time: str
    department: str
    reporting_manager: str
    custom_message: Optional[str] = None


class ReassignJoiningRequest(BaseModel):
    user_uuid: str
    new_joining_date: date
    reporting_manager: str
    reporting_time: str
    location: str
    department: str
    comment: Optional[str] = None