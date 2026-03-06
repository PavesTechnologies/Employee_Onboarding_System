from pydantic import BaseModel
from typing import Optional


class DesignationCreate(BaseModel):
    designation_name: str
    department_uuid: str
    description: Optional[str] = None


class DesignationUpdate(BaseModel):
    designation_name: Optional[str] = None
    department_uuid: Optional[str] = None
    description: Optional[str] = None


class DesignationResponse(BaseModel):
    designation_uuid: str
    designation_name: str
    department_uuid: str
    description: Optional[str]

    class Config:
        from_attributes = True