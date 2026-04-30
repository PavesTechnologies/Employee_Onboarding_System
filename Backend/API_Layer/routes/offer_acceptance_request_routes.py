from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy.ext.asyncio import AsyncSession


from ...Business_Layer.services.offer_approval_service import OfferApprovalRequestService
from ...API_Layer.interfaces.offer_request_interfaces import OfferRequestCreateResponse, OfferRequestUpdateResponse, OfferRequestDelete,OfferRequestListResponse,OfferRequestUpdateResponse2

from ...DAL.utils.dependencies import get_db
from ..utils.role_based import require_roles

router = APIRouter()

@router.post("/request", dependencies=[Depends(require_roles("HR"))])
async def create_offer_approval_requests(
    payload: list[OfferRequestListResponse],
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    HR sends offer approval request(s) to higher authority
    """
    service = OfferApprovalRequestService(db)

    current_user_id = int(request.state.user.get("user_id"))  # Access user info from request state
    print("current user id:", current_user_id)

    print("payload:", payload)

    updated_payload = []
    for item in payload:
        updated_payload.append(
            OfferRequestCreateResponse(
                user_uuid=item.user_uuid,
                request_by=current_user_id,   # 👈 HR id
                action_taker_id=item.action_taker_id
            )
        )

    print("updated payload:", updated_payload)

    result = await service.create_offer_approval_requests(updated_payload)

    if not result:
        raise HTTPException(
            status_code=400,
            detail="Failed to create offer approval requests"
        )

    return result

@router.put("/request/update", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def update_offer_approval_requests(
    payload: list[OfferRequestUpdateResponse2],
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    HR updates existing offer approval requests (bulk)
    """
    service = OfferApprovalRequestService(db)

    current_user_id = int(request.state.user.get("user_id"))

    return await service.update_offer_approval_requests(
        data_list=payload,
        current_user_id=current_user_id
    )

@router.delete("/request/delete", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def delete_offer_approval_requests(
    payload: list[OfferRequestDelete],
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    HR deletes offer approval requests (bulk)
    """
    service = OfferApprovalRequestService(db)

    current_user_id = int(request.state.user.get("user_id"))

    return await service.delete_offer_approval_requests(
        data_list=payload,
        current_user_id=current_user_id
    )