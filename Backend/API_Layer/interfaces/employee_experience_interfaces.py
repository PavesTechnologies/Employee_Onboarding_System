# interfaces/employee_experience_interfaces.py

from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional
import re


# ---------------------------------------------------------
# ENUMS (MATCH DB ENUMS EXACTLY)
# ---------------------------------------------------------

class EmploymentType(str, Enum):
    FULL_TIME = "Full-Time"
    PART_TIME = "Part-Time"
    INTERN = "Intern"
    CONTRACT = "Contract"
    FREELANCE = "Freelance"


class CertificateStatus(str, Enum):
    UPLOADED = "uploaded"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class ExperienceDocumentType(str, Enum):
    EXPERIENCE_LETTER = "experience_letter"
    PAYSLIP = "payslip"
    CONTRACT = "contract"
    FORM16 = "form16"
    INTERN_CERTIFICATE = "intern_certificate"
    OTHER = "other"

# ---------------------------------------------------------
# BASE VALIDATION UTILS
# ---------------------------------------------------------

def clean_text(value: Optional[str]) -> Optional[str]:
    """
    Normalize user input:
    - Strip leading/trailing spaces
    - Replace newlines & tabs safely
    NOTE: JSON must already be valid before this runs
    """
    if value is None:
        return value
    return (
        value
        .replace("\n", " ")
        .replace("\t", " ")
        .strip()
    )


# ---------------------------------------------------------
# REQUEST MODELS (CREATE / UPDATE)
# ---------------------------------------------------------


class ExperienceCreateRequest(BaseModel):
    employee_uuid: str
    company_name: str 
    start_date: date
    end_date: Optional[date] = None
    role_title: Optional[str] = Field(None, max_length=100)
    employment_type: EmploymentType
    is_current: bool = False
    notice_period_days: Optional[int] = Field(None, ge=0, le=120)

    # -------- VALIDATORS --------

    @validator("company_name")
    def validate_company_name(cls, v: str) -> str:
        if not re.match(r"^[A-Za-z0-9\s\&\-\.\,']+$", v):
            raise ValueError("Company name contains invalid characters")
        return v.strip()

    @validator("role_title", pre=True)
    def sanitize_text_fields(cls, v):
        v = clean_text(v)

        if v is None or len(v) < 2:
            raise ValueError("Role title must be at least 2 characters long")

        if len(v) > 100:
            raise ValueError("Role title must be at most 100 characters long")
        return v

    @validator("end_date")
    def validate_dates(cls, end_date, values):

        start_date = values.get("start_date")

        if start_date and end_date:

            if end_date < start_date:
                raise ValueError("End date cannot be before start date")

            if end_date > date.today():
                raise ValueError("End date cannot be in the future")

        return end_date

class ExperienceUpdateRequest(BaseModel):
    company_name: Optional[str] = Field(None, min_length=2, max_length=150)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    role_title: Optional[str] = Field(None, max_length=100)
    employment_type: Optional[EmploymentType] = None
    is_current: Optional[bool] = None
    notice_period_days: Optional[int] = Field(None, ge=0, le=120)

    # -------- VALIDATORS --------

    @validator("company_name")
    def validate_company_name(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^[A-Za-z0-9\s\&\-\.\,']+$", v):
            raise ValueError("Company name contains invalid characters")
        return v.strip() if v else v

    @validator("role_title", pre=True)
    def sanitize_text_fields(cls, v):
        return clean_text(v)


# ---------------------------------------------------------
# RESPONSE MODELS
# ---------------------------------------------------------

class ExperienceDocumentResponse(BaseModel):
    doc_uuid: str
    doc_type: ExperienceDocumentType
    file_name: str
    status: CertificateStatus
    uploaded_at: datetime

class ExperienceResponse(BaseModel):
    experience_uuid: str
    employee_uuid: str
    company_name: str
    role_title: str | None
    employment_type: str
    start_date: date
    end_date: date | None
    is_current: bool
    notice_period_days: int | None

    exp_certificate_path: str | None
    payslip_path: str | None
    internship_certificate_path: str | None
    contract_aggrement_path: str | None

    status: str
    uploaded_at: datetime

class GenericMessageResponse(BaseModel):
    experience_uuid: str
    message: str


class ExperienceCreateResponse(BaseModel):
    experience_uuid: str
    message: str

class ExperienceUpdate(BaseModel):
    company_name: str
    role_title: str | None
    employment_type: EmploymentType
    start_date: date
    end_date: date | None
    is_current: bool
    exp_certificate_path: str | None = None
    internship_certificate_path: str | None = None
    payslip_path: str | None = None
    contract_aggrement_path: str | None = None

    status: str | None = None
    verified_by: str | None = None
    verified_at: datetime | None = None
   # remarks: str | None
    

