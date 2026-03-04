from enum import Enum
import re
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional
class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class MaritalStatus(str, Enum):
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"

class PersonalDetailsRequest(BaseModel):
    user_uuid: str
    date_of_birth: str
    gender: Gender
    marital_status: MaritalStatus
    blood_group: str
    nationality_country_uuid: str
    residence_country_uuid: str
    emergency_contact_name: str
    emergency_contact_phone: str
    emergency_contact_relation_uuid: str

class PersonalDetailsResponse(BaseModel):
    personal_uuid: str
    message: str
class PersonalDetails(BaseModel):
    personal_uuid: str
    user_uuid: str
    date_of_birth: date     # <-- accepts datetime.date automatically
    gender: str
    marital_status: str
    blood_group: str
    nationality_country_uuid: str
    residence_country_uuid: str
    emergency_contact_name: str
    emergency_contact_phone: str
    emergency_contact_relation_uuid: str
        
class UpdatePersonalRequest(BaseModel):
    date_of_birth: str
    gender: Gender
    marital_status: MaritalStatus
    blood_group: str
    nationality_country_uuid: str
    residence_country_uuid: str
    emergency_contact_name: str
    emergency_contact_phone: str
    emergency_contact_relation_uuid: str
    

class CreateRelationRequest(BaseModel):
    relation_name: str

class CreateRelationResponse(BaseModel):
    relation_uuid: str
    message: str

# Addresses Interfaces

class AddressType(str, Enum):
    permanent = "permanent"
    current = "current"


class CreateAddressRequest(BaseModel):
    user_uuid: str
    address_type: AddressType
    address_line1: str = Field(..., min_length=3, max_length=100)
    address_line2: str = Field(..., min_length=3, max_length=100)
    city: str = Field(..., min_length=2, max_length=50)
    district_or_ward: Optional[str] = None
    state_or_region: str = Field(..., min_length=2, max_length=50)
    postal_code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")  
    country_uuid: str

    # Prevent empty strings
    @validator("address_line1","address_line2", "city", "state_or_region")
    def validate_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v

    # City validation
    @validator("city")
    def validate_city(cls, v):
        if not re.match(r"^[A-Za-z\s\-'.]+$", v):
            raise ValueError("City name contains invalid characters")
        return v

    # State validation
    @validator("state_or_region")
    def validate_state(cls, v):
        if not re.match(r"^[A-Za-z\s\-'.]+$", v):
            raise ValueError("State/Region contains invalid characters")
        return v

    # At least one location field required
    @validator("district_or_ward", always=True)
    def validate_location_fields(cls, v, values):
        city = values.get("city")
        state = values.get("state_or_region")
        
        if not (city or state or v):
            raise ValueError("At least one of city / district_or_ward / state_or_region must be provided")
        return v
class CreateAddressResponse(BaseModel):
    address_uuid: str
    message: str

class AddressDetails(BaseModel):
    address_uuid: str
    user_uuid: str
    address_type: str
    address_line1: str
    address_line2: Optional[str] = None
    city: Optional[str] = None
    district_or_ward: Optional[str] = None
    state_or_region: Optional[str] = None
    postal_code: str
    country_uuid: str

class EmployeeIdentityResponse(BaseModel):
    identity_uuid: str
    identity_file_number: str
    file_path: str
    message: str

class DeleteEmployeeIdentityResponse(BaseModel):
    document_uuid: str
    message: str