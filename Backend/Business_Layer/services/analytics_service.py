from collections import Counter, defaultdict
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.models.models import EmployeeDetails, PersonalDetails, Countries, Departments


def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


# ---------------- DEMOGRAPHICS ----------------
async def get_demographics(db: AsyncSession):

    stmt = (
        select(EmployeeDetails, PersonalDetails, Countries)
        .join(PersonalDetails, EmployeeDetails.user_uuid == PersonalDetails.user_uuid)
        .join(Countries, PersonalDetails.nationality_country_uuid == Countries.country_uuid)
    )

    result = await db.execute(stmt)
    data = result.all()

    gender_counter = Counter()
    nationality_counter = Counter()
    employment_counter = Counter()
    worker_counter = Counter()

    age_groups = {
        "18-21": {"female": 0, "male": 0},
        "22-25": {"female": 0, "male": 0},
        "26-30": {"female": 0, "male": 0},
        "31-40": {"female": 0, "male": 0},
        "41-55": {"female": 0, "male": 0},
    }

    experience_counter = {"0-1": 0, "1-2": 0}

    for emp, personal, country in data:

        if emp.gender:
            gender_counter[emp.gender] += 1

        if country and country.country_name:
            nationality_counter[country.country_name] += 1

        if emp.employment_type:
            employment_counter[emp.employment_type] += 1
            if emp.employment_type == "Full-Time":
                worker_counter["Permanent"] += 1
            else:
                worker_counter["Contract"] += 1

        if personal.date_of_birth and emp.gender:
            age = calculate_age(personal.date_of_birth)
            gender = emp.gender.lower()

            if gender in ["male", "female"]:
                if 18 <= age <= 21:
                    age_groups["18-21"][gender] += 1
                elif 22 <= age <= 25:
                    age_groups["22-25"][gender] += 1
                elif 26 <= age <= 30:
                    age_groups["26-30"][gender] += 1
                elif 31 <= age <= 40:
                    age_groups["31-40"][gender] += 1
                elif 41 <= age <= 55:
                    age_groups["41-55"][gender] += 1

        if emp.joining_date:
            years = (date.today() - emp.joining_date).days / 365
            if years <= 1:
                experience_counter["0-1"] += 1
            elif years <= 2:
                experience_counter["1-2"] += 1

    return {
        "total": len(data),

        "gender": [{"label": k, "value": v} for k, v in gender_counter.items()],
        "employmentType": [{"label": k, "value": v} for k, v in employment_counter.items()],
        "workerType": [{"label": k, "value": v} for k, v in worker_counter.items()],
        "nationality": [{"label": k, "value": v} for k, v in nationality_counter.items()],

        "ageGroups": [{"group": k, **v} for k, v in age_groups.items()],
        "experience": [{"range": k, "value": v} for k, v in experience_counter.items()],
    }


# ---------------- WORKER BY DEPT ----------------
async def get_worker_department(db: AsyncSession):

    stmt = select(EmployeeDetails, Departments).join(
        Departments, EmployeeDetails.department_uuid == Departments.department_uuid
    )

    result = await db.execute(stmt)
    data = result.all()

    dept_map = defaultdict(lambda: {"permanent": 0, "contingent": 0})

    for emp, dept in data:
        if emp.employment_type == "Full-Time":
            dept_map[dept.department_name]["permanent"] += 1
        else:
            dept_map[dept.department_name]["contingent"] += 1

    return [{"dept": k, **v} for k, v in dept_map.items()]


# ---------------- GENDER BY DEPT ----------------
async def get_gender_department(db: AsyncSession):

    stmt = select(EmployeeDetails, Departments).join(
        Departments, EmployeeDetails.department_uuid == Departments.department_uuid
    )

    result = await db.execute(stmt)
    data = result.all()

    dept_map = defaultdict(lambda: {"female": 0, "male": 0})

    for emp, dept in data:
        if emp.gender:
            dept_map[dept.department_name][emp.gender.lower()] += 1

    return [{"dept": k, **v} for k, v in dept_map.items()]


# ---------------- EMPLOYMENT BY DEPT ----------------
async def get_employment_department(db: AsyncSession):

    stmt = select(EmployeeDetails, Departments).join(
        Departments, EmployeeDetails.department_uuid == Departments.department_uuid
    )

    result = await db.execute(stmt)
    data = result.all()

    dept_map = defaultdict(lambda: {"full": 0})

    for emp, dept in data:
        if emp.employment_type == "Full-Time":
            dept_map[dept.department_name]["full"] += 1

    return [{"dept": k, **v} for k, v in dept_map.items()]