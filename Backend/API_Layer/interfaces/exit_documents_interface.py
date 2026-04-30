from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

class ExitDocumentResponse(BaseModel):
    document_uuid: str
    exit_uuid: str
    employee_uuid: str
    document_type: str
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
