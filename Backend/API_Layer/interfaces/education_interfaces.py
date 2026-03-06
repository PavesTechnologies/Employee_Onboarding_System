from typing import Optional
from pydantic import BaseModel
from enum import Enum

# from pyparsing import Optional

# Education Documents #
class CreateEducDocRequest(BaseModel):
    document_name: str
    description: str

class EducDocResponse(BaseModel):
    education_document_uuid: str
    message: str

class EducDocDetails(BaseModel):
    education_document_uuid: str
    document_name: str
    description: str

class UploadFileResponse(BaseModel):
    document_uuid: str
    file_path: str
    message: str

class EmployeEduDoc(BaseModel):
    mapping_uuid: str
    user_uuid: str
    institution_name: str 
    specialization: str
    year_of_passing: int
    # percentage_cgpa: str
    

class DocumentStatus(str, Enum):
    uploaded = "uploaded"
    verified = "verified"
    rejected = "rejected"

class EmployeEduDocDetails(BaseModel):
    document_uuid: str
    mapping_uuid: str
    user_uuid: str
    institution_name: str 
    institute_location: str
    degree_uuid: str
    specialization: str
    education_mode: str
    start_year: int 
    year_of_passing: int
    delay_reason: Optional[str] = None
    percentage_cgpa: Optional[str] = None
    

    file_path: str
    status: DocumentStatus

class DeleteEmpEducResponse(BaseModel):
    document_uuid: str
    file_path:str
    message: str


class CountryEducationMappingResponse(BaseModel):
    mapping_uuid: str
    education_name: str
    document_name: str
    is_mandatory: bool

class DegreeMasterResponse(BaseModel):
    degree_uuid: str
    degree_name: str
    education_uuid: str
    education_name: str
class DegreeMasterRequest(BaseModel):
    
    degree_name: str
    education_uuid: str
    

