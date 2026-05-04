from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import aliased

from Backend.API_Layer.utils.role_based import require_roles
from Backend.API_Layer.utils.role_based import require_roles
from Backend.DAL.utils.dependencies import get_db

from Backend.DAL.models.models import (
    EmployeeDetails,
    OfferLetterDetails,
    EmployeeExit,
    Designations
)

router = APIRouter(
)


@router.get("/resources",dependencies=[Depends(require_roles("resource_manager"))])
async def get_rms_resources(
    db: AsyncSession = Depends(get_db)
):
    
    # Alias for Reporting Manager
    ManagerEmployee = aliased(EmployeeDetails)

    stmt = (
        select(

            EmployeeDetails.employee_id.label("resource_id"),

            func.trim(
                func.concat(
                    EmployeeDetails.first_name,
                    " ",
                    func.coalesce(EmployeeDetails.middle_name, ""),
                    " ",
                    EmployeeDetails.last_name
                )
            ).label("full_name"),

            EmployeeDetails.work_email.label("email"),

            EmployeeDetails.employment_type.label("employment_type"),

            Designations.designation_name.label("designation"),

            EmployeeDetails.location.label("working_location"),

            EmployeeDetails.total_experience.label("experience"),

            EmployeeDetails.employment_status.label("active_flag"),

            EmployeeDetails.created_at.label("created_at"),

            EmployeeDetails.updated_at.label("updated_at"),

            EmployeeDetails.created_by.label("created_by"),

            EmployeeDetails.work_mode.label("work_mode"),

            OfferLetterDetails.total_ctc.label("annual_ctc"),

            OfferLetterDetails.currency.label("currency_type"),

            OfferLetterDetails.joining_date.label("date_of_joining"),

            EmployeeDetails.reporting_manager_uuid.label("reporting_manager_uuid"),

            EmployeeExit.notice_start_date.label("notice_start_date"),

            EmployeeExit.notice_end_date.label("notice_end_date"),

            EmployeeExit.last_working_day.label("date_of_exit")

        )

        .outerjoin(
            OfferLetterDetails,
            EmployeeDetails.user_uuid == OfferLetterDetails.user_uuid
        )

        .outerjoin(
            Designations,
            EmployeeDetails.designation_uuid == Designations.designation_uuid
        )

        .outerjoin(
            EmployeeExit,
            EmployeeDetails.employee_uuid == EmployeeExit.employee_uuid
        )

       
    )


    result = await db.execute(stmt)

    resources = result.fetchall()

    response = []

    for resource in resources:

        response.append({

            "resource_id": resource.resource_id,

            "full_name": resource.full_name,

            "email": resource.email,

            "employment_type": resource.employment_type,

            "designation": resource.designation,

            "working_location": resource.working_location,

            "experience": float(resource.experience)
            if resource.experience else None,

            "active_flag": resource.active_flag,

            "created_at": resource.created_at,

            "updated_at": resource.updated_at,

            "created_by": resource.created_by,

            "work_mode": resource.work_mode,

            "reporting_manager_uuid": resource.reporting_manager_uuid,

            "annual_ctc": float(resource.annual_ctc)
            if resource.annual_ctc else None,

            "currency_type": resource.currency_type,

            "date_of_joining": resource.date_of_joining,

            "notice_start_date": resource.notice_start_date,

            "notice_end_date": resource.notice_end_date,

            "date_of_exit": resource.date_of_exit

        })

    return {
        "success": True,
        "message": "RMS resources fetched successfully",
        "data": response
    }