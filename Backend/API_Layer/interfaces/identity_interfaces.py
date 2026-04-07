from pydantic import BaseModel, field_validator
from typing import Optional
import re
from datetime import date
class IdentityDetails(BaseModel):
    identity_type_uuid: str
    identity_type_name: str
    description: str
    is_active: bool

class IdentityCreateRequest(BaseModel):
    identity_type_name: str
    description: str
    is_active: Optional[bool] = True
    @field_validator("identity_type_name")
    def validate_type_name(cls, v):
        if not v or not v.strip():
            raise ValueError("type_name cannot be empty")

        v = v.strip()

        if len(v) < 3 or len(v) > 50:
            raise ValueError("type_name must be between 3 and 50 characters")

        pattern = r"^[A-Za-z0-9\- ]+$"
        if not re.match(pattern, v):
            raise ValueError("type_name must contain only letters, numbers, spaces, or hyphens")

        return v

class IdentityResponse(BaseModel):
    identity_type_uuid: str
    message: str

# Country Identity Mapping Intefaces
class CountryIdentityMappingDetails(BaseModel):
    mapping_uuid: str
    country_uuid: str
    identity_type_uuid: str
    is_mandatory: Optional[bool] = True

class CountryIdentityMappingRequest(BaseModel):
    country_uuid: str
    identity_type_uuid: str
    is_mandatory: Optional[bool] = True
class CountryIdentityMappingResponse(BaseModel):
    mapping_uuid: str
    message: str

class CountryIdentityDropdownResponse(BaseModel):
    mapping_uuid: str
    identity_type_uuid: str
    identity_type_name: str
    is_mandatory: bool

class EmployeeIdentityDocumentUpdateRequest(BaseModel):
    mapping_uuid: str
    identity_file_number: str
    expiry_date: Optional[date] = None
    file_path: Optional[str] = None


class EmployeeIdentityDocumentUpdateResponse(BaseModel):
    document_uuid: str
    message: str


 