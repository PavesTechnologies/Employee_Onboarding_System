from sqlalchemy import select, func
from sqlalchemy.orm import aliased
from Backend.DAL.models.models import (
    OfferLetterDetails,
    EmployeeDetails,
    Departments,
    Designations,
)


async def get_dashboard_data_from_db(db, start_date, end_date):
    employee_department = aliased(Departments)
    employee_designation = aliased(Designations)
    employee_designation_department = aliased(Departments)
    offer_designation = aliased(Designations)
    offer_designation_department = aliased(Departments)

    stmt = (
        select(
            OfferLetterDetails,
            EmployeeDetails,
            func.coalesce(
                employee_department.department_name,
                employee_designation_department.department_name,
                offer_designation_department.department_name
            ).label("department_name")
        )
        .outerjoin(
            EmployeeDetails,
            OfferLetterDetails.user_uuid == EmployeeDetails.user_uuid
        )
        .outerjoin(
            employee_designation,
            EmployeeDetails.designation_uuid == employee_designation.designation_uuid
        )
        .outerjoin(
            employee_department,
            EmployeeDetails.department_uuid == employee_department.department_uuid
        )
        .outerjoin(
            employee_designation_department,
            employee_designation.department_uuid == employee_designation_department.department_uuid
        )
        .outerjoin(
            offer_designation,
            func.lower(func.trim(OfferLetterDetails.designation)) ==
            func.lower(func.trim(offer_designation.designation_name))
        )
        .outerjoin(
            offer_designation_department,
            offer_designation.department_uuid == offer_designation_department.department_uuid
        )
        .where(
            OfferLetterDetails.joining_date != None
        )
    )

    result = await db.execute(stmt)

    return result.all()   
