from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.dao.hr_bulk_join_dao import HrBulkJoinDAO
from ...DAL.utils.dependencies import get_db
from  ...API_Layer.interfaces.bulk_join_request_interfaces import BulkJoinRequest,ReassignJoiningRequest
from ...Business_Layer.services.hr_bulk_join_service import HrBulkJoinService
from ..utils.role_based import require_roles

router = APIRouter()

@router.post("/offerletters/bulk-join", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def bulk_join(
    payload: BulkJoinRequest,
    request: Request,
   
    db: AsyncSession = Depends(get_db)
):
    try:
        
        current_user_id = int(request.state.user.get("user_id"))

        service = HrBulkJoinService(db)
          
        result = await service.process_bulk_join(payload, current_user_id)


        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.put("/offerletters/reassign-joining", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def reassign_joining(
    payload: ReassignJoiningRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        current_user_id = int(request.state.user.get("user_id"))

        service = HrBulkJoinService(db)

        result = await service.reassign_joining(payload, current_user_id)

        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/offerletters/{user_uuid}")
async def get_offer_details(user_uuid: str, db: AsyncSession = Depends(get_db)):

    dao = HrBulkJoinDAO(db)
    user = await dao.get_user_by_uuid(user_uuid)

    if not user:
        raise HTTPException(404, "User not found")

    return {
        "user_uuid": user.user_uuid,
        "joining_date": user.joining_date,
        "reporting_manager": user.reporting_manager,
    }