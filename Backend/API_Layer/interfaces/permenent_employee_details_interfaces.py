from enum import Enum
import re
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional


# --------------------------------
# ENUM CLASSES
# --------------------------------

class EmploymentType(str, Enum):
    FULL_TIME = "Full-Time"
    PART_TIME = "Part-Time"
    INTERN = "Intern"
    CONTRACTOR = "Contractor"
    FREELANCE = "Freelance"


class EmploymentStatus(str, Enum):
    PROBATION = "Probation"
    ACTIVE = "Active"
    RESIGNED = "Resigned"
    TERMINATED = "Terminated"
    ABSCONDED = "Absconded"


class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class MaritalStatus(str, Enum):
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"

class WorkMode(str, Enum):
    OFFICE = "Office"
    REMOTE = "Remote"
    HYBRID = "Hybrid"    


# --------------------------------
# CREATE EMPLOYEE REQUEST
# --------------------------------

class CreatePermanentEmployeeRequest(BaseModel):

    user_uuid: str
    first_name: str = Field(..., min_length=2)
    middle_name: Optional[str] = None
    last_name: str = Field(..., min_length=1)
    date_of_birth: date
    contact_number: Optional[str] = None
    department_uuid: str
    designation_uuid: str
    reporting_manager_uuid: Optional[str] = None
    employment_type: EmploymentType
    joining_date: date
    location: str
    work_mode: WorkMode
    employment_status: EmploymentStatus
    blood_group: Optional[str] = None
    gender: Optional[Gender] = None
    marital_status: Optional[MaritalStatus] = None
    total_experience: Optional[float] = None


    @validator("contact_number")
    def validate_contact_number(cls, v):
        if v and not re.match(r"^[0-9]{10}$", v):
            raise ValueError("Contact number must contain exactly 10 digits")
        return v


    @validator("total_experience")
    def validate_experience(cls, v):
        if v is not None and v < 0:
            raise ValueError("Total experience cannot be negative")
        return v


# --------------------------------
# CREATE EMPLOYEE RESPONSE
# --------------------------------

class CreatePermanentEmployeeResponse(BaseModel):

    employee_uuid: str
    employee_id: str
    work_email: str
    message: str


# --------------------------------
# EMPLOYEE DETAILS RESPONSE
# --------------------------------

class PermanentEmployeeDetails(BaseModel):

    user_uuid: str
    employee_id: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    date_of_birth: date
    work_email: Optional[str]
    contact_number: Optional[str]
    department_uuid: str
    designation_uuid: str
    reporting_manager_uuid: Optional[str]
    employment_type: str
    joining_date: date
    location: str
    work_mode: str
    employment_status: str
    blood_group: Optional[str]
    gender: Optional[str]
    marital_status: Optional[str]
    total_experience: Optional[float]
    created_at: datetime


# --------------------------------
# UPDATE EMPLOYEE REQUEST
# --------------------------------

class UpdatePermanentEmployeeRequest(BaseModel):

    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    contact_number: Optional[str] = None

    department_uuid: Optional[str] = None
    designation_uuid: Optional[str] = None
    reporting_manager_uuid: Optional[str] = None

    location: Optional[str] = None

    employment_type: Optional[EmploymentType] = None
    joining_date: Optional[date] = None
    employment_status: Optional[EmploymentStatus] = None
    work_mode: Optional[WorkMode] = None

    blood_group: Optional[str] = None
    gender: Optional[Gender] = None
    marital_status: Optional[MaritalStatus] = None

    total_experience: Optional[float] = None