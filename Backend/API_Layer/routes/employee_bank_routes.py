from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from time import perf_counter
import traceback

from ...DAL.utils.dependencies import get_db
from ..interfaces.employee_bank_interfaces import (
    CreateBankDetailsRequest,
    CreateBankDetailsResponse,
    BankDetails
)

from ...Business_Layer.services.employee_bank_service import EmployeeBankService

router = APIRouter()


@router.get("/", response_model=list[BankDetails])
async def get_all_bank_details(db: AsyncSession = Depends(get_db)):
    try:
        bank_service = EmployeeBankService(db)
        result = await bank_service.get_all_bank_details()
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_uuid}", response_model=BankDetails)
async def get_bank_details_by_user_uuid(user_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        bank_service = EmployeeBankService(db)
        result = await bank_service.get_bank_details_by_user_uuid(user_uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{bank_uuid}", response_model=BankDetails)
async def get_bank_details_by_uuid(bank_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        bank_service = EmployeeBankService(db)
        result = await bank_service.get_bank_details_by_uuid(bank_uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=CreateBankDetailsResponse)
async def create_bank_details(request_data: CreateBankDetailsRequest, db: AsyncSession = Depends(get_db)):
    try:
        start = perf_counter()

        bank_service = EmployeeBankService(db)
        result = await bank_service.create_bank_details(request_data)

        end = perf_counter()
        print("Bank API Time:", end - start)

        return CreateBankDetailsResponse(
            bank_uuid=result["bank_uuid"],
            message="Bank Details Created Successfully"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{bank_uuid}", response_model=CreateBankDetailsResponse)
async def update_bank_details(bank_uuid: str, request_data: CreateBankDetailsRequest, db: AsyncSession = Depends(get_db)):
    try:
        bank_service = EmployeeBankService(db)
        result = await bank_service.update_bank_details(bank_uuid, request_data)

        return CreateBankDetailsResponse(
            bank_uuid=bank_uuid,
            message="Bank Details Updated Successfully"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{bank_uuid}", response_model=CreateBankDetailsResponse)
async def delete_bank_details(bank_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        bank_service = EmployeeBankService(db)
        await bank_service.delete_bank_details(bank_uuid)

        return CreateBankDetailsResponse(
            bank_uuid=bank_uuid,
            message="Bank Details Deleted Successfully"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))