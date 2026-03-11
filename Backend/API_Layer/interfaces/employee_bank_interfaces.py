from enum import Enum
import re
from pydantic import BaseModel, Field, validator
from typing import Optional


class AccountType(str, Enum):
    SAVINGS = "Savings"
    CURRENT = "Current"


class CreateBankDetailsRequest(BaseModel):
    user_uuid: str
    account_holder_name: str = Field(..., min_length=3, max_length=150)
    bank_name: str = Field(..., min_length=2, max_length=100)
    branch_name: Optional[str] = Field(None, max_length=100)
    account_number: str = Field(..., min_length=9, max_length=30)
    ifsc_code: str = Field(..., min_length=11, max_length=11)
    account_type: AccountType

    @validator("account_holder_name", "bank_name")
    def validate_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v

    @validator("ifsc_code")
    def validate_ifsc(cls, v):
        if not re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", v):
            raise ValueError("Invalid IFSC code format")
        return v


class CreateBankDetailsResponse(BaseModel):
    bank_uuid: str
    message: str


class BankDetails(BaseModel):
    bank_uuid: str
    user_uuid: str
    account_holder_name: str
    bank_name: str
    branch_name: Optional[str]
    account_number: str
    ifsc_code: str
    account_type: str