from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class BackgroundCheckStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_REVIEW = "IN_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class EmployeeStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    READY_TO_SEND = "READY_TO_SEND"
    AWAITING_BGV_RESULT = "AWAITING_BGV_RESULT"
    CLEARED = "CLEARED"
    REJECTED = "REJECTED"


class BackgroundCheckGroup(str, Enum):
    Identity = "Identity"
    Education = "Education"
    Experience = "Experience"
    Reference = "Reference"
    Address = "Address"
    Compliance = "Compliance"
    Financial = "Financial"
    Custom_Session = "Custom Session"


class BackgroundCheckCreateRequest(BaseModel):
    user_uuid: str = Field(..., min_length=1)
    check_type: Optional[str] = None
    label: str = Field(..., min_length=1)
    group: str = Field(..., min_length=1)
    status: BackgroundCheckStatus = BackgroundCheckStatus.NOT_STARTED
    notes: Optional[str] = ""
    details: Optional[dict[str, Any]] = None
    doc_category: Optional[str] = None
    document_id: Optional[str] = None
    created_by: Optional[str] = None


class BackgroundCheckUpdateRequest(BaseModel):
    check_type: Optional[str] = None
    label: Optional[str] = None
    group: Optional[str] = None
    status: Optional[BackgroundCheckStatus] = None
    notes: Optional[str] = None
    details: Optional[dict[str, Any]] = None
    doc_category: Optional[str] = None
    document_id: Optional[str] = None
    created_by: Optional[str] = None


class BackgroundCheckStatusUpdateRequest(BaseModel):
    status: BackgroundCheckStatus
    notes: Optional[str] = None


class BackgroundCheckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    check_uuid: str
    user_uuid: str
    check_type: str
    label: str
    group: str
    status: BackgroundCheckStatus
    notes: Optional[str] = ""
    details: Optional[dict[str, Any]] = None
    doc_category: Optional[str] = None
    document_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BackgroundCheckMessageResponse(BaseModel):
    check_uuid: str
    message: str


class SendToConsultancyRequest(BaseModel):
    user_uuid: str = Field(..., min_length=1)
    to_email: EmailStr
    cc_email: Optional[str] = None
    message: str = (
        "Please find the attached background verification documents in the ZIP file."
    )
    check_ids: list[str] = Field(default_factory=list)


class BackgroundCheckDocumentResponse(BaseModel):
    document_id: str
    user_uuid: str
    category: str
    document_name: Optional[str] = None
    doc_type: Optional[str] = None
    file_path: str
    uploaded_at: Optional[datetime] = None


class BackgroundCheckDocumentMessageResponse(BaseModel):
    document_id: str
    file_path: Optional[str] = None
    message: str


class SendToConsultancyResponse(BaseModel):
    user_uuid: str
    to_email: str
    selected_check_count: int
    docs_attached: int = 0
    message: str


class EmployeeBgvStatusUpdateRequest(BaseModel):
    bgv_status: EmployeeStatus


class EmployeeBgvStatusUpdateResponse(BaseModel):
    user_uuid: str
    bgv_status: EmployeeStatus
    message: str


class FinalBGVDecision(str, Enum):
    CLEARED = "CLEARED"
    REJECTED = "REJECTED"


class FinalBGVDecisionRequest(BaseModel):
    decision: FinalBGVDecision
    remarks: Optional[str] = None
    decision_by: Optional[str] = None


class FinalBGVDecisionResponse(BaseModel):
    user_uuid: str
    decision: FinalBGVDecision
    tasks_updated: int
    message: str
