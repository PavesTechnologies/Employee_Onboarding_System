from pydantic import BaseModel
from typing import List, Optional
from datetime import date


# -----------------------------
# REQUEST MODEL
# -----------------------------
class EmployeeTaskCreateRequest(BaseModel):
    user_uuid: str

    task_title: str
    task_type: str
    description: Optional[str] = None

    assigned_to: str
    assigned_team: Optional[str] = None

    priority: str
    status: str = "To Do"
    progress: int = 0

    due_date: Optional[date] = None
    reminder_date: Optional[date] = None

    send_notification: bool = True

    escalation_owner: Optional[str] = None

    internal_notes: Optional[str] = None
    comments: Optional[str] = None

    created_by: str


# -----------------------------
# RESPONSE MODEL
# -----------------------------
class EmployeeTaskCreateResponse(BaseModel):
    message: str
    task_uuid: str
    task_title: str
    status: str

# ============================================================
# UPDATE REQUEST MODEL
# ============================================================
class EmployeeTaskUpdateRequest(BaseModel):
    task_title: Optional[str] = None
    task_type: Optional[str] = None
    description: Optional[str] = None

    assigned_to: Optional[str] = None
    assigned_team: Optional[str] = None

    priority: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None

    due_date: Optional[date] = None
    reminder_date: Optional[date] = None

    send_notification: Optional[bool] = None

    escalation_owner: Optional[str] = None

    internal_notes: Optional[str] = None
    comments: Optional[str] = None

    updated_by: str


# ============================================================
# UPDATE RESPONSE MODEL
# ============================================================
class EmployeeTaskUpdateResponse(BaseModel):
    message: str
    task_uuid: str
    task_title: str
    status: str

# ============================================================
# GET TASK ITEM RESPONSE
# Reusing Create Request Model
# ============================================================
class EmployeeTaskItemResponse(EmployeeTaskCreateRequest):
    task_uuid: str
    class Config:
        from_attributes = True
class EmployeeTaskListResponse(BaseModel):
    message: str
    total_tasks: int
    tasks: List[EmployeeTaskItemResponse]

class EmployeeTaskListResponse(BaseModel):
    tasks: List[EmployeeTaskItemResponse]