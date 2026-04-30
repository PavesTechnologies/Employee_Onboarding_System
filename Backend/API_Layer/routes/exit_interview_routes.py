from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.utils.dependencies import get_db
from Backend.Business_Layer.services.exit_interview_service import ExitInterviewService
from Backend.API_Layer.interfaces.exit_interview_interface import (
    ExitInterviewCreate,
    ExitInterviewUpdate,
    ExitInterviewResponse
)

router = APIRouter(
    prefix="/exit-interview",
    tags=["Exit Interview"]
)


@router.post("/create", response_model=ExitInterviewResponse)
async def create_exit_interview(
    data: ExitInterviewCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = ExitInterviewService()
        result = await service.create_exit_interview(db, data)
        return result

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{interview_uuid}", response_model=ExitInterviewResponse)
async def get_exit_interview(
    interview_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = ExitInterviewService()
        return await service.get_exit_interview(db, interview_uuid)

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{interview_uuid}", response_model=ExitInterviewResponse)
async def update_exit_interview(
    interview_uuid: str,
    data: ExitInterviewUpdate,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = ExitInterviewService()
        return await service.update_exit_interview(
            db, interview_uuid, data
        )

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{interview_uuid}")
async def delete_exit_interview(
    interview_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = ExitInterviewService()
        return await service.delete_exit_interview(
            db, interview_uuid
        )

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))