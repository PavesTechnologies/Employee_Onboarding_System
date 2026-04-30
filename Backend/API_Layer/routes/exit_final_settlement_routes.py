from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.utils.dependencies import get_db
from Backend.Business_Layer.services.exit_final_settlement_service import ExitFinalSettlementService
from Backend.API_Layer.interfaces.exit_final_settlement_interface import (
    ExitFinalSettlementCreate,
    ExitFinalSettlementApprove,
    ExitFinalSettlementPaid,
    ExitFinalSettlementResponse
)


router = APIRouter(
    prefix="/exit-settlement",
    tags=["Exit Final Settlement"]
)


# Create Settlement
@router.post("/create", response_model=ExitFinalSettlementResponse)
async def create_settlement(
    data: ExitFinalSettlementCreate,
    db: AsyncSession = Depends(get_db)
):

    service = ExitFinalSettlementService()

    return await service.create_settlement(db, data)


# Get Settlement
@router.get("/{exit_uuid}", response_model=ExitFinalSettlementResponse)
async def get_settlement(
    exit_uuid: str,
    db: AsyncSession = Depends(get_db)
):

    service = ExitFinalSettlementService()

    return await service.get_settlement(db, exit_uuid)


# Approve Settlement
@router.put("/approve", response_model=ExitFinalSettlementResponse)
async def approve_settlement(
    data: ExitFinalSettlementApprove,
    request: Request,
    db: AsyncSession = Depends(get_db)
):

    user = request.state.user
    user_id = user.get("user_id")

    service = ExitFinalSettlementService()

    return await service.approve_settlement(
        db,
        data.settlement_uuid,
        user_id,
        data.remarks
    )


# Mark Paid
@router.put("/paid", response_model=ExitFinalSettlementResponse)
async def mark_paid(
    data: ExitFinalSettlementPaid,
    db: AsyncSession = Depends(get_db)
):

    service = ExitFinalSettlementService()

    return await service.mark_paid(
        db,
        data.settlement_uuid
    )