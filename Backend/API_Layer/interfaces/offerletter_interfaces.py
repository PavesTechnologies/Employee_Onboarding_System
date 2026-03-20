# Backend/api/interfaces/offerletter_interfaces.py

from pydantic import BaseModel, EmailStr
from typing import List, Optional

class OfferCreateRequest(BaseModel):
    first_name: str
    last_name: str
    mail: str
    country_code: str
    contact_number: str
    designation: str
    employee_type: str
    package: str
    currency : str
    job_id :str
    cc_emails: Optional[List[EmailStr]] = None


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
    user_uuid: str
    first_name: str
    last_name: str
    mail: str
    country_code: str
    contact_number: str
    designation: str
    employee_type: str
    package: Optional[str] = None
    currency : Optional[str] = None
    job_id : Optional[str] = None
    created_by: int
    status : str
    cc_emails: Optional[str] = None



class Config:
    from_attributes = True  # important

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