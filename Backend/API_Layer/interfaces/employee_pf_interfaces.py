from pydantic import BaseModel, Field, validator
from typing import Optional
import re


class CreatePfDetailsRequest(BaseModel):
    user_uuid: str
    pf_member: bool
    uan_number: Optional[str] = Field(None, min_length=12, max_length=12)

    @validator("uan_number", always=True)
    def validate_uan(cls, v, values):
        pf_member = values.get("pf_member")

        if pf_member and not v:
            raise ValueError("UAN number is required if PF member is Yes")

        if v and not re.match(r"^\d{12}$", v):
            raise ValueError("UAN must be exactly 12 digits")

        return v


class CreatePfDetailsResponse(BaseModel):
    pf_uuid: str
    message: str


class PfDetails(BaseModel):
    pf_uuid: str
    user_uuid: str
    pf_member: bool
    uan_number: Optional[str]