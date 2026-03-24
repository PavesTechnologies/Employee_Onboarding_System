from pydantic import BaseModel
from typing import List


class Overview(BaseModel):
    total_candidates: int
    offers_created: int
    offers_sent: int
    offers_accepted: int
    offers_verified: int
    offers_rejected: int


class Pipeline(BaseModel):
    created: int
    sent: int
    accepted: int
    verified: int
    completed: int


class PendingActions(BaseModel):
    pending_verification: int
    pending_joining: int


class Metrics(BaseModel):
    acceptance_rate: str
    completion_rate: str
    drop_off_rate: str

class Documents(BaseModel):
    education_completed: int
    bank_completed: int
    pf_completed: int


class Aging(BaseModel):
    pending_3_days: int
    pending_7_days: int


class Activity(BaseModel):
    user_uuid: str
    name: str
    action: str


class DashboardResponse(BaseModel):
    overview: Overview
    pipeline: Pipeline
    pending_actions: PendingActions
    metrics: Metrics
    documents: Documents
    aging: Aging
    recent_activity: List[Activity]