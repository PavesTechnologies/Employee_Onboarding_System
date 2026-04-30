# Backend/API_Layer/routes/employee_details_routes.py
from time import perf_counter
from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, UploadFile
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.utils.dependencies import get_db
from ..interfaces.employee_details_interfaces import (PersonalDetails, DeleteEmployeeIdentityResponse, PersonalDetailsRequest, PersonalDetailsResponse, PersonalDetails,
                                                      UpdatePersonalRequest, CreateAddressRequest, CreateAddressResponse,
                                                      AddressDetails, EmployeeIdentityResponse, SocialLinkRequest, SocialLinkResponse, SocialLinkDetails, EmployeeAboutResponse, EmployeeAboutRequest, EmployeeAboutDetails)
from ...Business_Layer.services.employee_details_service import EmployeeDetailsService, AddressService, EmployeeIdentityService, EmployeeSocialLinkService, EmployeeAboutService
from datetime import date
from ..utils.role_based import require_roles
import time
from time import perf_counter
router = APIRouter()


@router.get("", response_model = list[PersonalDetails])
async def get_all_personal_details(db: AsyncSession = Depends(get_db)):
    try:
        employee_service = EmployeeDetailsService(db)
        result = await employee_service.get_all_personal_details()
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/about/{employee_uuid}", response_model=EmployeeAboutDetails)
async def get_employee_about(
    employee_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        about_service = EmployeeAboutService(db)
        return await about_service.get_employee_about(employee_uuid)

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/about", response_model=EmployeeAboutResponse)
async def save_employee_about(
    request_data: EmployeeAboutRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        about_service = EmployeeAboutService(db)

        result = await about_service.save_employee_about(
            request_data.employee_uuid,
            request_data
        )

        return EmployeeAboutResponse(
            employee_about_uuid=result.employee_about_uuid,
            message="Employee About Details Saved Successfully"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/about/{employee_uuid}", response_model=EmployeeAboutResponse)
async def update_employee_about(
    employee_uuid: str,
    request_data: EmployeeAboutRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        about_service = EmployeeAboutService(db)

        result = await about_service.save_employee_about(
            employee_uuid,
            request_data
        )

        return EmployeeAboutResponse(
            employee_about_uuid=result.employee_about_uuid,
            message="Employee About Details Updated Successfully"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/about/{employee_uuid}", response_model=EmployeeAboutResponse)
async def delete_employee_about(
    employee_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        about_service = EmployeeAboutService(db)
        result = await about_service.delete_employee_about(employee_uuid)
        return EmployeeAboutResponse(
            employee_about_uuid=result.employee_about_uuid,
            message="Employee About Details Deleted Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/{personal_uuid}", response_model = PersonalDetails)
async def get_personal_details_by_user_uuid(personal_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        employee_service = EmployeeDetailsService(db)
        result = await employee_service.get_personal_details_by_user_uuid(personal_uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/{personal_uuid}", response_model = PersonalDetailsResponse)
async def update_personal_details(personal_uuid: str, request_data: UpdatePersonalRequest, db: AsyncSession = Depends(get_db)):
    try:
        start = perf_counter()
        employee_service = EmployeeDetailsService(db)
        result = await employee_service.update_personal_details(personal_uuid, request_data)
        end = perf_counter()
        print("Total API time:", end - start)
        return PersonalDetailsResponse(
            personal_uuid = result["personal_uuid"],
            message = "Personal Details Updated Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.delete("/{personal_uuid}", response_model = PersonalDetailsResponse)
async def delete_personal_details(personal_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        employee_service = EmployeeDetailsService(db)
        await employee_service.delete_personal_details(personal_uuid)
        return PersonalDetailsResponse(
            personal_uuid = personal_uuid,
            message = "Personal Details Deleted Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    
@router.get("/address/", response_model = list[AddressDetails], )
async def get_all_addresses(db: AsyncSession = Depends(get_db)):
    try:
        address_service = AddressService(db)
        result = await address_service.get_all_addresses()
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/address/{address_uuid}", response_model = AddressDetails, )
async def get_address_by_address_uuid(address_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        address_service = AddressService(db)
        result = await address_service.get_address_by_address_uuid(address_uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.put("/address/{address_uuid}", response_model = CreateAddressResponse, )
async def update_address(address_uuid: str, request_data: CreateAddressRequest, db: AsyncSession = Depends(get_db)):
    try:
        address_service = AddressService(db)
        result = await address_service.update_address(address_uuid, request_data)
        return CreateAddressResponse(
            address_uuid = address_uuid,
            message = "Address Updated Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.delete("/address/{address_uuid}", response_model=CreateAddressResponse, )
async def delete_address(address_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        address_service = AddressService(db)
        await address_service.delete_address(address_uuid)
        return CreateAddressResponse(
            address_uuid = address_uuid,
            message = "Address Deleted Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.delete("/identity/{document_uuid}", response_model=DeleteEmployeeIdentityResponse, )
async def delete_employee_identity(document_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        employee_service = EmployeeIdentityService(db)
        await employee_service.delete_employee_identity(document_uuid)
        return DeleteEmployeeIdentityResponse(
            document_uuid=document_uuid,
            message="Employee Identity Document Deleted Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/social-links/{user_uuid}", response_model=list[SocialLinkDetails])
async def get_social_links(user_uuid: str, db: AsyncSession = Depends(get_db)):
    social_service = EmployeeSocialLinkService(db)
    return await social_service.get_social_links(user_uuid)


@router.post("/social-links", response_model=SocialLinkResponse)
async def create_social_link(
    request_data: SocialLinkRequest,
    db: AsyncSession = Depends(get_db)
):
    social_service = EmployeeSocialLinkService(db)
    result = await social_service.create_social_link(request_data.user_uuid, request_data)

    return SocialLinkResponse(
        social_link_uuid=result.social_link_uuid,
        message="Social Link Created Successfully"
    )


@router.put("/social-links/{social_link_uuid}", response_model=SocialLinkResponse)
async def update_social_link(
    social_link_uuid: str,
    request_data: SocialLinkRequest,
    db: AsyncSession = Depends(get_db)
):
    social_service = EmployeeSocialLinkService(db)
    await social_service.update_social_link(social_link_uuid, request_data)

    return SocialLinkResponse(
        social_link_uuid=social_link_uuid,
        message="Social Link Updated Successfully"
    )


@router.delete("/social-links/{social_link_uuid}", response_model=SocialLinkResponse)
async def delete_social_link(
    social_link_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    social_service = EmployeeSocialLinkService(db)
    await social_service.delete_social_link(social_link_uuid)

    return SocialLinkResponse(
        social_link_uuid=social_link_uuid,
        message="Social Link Deleted Successfully"
    )