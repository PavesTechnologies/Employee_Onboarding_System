from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.utils.dependencies import get_db
from ..interfaces.employee_details_interfaces import (
    CreateAddressRequest,
    CreateAddressResponse,
    EmployeeIdentityResponse,
    PersonalDetailsRequest,
    PersonalDetailsResponse,
    CreateRelationRequest,
    CreateRelationResponse,
)
from ...Business_Layer.services.employee_upload_service import EmployeeUploadService

router = APIRouter()


@router.post("/personal-details", response_model=PersonalDetailsResponse)
async def create_personal_details(
    request_data: PersonalDetailsRequest, db: AsyncSession = Depends(get_db)
):
    try:
        employee_service = EmployeeUploadService(db)
        result = await employee_service.create_personal_details(request_data)

        return PersonalDetailsResponse(
            personal_uuid=result.personal_uuid,
            message="Personal Details Created Successfully",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # 👈 show real error

    ## Addresses Routes ##


@router.post("/address", response_model=CreateAddressResponse)
async def create_address(
    request_data: CreateAddressRequest, db: AsyncSession = Depends(get_db)
):
    try:
        address_service = EmployeeUploadService(db)
        result = await address_service.create_address(request_data)
        return CreateAddressResponse(
            address_uuid=result.address_uuid, message="Address Created Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/address/{address_uuid}", response_model=CreateAddressResponse)
async def update_address(
    address_uuid: str,
    request_data: CreateAddressRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        address_service = EmployeeUploadService(db)
        result = await address_service.update_address(address_uuid, request_data)
        if result is None:
            raise HTTPException(status_code=404, detail="Address not found")
        return CreateAddressResponse(
            address_uuid=result.address_uuid, message="Address Updated Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Employee Identity Document Routes #


@router.post("/identity-documents", response_model=EmployeeIdentityResponse)
async def create_employee_identity(
    mapping_uuid: str = Form(...),
    user_uuid: str = Form(...),
    identity_file_number: str = Form(...),
    expiry_date: Optional[date] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        employee_service = EmployeeUploadService(db)

        result = await employee_service.create_employee_identity(
            mapping_uuid=mapping_uuid,
            user_uuid=user_uuid,
            identity_file_number=identity_file_number,
            expiry_date=expiry_date,
            file=file,
        )

        return EmployeeIdentityResponse(
            identity_uuid=result.document_uuid,
            identity_file_number=result.identity_file_number,
            file_path=result.file_path,
            message="Employee Identity Document Created Successfully",
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.put("/identity-documents/{identity_uuid}", response_model=EmployeeIdentityResponse)
# async def update_employee_identity(
#     identity_uuid: str,
#     mapping_uuid: str = Form(...),
#     user_uuid: str = Form(...),
#     identity_file_number: str = Form(...),
#     expiry_date: Optional[date] = Form(None),
#     file: Optional[UploadFile] = File(None),
#     db: AsyncSession = Depends(get_db),
# ):
#     try:
#         employee_service = EmployeeUploadService(db)

#         result = await employee_service.update_employee_identity(
#             identity_uuid=identity_uuid,
#             mapping_uuid=mapping_uuid,
#             user_uuid=user_uuid,
#             identity_file_number=identity_file_number,
#             expiry_date=expiry_date,
#             file=file
#         )

#         return EmployeeIdentityResponse(
#             identity_uuid=result.document_uuid,
#             identity_file_number=result.identity_file_number,
#             file_path=result.file_path,
#             message="Employee Identity Document Updated Successfully"
#         )

#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.put("/identity-documents/{identity_uuid}")
async def update_employee_identity(
    identity_uuid: str,
    mapping_uuid: str = Form(...),
    user_uuid: str = Form(...),
    identity_file_number: str = Form(...),
    expiry_date: Optional[date] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    service = EmployeeUploadService(db)

    result = await service.update_employee_identity(
        identity_uuid=identity_uuid,
        mapping_uuid=mapping_uuid,
        user_uuid=user_uuid,
        identity_file_number=identity_file_number,
        expiry_date=expiry_date,
        file=file,
    )

    if not result:
        raise HTTPException(status_code=404, detail="Update failed")

    return {
        "identity_uuid": result.document_uuid,
        "file_path": result.file_path,
    }


@router.post("/relations")
async def create_relation(
    request_data: CreateRelationRequest, db: AsyncSession = Depends(get_db)
):
    try:
        relation_service = EmployeeUploadService(db)
        result = await relation_service.create_relation(request_data)
        return CreateRelationResponse(
            relation_uuid=result.relation_uuid, message="Relation Created Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/relations")
async def get_relations(db: AsyncSession = Depends(get_db)):
    try:
        relation_service = EmployeeUploadService(db)
        result = await relation_service.get_relations(db)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
