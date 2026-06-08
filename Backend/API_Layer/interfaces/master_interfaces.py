from pydantic import BaseModel


class CreateCountryResponse(BaseModel):
    message: str
    country_uuid: str


class CountryDetails(BaseModel):
    country_code: str
    country_name: str
    is_active: bool


class CountryAllDetails(BaseModel):
    country_uuid: str
    calling_code: str
    country_name: str
    is_active: bool


# EDUCATION LEVEL #
class CreateEducLevelResponse(BaseModel):
    education_uuid: str
    message: str


class CreateEducLevelRequest(BaseModel):
    education_name: str
    description: str


class EducLevelDetails(BaseModel):
    education_name: str
    description: str
    is_active: bool


class AllEducLevelDetails(BaseModel):
    education_uuid: str
    education_name: str
    description: str
    is_active: bool


class CountryEductionMapping(BaseModel):
    mapping_uuid: str
    message: str


class CountryEducationMappingDetails(BaseModel):
    mapping_uuid: str
    country_uuid: str
    education_uuid: str
    education_document_uuid: str
    is_mandatory: bool


# Contacts ##
class CreateContactResponse(BaseModel):
    contact_uuid: str
    message: str


class CreateContactRequest(BaseModel):
    user_uuid: str
    country_uuid: str
    contact_number: str
    emergency_contact: str


class ContactDetails(BaseModel):
    contact_uuid: str
    user_uuid: str
    country_uuid: str
    contact_number: str
    emergency_contact: str


class UpdateContactRequest(BaseModel):
    contact_type: str
    contact_value: str
    emergency_contact: str
    is_active: bool
