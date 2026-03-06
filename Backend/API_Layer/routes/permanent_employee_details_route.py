from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.API_Layer.interfaces.permenent_employee_details_interfaces import CreatePermanentEmployeeRequest, CreatePermanentEmployeeResponse, UpdatePermanentEmployeeRequest
from Backend.Business_Layer.services.permanent_employee_details_service import PermanentEmployeeDetailsService

from ...DAL.utils.dependencies import get_db

router = APIRouter(
    prefix="/core-employee-details",
    tags=["Permanent Employees"]
)

service = PermanentEmployeeDetailsService()


@router.post("/", response_model=CreatePermanentEmployeeResponse)
async def create_employee(
        request: CreatePermanentEmployeeRequest,
        db: AsyncSession = Depends(get_db)
):

    try:

        return await service.create_employee(db, request)

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@router.get("/{employee_uuid}")
async def get_employee(
            employee_uuid: str,
            db: AsyncSession = Depends(get_db)
            ):
            try:
                return await service.get_employee_by_uuid(db, employee_uuid)

            except ValueError as e:
                raise HTTPException(
                    status_code=404,
                    detail=str(e)
                )
@router.get("/")
async def get_all_employees(
    db: AsyncSession = Depends(get_db)
):
    return await service.get_all_employees(db)

@router.put("/{employee_uuid}")
async def update_employee(
    employee_uuid: str,
    request: UpdatePermanentEmployeeRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await service.update_employee(db, employee_uuid, request)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
            
@router.delete("/{employee_uuid}")
async def delete_employee(
    employee_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await service.delete_employee(db, employee_uuid)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
