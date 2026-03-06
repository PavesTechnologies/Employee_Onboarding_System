from pydantic import BaseModel
from typing import Optional


class DepartmentCreate(BaseModel):
    department_name: str
    description: Optional[str] = None


class DepartmentResponse(BaseModel):
    department_uuid: str
    department_name: str
    description: Optional[str]

    class Config:
        from_attributes = True

class DepartmentUpdate(BaseModel):
    department_name: Optional[str]
    description: Optional[str]        