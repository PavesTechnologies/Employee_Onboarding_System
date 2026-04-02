from pydantic import BaseModel
from typing import List


class Summary(BaseModel):
    selected: int
    offersMade: int
    joined: int
    dropOffs: int
    pending: int


class MonthlyJoining(BaseModel):
    week: str
    completed: int
    joining: int


class WeeklyJoining(BaseModel):
    day: str
    completed: int
    joining: int


class Candidate(BaseModel):
    name: str
    role: str
    department: str
    joiningDate: str
    status: str


class Activity(BaseModel):
    message: str
    type: str
    time: str


class DashboardResponse(BaseModel):
    summary: dict
    monthlyJoinings: List[MonthlyJoining]
    weeklyJoinings: List[WeeklyJoining]
    joinedCandidates: List[dict]
    activities: List[dict]