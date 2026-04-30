import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...DAL.utils.dependencies import get_db
from Backend.DAL.models.models import EmployeeDetails

router = APIRouter()


@router.get("/employees/export-preview")
async def get_export_preview(
    db: AsyncSession = Depends(get_db)
):

    stmt = select(
        EmployeeDetails
    ).where(

        EmployeeDetails.export_status.in_([
            "NOT_EXPORTED",
            "FAILED"
        ])

    ).order_by(
        EmployeeDetails.created_at.desc()
    )

    result = await db.execute(stmt)

    employees = result.scalars().all()

    response = []

    for emp in employees:

        response.append({

            "employee_uuid":
                emp.employee_uuid,

            "employee_id":
                emp.employee_id,

            "first_name":
                emp.first_name,

            "last_name":
                emp.last_name,

            "mail":
                emp.work_email,

            "contact":
                emp.contact_number,

            "department_uuid":
                emp.department_uuid,

            "designation_uuid":
                emp.designation_uuid,

            "joining_date":
                str(emp.joining_date)
                if emp.joining_date
                else None,

            "employment_status":
                emp.employment_status,

            "export_status":
                emp.export_status,

            "export_error":
                emp.export_error
        })

    return {
        "success": True,
        "count": len(response),
        "data": response
    }

@router.post("/employees/update-export-status")
async def update_export_status(
    payload: dict,
    db: AsyncSession = Depends(get_db)
):

    try:

        # =========================
        # SUCCESS USERS
        # =========================

        for item in payload.get("success", []):

            stmt = select(
                EmployeeDetails
            ).where(

                EmployeeDetails.work_email ==
                item["mail"]

            )

            result = await db.execute(stmt)

            employee = result.scalars().first()

            if employee:

                employee.export_status = (
                    "SUCCESS"
                )

                employee.export_error = None

                employee.exported_at = (
                    datetime.datetime.utcnow()
                )

        # =========================
        # FAILED USERS
        # =========================

        for item in payload.get("failed", []):

            stmt = select(
                EmployeeDetails
            ).where(

                EmployeeDetails.work_email ==
                item["mail"]

            )

            result = await db.execute(stmt)

            employee = result.scalars().first()

            if employee:

                error_message = (
                    item.get("error", "")
                )

                # =========================
                # USER ALREADY EXISTS
                # =========================

                if (
                    "user already exists"
                    in error_message.lower()
                ):

                    employee.export_status = (
                        "ALREADY_EXISTS"
                    )

                    employee.export_error = None

                # =========================
                # ACTUAL FAILURE
                # =========================

                else:

                    employee.export_status = (
                        "FAILED"
                    )

                    employee.export_error = (
                        error_message
                    )

                employee.exported_at = (
                    datetime.datetime.utcnow()
                )

        # =========================
        # SAVE CHANGES
        # =========================

        await db.commit()

        return {

            "success": True,

            "message":
                "Export statuses updated successfully"

        }

    except Exception as e:

        await db.rollback()

        return {

            "success": False,

            "message": str(e)
        }