from collections import Counter, defaultdict
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.models.models import (
    Countries,
    Departments,
    Designations,
    EmployeeDetails,
    OfferLetterDetails,
    PersonalDetails,
)


AGE_BUCKETS = (
    ("18-21", 18, 21),
    ("22-25", 22, 25),
    ("26-30", 26, 30),
    ("31-40", 31, 40),
    ("41-55", 41, 55),
)

EXPERIENCE_BUCKETS = (
    ("0-1", 0, 1),
    ("1-2", 1, 2),
    ("2-5", 2, 5),
    ("5-10", 5, 10),
    ("10+", 10, None),
)

EMPLOYMENT_TYPE_KEYS = {
    "full-time": ("Full-Time", "full"),
    "part-time": ("Part-Time", "partTime"),
    "intern": ("Intern", "intern"),
    "contract": ("Contract", "contract"),
    "contractor": ("Contract", "contract"),
    "freelance": ("Freelance", "freelance"),
}


def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def normalize_gender(*values):
    for value in values:
        if not value:
            continue

        gender = str(value).strip().lower()
        if gender in {"male", "m"}:
            return "male"
        if gender in {"female", "f"}:
            return "female"
        if gender:
            return "other"

    return None


def normalize_employment_type(value):
    if not value:
        return None, None

    normalized = str(value).strip().lower()
    return EMPLOYMENT_TYPE_KEYS.get(normalized, (str(value).strip(), normalized))


def worker_type_for_employment(employment_type):
    if not employment_type:
        return None

    return "Permanent" if employment_type == "Full-Time" else "Contingent"


def empty_age_groups():
    return {label: {"female": 0, "male": 0} for label, _, _ in AGE_BUCKETS}


def age_bucket_for(dob):
    if not dob:
        return None

    age = calculate_age(dob)
    for label, start, end in AGE_BUCKETS:
        if start <= age <= end:
            return label

    return None


def experience_bucket_for(total_experience):
    if total_experience is None:
        return None

    years = float(total_experience)
    if years < 0:
        return None

    for label, start, end in EXPERIENCE_BUCKETS:
        if end is None and years > start:
            return label
        if end is not None and start <= years <= end:
            return label

    return None


def department_name(dept):
    if dept and dept.department_name:
        return dept.department_name

    return "Unassigned"


def employee_type_for(emp, offer):
    return (offer.employee_type if offer and offer.employee_type else None) or emp.employment_type


# ---------------- DEMOGRAPHICS ----------------
async def get_demographics(db: AsyncSession):

    stmt = (
        select(EmployeeDetails, OfferLetterDetails, PersonalDetails, Countries, Departments, Designations)
        .select_from(EmployeeDetails)
        .outerjoin(OfferLetterDetails, EmployeeDetails.user_uuid == OfferLetterDetails.user_uuid)
        .outerjoin(PersonalDetails, EmployeeDetails.user_uuid == PersonalDetails.user_uuid)
        .outerjoin(Countries, PersonalDetails.nationality_country_uuid == Countries.country_uuid)
        .outerjoin(Departments, EmployeeDetails.department_uuid == Departments.department_uuid)
        .outerjoin(Designations, EmployeeDetails.designation_uuid == Designations.designation_uuid)
    )

    result = await db.execute(stmt)
    data = result.all()

    gender_counter = Counter()
    nationality_counter = Counter()
    employment_counter = Counter()
    worker_counter = Counter()

    age_groups = empty_age_groups()

    experience_counter = {label: 0 for label, _, _ in EXPERIENCE_BUCKETS}

    for emp, offer, personal, country, _dept, _designation in data:
        gender = normalize_gender(
            personal.gender if personal else None,
            emp.gender,
        )

        if gender:
            gender_counter[gender.capitalize()] += 1

        nationality_counter[country.country_name if country and country.country_name else "Unknown"] += 1

        employment_type, _employment_key = normalize_employment_type(employee_type_for(emp, offer))
        if employment_type:
            employment_counter[employment_type] += 1
            worker_counter[worker_type_for_employment(employment_type)] += 1

        age_group = age_bucket_for((personal.date_of_birth if personal else None) or emp.date_of_birth)
        if age_group and gender in {"male", "female"}:
            age_groups[age_group][gender] += 1

        experience_group = experience_bucket_for(emp.total_experience)
        if experience_group:
            experience_counter[experience_group] += 1

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

    stmt = (
        select(EmployeeDetails, OfferLetterDetails, Departments, Designations)
        .select_from(EmployeeDetails)
        .outerjoin(OfferLetterDetails, EmployeeDetails.user_uuid == OfferLetterDetails.user_uuid)
        .outerjoin(Departments, EmployeeDetails.department_uuid == Departments.department_uuid)
        .outerjoin(Designations, EmployeeDetails.designation_uuid == Designations.designation_uuid)
    )

    result = await db.execute(stmt)
    data = result.all()

    dept_map = defaultdict(lambda: {"permanent": 0, "contingent": 0})

    for emp, offer, dept, _designation in data:
        dept_name = department_name(dept)
        employment_type, _employment_key = normalize_employment_type(employee_type_for(emp, offer))
        worker_type = worker_type_for_employment(employment_type)
        if worker_type == "Permanent":
            dept_map[dept_name]["permanent"] += 1
        elif worker_type == "Contingent":
            dept_map[dept_name]["contingent"] += 1

    return [{"dept": k, **v} for k, v in dept_map.items()]


# ---------------- GENDER BY DEPT ----------------
async def get_gender_department(db: AsyncSession):

    stmt = (
        select(EmployeeDetails, PersonalDetails, Departments, Designations)
        .select_from(EmployeeDetails)
        .outerjoin(PersonalDetails, EmployeeDetails.user_uuid == PersonalDetails.user_uuid)
        .outerjoin(Departments, EmployeeDetails.department_uuid == Departments.department_uuid)
        .outerjoin(Designations, EmployeeDetails.designation_uuid == Designations.designation_uuid)
    )

    result = await db.execute(stmt)
    data = result.all()

    dept_map = defaultdict(lambda: {"female": 0, "male": 0})

    for emp, personal, dept, _designation in data:
        gender = normalize_gender(
            personal.gender if personal else None,
            emp.gender,
        )
        if gender in {"male", "female"}:
            dept_map[department_name(dept)][gender] += 1

    return [{"dept": k, **v} for k, v in dept_map.items()]


# ---------------- EMPLOYMENT BY DEPT ----------------
async def get_employment_department(db: AsyncSession):

    stmt = (
        select(EmployeeDetails, OfferLetterDetails, Departments, Designations)
        .select_from(EmployeeDetails)
        .outerjoin(OfferLetterDetails, EmployeeDetails.user_uuid == OfferLetterDetails.user_uuid)
        .outerjoin(Departments, EmployeeDetails.department_uuid == Departments.department_uuid)
        .outerjoin(Designations, EmployeeDetails.designation_uuid == Designations.designation_uuid)
    )

    result = await db.execute(stmt)
    data = result.all()

    dept_map = defaultdict(
        lambda: {
            "full": 0,
            "partTime": 0,
            "intern": 0,
            "contract": 0,
            "freelance": 0,
        }
    )

    for emp, offer, dept, _designation in data:
        _employment_type, employment_key = normalize_employment_type(employee_type_for(emp, offer))
        if employment_key in dept_map[department_name(dept)]:
            dept_map[department_name(dept)][employment_key] += 1

    return [{"dept": k, **v} for k, v in dept_map.items()]
