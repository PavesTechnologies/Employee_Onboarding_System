from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from time import perf_counter

from ...DAL.utils.dependencies import get_db
from ..interfaces.employee_pf_interfaces import (
    CreatePfDetailsRequest,
    CreatePfDetailsResponse,
    PfDetails
)

from ...Business_Layer.services.employee_pf_service import EmployeePfService

router = APIRouter()


@router.get("/pf", response_model=list[PfDetails])
async def get_all_pf_details(db: AsyncSession = Depends(get_db)):
    try:
        pf_service = EmployeePfService(db)
        result = await pf_service.get_all_pf_details()
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pf/{pf_uuid}", response_model=PfDetails)
async def get_pf_details_by_uuid(pf_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        pf_service = EmployeePfService(db)
        result = await pf_service.get_pf_details_by_uuid(pf_uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pf", response_model=CreatePfDetailsResponse)
async def create_pf_details(request_data: CreatePfDetailsRequest, db: AsyncSession = Depends(get_db)):
    try:
        start = perf_counter()

        pf_service = EmployeePfService(db)
        result = await pf_service.create_pf_details(request_data)

        end = perf_counter()
        print("PF API Time:", end - start)

        return CreatePfDetailsResponse(
            pf_uuid=result["pf_uuid"],
            message="PF Details Created Successfully"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/pf/{pf_uuid}", response_model=CreatePfDetailsResponse)
async def update_pf_details(pf_uuid: str, request_data: CreatePfDetailsRequest, db: AsyncSession = Depends(get_db)):
    try:
        pf_service = EmployeePfService(db)
        result = await pf_service.update_pf_details(pf_uuid, request_data)

        return CreatePfDetailsResponse(
            pf_uuid=pf_uuid,
            message="PF Details Updated Successfully"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/pf/{pf_uuid}", response_model=CreatePfDetailsResponse)
async def delete_pf_details(pf_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        pf_service = EmployeePfService(db)
        await pf_service.delete_pf_details(pf_uuid)

        return CreatePfDetailsResponse(
            pf_uuid=pf_uuid,
            message="PF Details Deleted Successfully"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))