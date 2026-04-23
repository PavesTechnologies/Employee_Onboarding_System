from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.utils.dependencies import get_db
from Backend.Business_Layer.services.exit_clearance_items_service import ExitClearanceItemsService
from Backend.API_Layer.interfaces.exit_clearance_items_interface import (
    ExitClearanceItemUpdate,
    ExitClearanceItemResponse, 
    ExitClearanceItemCreate
)

router = APIRouter(
    prefix="/exit-clearance-items",
    tags=["Exit Clearance Items"]
)

@router.post("/create")
async def create_items(
    data: ExitClearanceItemCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = ExitClearanceItemsService()
        result = await service.create_items(db, data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@router.get("/{clearance_uuid}", response_model=list[ExitClearanceItemResponse])
async def get_items(
    clearance_uuid: str,
    db: AsyncSession = Depends(get_db)
):

    service = ExitClearanceItemsService()

    return await service.get_items(db, clearance_uuid)


@router.put("/update", response_model=ExitClearanceItemResponse)
async def update_item(
    data: ExitClearanceItemUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):

    try:
        user = request.state.user
        data.approved_by = user.get("user_id")
        service = ExitClearanceItemsService()
        result = await service.update_item(db, data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get(
    "/all",
    response_model=list[ExitClearanceItemResponse]
)
async def get_all_items(db: AsyncSession = Depends(get_db)):
    try:
        service = ExitClearanceItemsService()
        return await service.get_all_items(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
