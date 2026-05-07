# Backend/api/interfaces/offerletter_interfaces.py

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import List, Optional

class CompensationComponent(BaseModel):
    name: str
    type: str
    frequency: str
    amount: float

class CompensationComponentResponse(BaseModel):
    name: str
    type: str
    frequency: str
    amount: float
class OfferCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    mail: str
    country_code: str
    contact_number: str
    designation: str
    employee_type: str
    currency: str
    compensation_components: List[CompensationComponent]
    total_ctc: float                                    
    cc_emails: Optional[List[EmailStr]] = Field(
        default=None,
        validation_alias=AliasChoices("cc_emails", "cc_email", "ccEmails", "ccEmail"),
    )

    @field_validator("cc_emails", mode="before")
    @classmethod
    def normalize_cc_emails(cls, value):
        if value in (None, ""):
            return None
        if isinstance(value, str):
            return [email.strip() for email in value.split(",") if email.strip()]
        return value

class OfferCreateResponse(BaseModel):
    message: str
    offer_id: str

class OfferUpdateResponse(BaseModel):
    message: str
    offer_id: str

class BulkOfferCreateResponse(BaseModel):
    total_rows: int
    processed_rows: int
    successful_count: int
    failed_count: int
    successful_offers: list[dict]
    failed_offers: list[dict]
    skipped_rows: int

class OfferLetterDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_uuid: str
    first_name: Optional[str] = None
    middle_name :Optional[str] = None
    last_name: Optional[str] = None
    mail: Optional[str] = None
    country_code: Optional[str] = None
    contact_number: Optional[str] = None
    designation: Optional[str] = None
    employee_type: Optional[str] = None
    currency: Optional[str] = None
    total_ctc: float | None = None
    created_by: Optional[int] = None
    status : Optional[str] = None

    cc_emails: Optional[List[EmailStr]] = None
    compensation_components: List[CompensationComponentResponse] = Field(default_factory=list)

    @field_validator("cc_emails", mode="before")
    @classmethod
    def normalize_cc_emails(cls, value):
        if value in (None, ""):
            return []
        if isinstance(value, str):
            return [email.strip() for email in value.split(",") if email.strip()]
        return value

class OfferPendingCandidate(BaseModel):
    user_uuid: str
    first_name: str
    last_name: str
    mail: str
    designation: str
    employee_type: str
    package: str
    currency: str
    status: str
    created_by: int

class BulkSendOfferLettersRequest(BaseModel):
    user_uuid_list: List[str]

class BulkSendOfferLettersResult(BaseModel):
    user_uuid: str
    status: str                     # "success" or "failed"
    mail_sent_to: Optional[str]     # candidate email from DB
    pandadoc_status: Optional[str]  # e.g., "document_created_and_sent"
    message: Optional[str]          # success message
    error: Optional[str]            # error details if failed


class BulkSendOfferLettersResponse(BaseModel):
    total_requests: int
    successful: int
    failed: int
    results: List[BulkSendOfferLettersResult]

class DeleteOfferResponse(BaseModel):
    message: str
