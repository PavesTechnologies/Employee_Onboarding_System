from pydantic import BaseModel
from typing import List, Optional


# ---------------------------------------------------------------------------
# Dashboard Summary
# ---------------------------------------------------------------------------

class DashboardSummary(BaseModel):
    total_candidates: int
    active_candidates: int
    completed_candidates: int
    pending_candidates: int


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------

class OfferManagement(BaseModel):
    created: int
    offered: int
    accepted: int
    rejected: int


class EmployeeOnboarding(BaseModel):
    submitted: int
    verified: int
    completed: int


class JoiningProcess(BaseModel):
    joining_pending: int
    joining: int
    rescheduled: int


class Overview(BaseModel):
    total_candidates: int
    offer_management: OfferManagement
    employee_onboarding: EmployeeOnboarding
    joining_process: JoiningProcess


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class PipelineStage(BaseModel):
    count: int
    label: str
    description: str


class Pipeline(BaseModel):
    created: PipelineStage
    offered: PipelineStage
    accepted: PipelineStage
    submitted: PipelineStage
    verified: PipelineStage
    completed: PipelineStage


# ---------------------------------------------------------------------------
# Pending Actions
# ---------------------------------------------------------------------------

class ActionItem(BaseModel):
    count: int
    description: str
    priority: str


class PendingActions(BaseModel):
    documents_pending_verification: ActionItem
    candidates_awaiting_joining: ActionItem
    candidates_yet_to_submit: ActionItem


# ---------------------------------------------------------------------------
# Action Required Summary
# ---------------------------------------------------------------------------

class ActionRequiredSummary(BaseModel):
    total_pending_actions: int
    high_priority: int
    medium_priority: int
    low_priority: int


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

class MetricItem(BaseModel):
    value: str
    description: str


class Metrics(BaseModel):
    offer_acceptance_success_rate: MetricItem
    employee_onboarding_completion_rate: MetricItem
    candidate_attrition_rate: MetricItem


# ---------------------------------------------------------------------------
# Documents (per-type breakdown)
# ---------------------------------------------------------------------------

class DocumentStat(BaseModel):
    verified_count: int
    pending_count: int
    rejected_count: int
    total: int
    completion_percentage: float


class Documents(BaseModel):
    personal: DocumentStat
    address: DocumentStat
    education: DocumentStat
    identity: DocumentStat
    experience: DocumentStat
    bank: DocumentStat
    pf: DocumentStat


# ---------------------------------------------------------------------------
# Document Summary (aggregated across all types)
# ---------------------------------------------------------------------------

class DocumentSummary(BaseModel):
    total_documents: int
    verified_documents: int
    pending_documents: int
    rejected_documents: int
    overall_completion_percentage: float


# ---------------------------------------------------------------------------
# Process Delays
# ---------------------------------------------------------------------------

class DelayItem(BaseModel):
    count: int
    description: str


class ProcessDelays(BaseModel):
    delayed_more_than_3_days: DelayItem
    delayed_more_than_7_days: DelayItem


# ---------------------------------------------------------------------------
# Department Summary
# ---------------------------------------------------------------------------

class DepartmentSummaryItem(BaseModel):
    department: str
    count: int
    percentage: float


# ---------------------------------------------------------------------------
# Recent Activity
# ---------------------------------------------------------------------------

class RecentActivityItem(BaseModel):
    user_uuid: str
    candidate_name: str
    department: str
    designation: str
    # raw value kept for backward compatibility
    reporting_manager: str
    # HR-friendly resolved fields
    reporting_manager_id: Optional[str]
    reporting_manager_name: str
    joining_date: Optional[str]
    current_status: str
    activity_action: str
    activity_timestamp: str


# ---------------------------------------------------------------------------
# Top-level Dashboard Response
# ---------------------------------------------------------------------------

class DashboardResponse(BaseModel):
    dashboard_summary: DashboardSummary
    overview: Overview
    pipeline: Pipeline
    pending_actions: PendingActions
    action_required_summary: ActionRequiredSummary
    metrics: Metrics
    documents: Documents
    document_summary: DocumentSummary
    overall_document_completion_percentage: float
    process_delays: ProcessDelays
    department_summary: List[DepartmentSummaryItem]
    recent_activity: List[RecentActivityItem]


# ---------------------------------------------------------------------------
# Celebrations
# ---------------------------------------------------------------------------

class CelebrationItem(BaseModel):
    name: str
    date: str


class WorkAnniversaryItem(CelebrationItem):
    anniversaryYear: int


class CelebrationsResponse(BaseModel):
    birthdays: List[CelebrationItem]
    workAnniversaries: List[WorkAnniversaryItem]
    newJoinees: List[CelebrationItem]
