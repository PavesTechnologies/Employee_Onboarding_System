from pydantic import BaseModel
from typing import List


# -------- COMMON --------

class LabelValue(BaseModel):
    label: str
    value: int


# -------- DEMOGRAPHICS --------

class AgeGroupStats(BaseModel):
    group: str
    female: int
    male: int


class ExperienceStats(BaseModel):
    range: str
    value: int


class DemographicsResponse(BaseModel):
    total: int

    gender: List[LabelValue]

    employmentType: List[LabelValue]   # ✅ ADDED
    workerType: List[LabelValue]       # ✅ ADDED

    nationality: List[LabelValue]

    ageGroups: List[AgeGroupStats]

    experience: List[ExperienceStats]


# -------- DEPARTMENT BASED --------

class WorkerDeptStats(BaseModel):
    dept: str
    permanent: int
    contingent: int


class GenderDeptStats(BaseModel):
    dept: str
    female: int
    male: int


class EmploymentDeptStats(BaseModel):
    dept: str
    full: int


# -------- DASHBOARD --------

class DashboardResponse(BaseModel):
    demographics: DemographicsResponse
    workerDept: List[WorkerDeptStats]
    genderDept: List[GenderDeptStats]
    employmentDept: List[EmploymentDeptStats]