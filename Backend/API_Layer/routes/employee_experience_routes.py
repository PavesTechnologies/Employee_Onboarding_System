from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import List
from Backend.API_Layer.interfaces.employee_experience_interfaces import (
    ExperienceCreateRequest,
    ExperienceResponse,
    ExperienceCreateResponse,
    EmploymentType,
    ExperienceUpdate,
)

from ...DAL.utils.dependencies import get_db
from ...Business_Layer.services.employee_experience_service import EmployeeExperienceService
from ...DAL.utils.storage_utils import get_storage_service  # If needed for presigned URL
from ..utils.role_based import require_roles

router = APIRouter()

# -------------------------------------------------------
# CREATE EXPERIENCE
# -------------------------------------------------------
# @router.post("/", dependencies=[Depends(require_roles("HR", "ADMIN"))])
@router.post("/", response_model=ExperienceCreateResponse)
async def create_experience(
    employee_uuid: str = Form(...),
    company_name: str = Form(...),
    role_title: str | None = Form(None),
    employment_type: EmploymentType = Form(...),
    start_date: date = Form(...),
    end_date: date | None = Form(None),
    is_current: bool = Form(False),
    notice_period_days: int | None = Form(None, ge=0, le=120),

    doc_types: List[str] = Form(...),
    files: List[UploadFile] = File(...),

    db: AsyncSession = Depends(get_db),
):
    if is_current and end_date:
        raise HTTPException(
            status_code=400,
            detail="Current job cannot have end date"
        )

    if is_current and notice_period_days is None:
        raise HTTPException(
            status_code=400,
            detail="Notice period required for current job"
        )

    if len(doc_types) != len(files):
        raise HTTPException(
            status_code=400,
            detail="doc_types and files count must match"
        )

    request_data = ExperienceCreateRequest(
        employee_uuid=employee_uuid,
        company_name=company_name,
        role_title=role_title,
        employment_type=employment_type,
        start_date=start_date,
        end_date=end_date,
        is_current=is_current,
        notice_period_days=notice_period_days,
    )

    service = EmployeeExperienceService(db)
    return await service.create_experience(request_data, doc_types, files)


# -------------------------------------------------------
# GET ALL EXPERIENCE RECORDS
# -------------------------------------------------------
@router.get("/", response_model=list[ExperienceResponse])
async def get_all_experience(db: AsyncSession = Depends(get_db)):
    try:
        service = EmployeeExperienceService(db)
        result = await service.get_all_experience()
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------
# GET EXPERIENCE BY EMPLOYEE UUID
# -------------------------------------------------------
@router.get("/employee/{employee_uuid}", response_model=list[ExperienceResponse])
async def get_experience_by_employee_uuid(employee_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        service = EmployeeExperienceService(db)
        result = await service.get_experience_by_employee_uuid(employee_uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------
# GET EXPERIENCE BY UUID
# -------------------------------------------------------
@router.get("/{experience_uuid}", response_model=ExperienceResponse)
async def get_experience_by_uuid(experience_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        service = EmployeeExperienceService(db)
        result = await service.get_experience_by_uuid(experience_uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------
# UPDATE EXPERIENCE DETAILS + CERTIFICATES
# -------------------------------------------------------
@router.put("/{experience_uuid}", response_model=ExperienceCreateResponse)
async def update_experience(
    experience_uuid: str,

    company_name: str = Form(...),
    role_title: str | None = Form(None),
    employment_type: EmploymentType = Form(...),
    start_date: date = Form(...),
    end_date: date | None = Form(None),
    is_current: bool = Form(False),
    notice_period_days: int | None = Form(None, ge=0, le=120),

    doc_types: List[str] = Form([]),
    files: List[UploadFile] | None = File(None),

    db: AsyncSession = Depends(get_db),
):

    if is_current and end_date:
        raise HTTPException(
            status_code=400,
            detail="Current job cannot have end date"
        )

    if is_current and notice_period_days is None:
        raise HTTPException(
            status_code=400,
            detail="Notice period required for current job"
        )

    if files and len(doc_types) != len(files):
        raise HTTPException(
            status_code=400,
            detail="doc_types and files count must match"
        )

    service = EmployeeExperienceService(db)

    return await service.update_experience_with_files(
        experience_uuid,
        company_name,
        role_title,
        employment_type,
        start_date,
        end_date,
        is_current,
        notice_period_days,
        doc_types,
        files,
    )


# ------------------------------------------------------
# UPDATE CERTIFICATES
# ------------------------------------------------------
@router.put("/certificate/{experience_uuid}/", response_model=ExperienceCreateResponse)
async def update_experience_certificate(
    experience_uuid: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        service = EmployeeExperienceService(db)

        result = await service.update_experience_certificate(
            experience_uuid=experience_uuid,
            file=file
        )

        return ExperienceCreateResponse(
            experience_uuid=result.experience_uuid,
            message="Experience certificate updated successfully",
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------
# DELETE EXPERIENCE + S3 FILE
# -------------------------------------------------------
@router.delete("/{experience_uuid}", response_model=ExperienceCreateResponse)
async def delete_experience(experience_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        service = EmployeeExperienceService(db)
        result = await service.delete_experience(experience_uuid)

        return ExperienceCreateResponse(
            experience_uuid=result.experience_uuid,
            message="Experience record deleted successfully"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------
# GET PRESIGNED URL (DOWNLOAD EXPERIENCE CERTIFICATE)
# -------------------------------------------------------
# @router.get("/{experience_uuid}/certificate-url", response_model=ExperienceResponse, dependencies=[Depends(require_roles("HR", "ADMIN"))])
# async def get_certificate_presigned_url(
#     experience_uuid: str,
#     db: AsyncSession = Depends(get_db)
# ):
#     service = EmployeeExperienceService(db)
#     storage = get_storage_service()

#     experience = await service.get_experience_by_uuid(experience_uuid)

#     if not experience.exp_certificate_path:
#         raise HTTPException(status_code=404, detail="No certificate uploaded")

#     url = await storage.get_presigned_url(experience.exp_certificate_path)

#     return {"url": url}


# -------------------------------------------------------
# DELETE CERTIFICATE ONLY
# -------------------------------------------------------
# @router.delete("/certificate/{experience_uuid}", dependencies=[Depends(require_roles("HR", "ADMIN"))])
# async def delete_certificate(experience_uuid: str, db: AsyncSession = Depends(get_db)):
#     service = EmployeeExperienceService(db)
#     storage = get_storage_service()

#     experience = await service.get_experience_by_uuid(experience_uuid)

#     if experience.exp_certificate_path:
#         await storage.delete_file(experience.exp_certificate_path)
#         await service.dao.update_certificate_path(experience_uuid, None)

#     return {"message": "Certificate deleted successfully"}


@router.delete("/certificate/{experience_uuid}")
async def delete_certificate(experience_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        service = EmployeeExperienceService(db)
        result = await service.delete_certificate(experience_uuid)
        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))