from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.utils.dependencies import get_db
from Backend.Business_Layer.services.exit_approval_service import ExitApprovalService
from Backend.API_Layer.interfaces.exit_approval_interface import ExitApprovalCreate

router = APIRouter(
    prefix="/exit-approvals",
    tags=["Exit Approvals"]
)


@router.post("/create")
async def create_exit_approval(
    data: ExitApprovalCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = ExitApprovalService()
        result = await service.create_exit_approval(db, data)
        return result

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))