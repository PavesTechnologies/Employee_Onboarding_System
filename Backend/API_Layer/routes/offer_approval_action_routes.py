from http.client import HTTPException
from Backend.API_Layer.interfaces.offer_approve_action_interfaces import OfferApproveActionRequest, OfferApproveActionResponse
from Backend.API_Layer.interfaces.offer_request_approve_resign import OfferReassignApprovalRequest, OfferReassignApprovalResponse
from Backend.Business_Layer.utils.ums_users_list import fetch_admin_users_reformed
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...Business_Layer.services.offer_approval_action_service import (
    OfferApprovalActionService
)
from ..utils.role_based import require_roles

from ...DAL.utils.dependencies import get_db
from ...API_Layer.interfaces.offer_request_interfaces import OfferRequestResponse
from ...API_Layer.interfaces.OfferActionAdmin_interfaces import OfferActionAdminResponse

router = APIRouter()
@router.get("/status/{user_uuid}",response_model=OfferRequestResponse, dependencies=[Depends(require_roles("HR", "Admin"))])
async def get_offer_approval_status(
    user_uuid: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Get approval status for an offer using user_uuid
    """

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Authorization token missing"
        )
    
    service = OfferApprovalActionService(db)
    return await service.get_offer_status(user_uuid=user_uuid, auth_header=auth_header)

@router.get("/all", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def get_all_offer_statuses(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    
    """
    Get all offer approval statuses 
    """

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Authorization token missing"
        )

    service = OfferApprovalActionService(db)
    return await service.get_all_offer_statuses(auth_header=auth_header)

@router.post("/action", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def create_offer_approval_actions(
    payload: list[OfferApproveActionRequest],
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Approver submits APPROVED / REJECTED / ON_HOLD actions (bulk)
    """
    current_user_id = int(request.state.user.get("user_id"))

    service = OfferApprovalActionService(db)
    return await service.create_offer_actions(payload, current_user_id)


@router.put(
    "/update_action"
, dependencies=[Depends(require_roles("Manager"))])
async def update_offer_action(
    payload: OfferApproveActionRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Update offer approval action:
    - Only assigned action taker can act
    - Offer must be in Created status
    - Prevent duplicate actions
    """
    current_user_id = int(request.state.user.get("user_id"))
    service = OfferApprovalActionService(db)

    response = await service.update_offer_action(
        user_uuid=payload.user_uuid,
        action=payload.action,
        comments=payload.comments,
        current_user_id=current_user_id
    )

    return response

@router.get("/admin/my-actions", response_model=list[OfferActionAdminResponse], dependencies=[Depends(require_roles("HR", "ADMIN", "Manager"))])
async def get_my_offer_actions(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Admin / Manager / Approver view
    """

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=400,
            detail="Authorization token missing"
        )
    current_user_id = int(request.state.user.get("user_id"))

    service = OfferApprovalActionService(db)
    return await service.get_admin_actions(current_user_id, auth_header)


@router.get("/admin-users", dependencies=[Depends(require_roles("HR", "Admin", "Manager"))])
async def get_admin_users(request: Request):
    """
    Controller passes token to service
    """

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Authorization token missing"
        )

    return await fetch_admin_users_reformed(
        token=auth_header
    )
@router.get("/my-actions", response_model=list[OfferApproveActionResponse], dependencies=[Depends(require_roles("Manager"))])
async def get_all_my_actions(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        """
        User views their own offer approval actions
        """

        current_user_id = int(request.state.user.get("user_id"))
        token = request.headers.get("Authorization")
        print("Current User ID:", current_user_id)  # Debugging line

        service = OfferApprovalActionService(db)
        result = await service.get_all_my_actions(current_user_id, token)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )
@router.put("/reassign", response_model=OfferReassignApprovalResponse, dependencies=[Depends(require_roles("HR"))])
async def reassign_offer_approval(
    payload: OfferReassignApprovalRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    current_user_id = int(request.state.user.get("user_id"))

    service = OfferApprovalActionService(db)
    return await service.reassign_offer_approval_action(
        payload,
        current_user_id
    )
    
