from Backend.API_Layer.interfaces.exit_clearance_interface import ExitClearanceUpdate
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.utils.dependencies import get_db
from Backend.Business_Layer.services.exit_clearance_service import ExitClearanceService
from Backend.API_Layer.interfaces.exit_clearance_interface import ExitClearanceResponse


router = APIRouter(
    prefix="/exit-clearance",
    tags=["Exit Clearance"]
)


# My Pending
@router.get(
    "/my-pending",
    response_model=list[ExitClearanceResponse]
)
async def get_my_pending(request: Request,db: AsyncSession = Depends(get_db)):
    try:
        user = request.state.user
        roles = [role.upper() for role in user.get("roles", [])]

        if "MANAGER" in roles:
            departments = ["Manager"]

        elif "HR" in roles:
            departments = ["HR", "Finance"]

        elif "ADMIN" in roles:
            departments = ["Admin", "IT"]

        else:
            return []

        service = ExitClearanceService()

        return await service.get_my_pending(
            db,
            departments
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@router.put(
    "/approve",
    response_model=ExitClearanceResponse
)
async def approve_clearance(
    data: ExitClearanceUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):

    try:

        user = request.state.user
        user_id = user.get("user_id")

        service = ExitClearanceService()

        return await service.update_clearance(
            db,
            data.clearance_uuid,
            data.status,
            data.remarks,
            user_id
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get(
    "/employee/{employee_uuid}",
    response_model=list[ExitClearanceResponse]
)
async def get_employee_clearances(employee_uuid: str,db: AsyncSession = Depends(get_db)):
    try:
        service = ExitClearanceService()
        return await service.get_employee_clearances(db, employee_uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get(
    "/history/{exit_uuid}",
    response_model=list[ExitClearanceResponse]
)
async def get_clearance_history(exit_uuid: str,db: AsyncSession = Depends(get_db)):
    try:
        service = ExitClearanceService()
        return await service.get_clearance_history(db, exit_uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get(
    "/all",
    response_model=list[ExitClearanceResponse]
)
async def get_all_clearances(db: AsyncSession = Depends(get_db)):
    try:
        service = ExitClearanceService()
        return await service.get_all_clearances(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


