from http import client
from wsgiref import headers
from Backend.API_Layer.interfaces.offer_request_approve_resign import OfferReassignApprovalRequest, OfferReassignApprovalResponse
from Backend.Business_Layer.utils.ums_users_list import fetch_admin_users_reformed
from Backend.config.env_loader import get_env_var
from fastapi import HTTPException
from Backend.API_Layer.interfaces.offer_approve_action_interfaces import OfferApproveActionRequest
from sqlalchemy.ext.asyncio import AsyncSession


from Backend.DAL.dao.offer_approval_action_dao import OfferApprovalActionDAO
from Backend.API_Layer.interfaces.offer_request_interfaces import OfferRequestResponse

from Backend.DAL.dao.offer_approval_action_dao import OfferApprovalActionDAO
from Backend.API_Layer.interfaces.offer_request_interfaces import OfferRequestResponse

from Backend.DAL.dao.offerresponse_dao import OfferResponseDAO
from Backend.API_Layer.interfaces.OfferActionAdmin_interfaces import OfferActionAdminResponse
import httpx


class OfferApprovalActionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = OfferApprovalActionDAO(db)
        self.offer_response_dao = OfferResponseDAO(db)

    async def get_offer_status(self, user_uuid: str, auth_header: str):

        request = await self.dao.get_request_with_latest_action(user_uuid)

        # ❌ No request
        if not request:
            return OfferRequestResponse(
                user_uuid=user_uuid,
                action_taker_id=0,
                action_taker_name="No user",
                status="No Request",
                comments="No Request."
            )

        # 🔴 Call external API only when needed
        user_details = await fetch_admin_users_reformed(token=auth_header)
        action_taker = next(
            (u for u in user_details if u["user_id"] == request["action_taker_id"]),
            None
        )

        if not action_taker:
            raise HTTPException(status_code=400, detail="Action taker not found")

        # No action yet
        if not request["action"]:
            return OfferRequestResponse(
                user_uuid=user_uuid,
                action_taker_id=request["action_taker_id"],
                action_taker_name=action_taker["name"],
                status="PENDING",
                comments="Awaiting approval"
            )

        # Latest action exists
        return OfferRequestResponse(
            user_uuid=user_uuid,
            action_taker_id=request["action_taker_id"],
            action_taker_name=action_taker["name"],
            status=request["action"],
            comments=request["comment"] or ""
        )

    async def get_all_offer_statuses(self, auth_header: str) -> list[OfferRequestResponse]:
        """
        Resolve offer approval status for ALL users
        """

        user_details = await fetch_admin_users_reformed(token=auth_header)
        
        requests = await self.dao.get_all_requests_with_actions()

        response: list[OfferRequestResponse] = []

        for request in requests:

            action_taker = next(
                (u for u in user_details if u["user_id"] == request.action_taker_id),
                None
            )

            # ❌ Request exists but no action
            if not request.offer_approval_action:
                response.append(
                    OfferRequestResponse(
                        user_uuid=request.user_uuid,
                        action_taker_id=request.action_taker_id,
                        action_taker_name=action_taker['name'] if action_taker else "Unknown",
                        status="PENDING",
                        comments="Awaiting approval"
                    )
                )
                continue

            # ✅ Take latest action
            latest_action = request.offer_approval_action[-1]

            response.append(
                OfferRequestResponse(
                    user_uuid=request.user_uuid,
                    action_taker_id=request.action_taker_id,
                    action_taker_name=action_taker['name'] if action_taker else "Unknown",
                    status=latest_action.action,
                    comments=latest_action.comment or ""
                )
            )

        return response
    
    async def create_offer_actions(
        self,
        payload: list[OfferApproveActionRequest],
        current_user_id: int
    ):
        if not payload:
            raise HTTPException(status_code=422, detail="Payload cannot be empty")

        created = []

        for item in payload:
            # 🔍 Validate request
            request = await self.dao.get_request_by_user_uuid(item.user_uuid)
            if not request:
                raise HTTPException(
                    status_code=404,
                    detail=f"No approval request found users"
                )
            
             # 🔐 VALIDATION: only assigned approver can act
            if request.action_taker_id != current_user_id:
                raise HTTPException(
                    status_code=401,
                    detail=(
                        f"You are not authorized to take action."
                    )
                )
            
             # ❌ NEW VALIDATION — already reviewed
            already_reviewed = await self.dao.has_action_for_request(request.id)
            if already_reviewed:
                raise HTTPException(
                    status_code=400,   # Conflict
                    detail="Action already taken for this user"
                )

            # ✅ Normalize action
            action = item.action.upper()
            if action not in {"APPROVED", "REJECTED", "ON_HOLD"}:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid action should be APPROVED / REJECTED / ON_HOLD"
                )
            

            result = await self.dao.create_action(
                request_id=request.id,
                action=action,
                comment=item.comments
            )

            if not result:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to insert action "
                )

            created.append({
                "user_uuid": item.user_uuid,
                "status": action,
                "comments": item.comments
            })

        return "Successfully created actions"
    
    async def update_offer_action(
    self,
    user_uuid: str,
    action: str,
    comments: str,
    current_user_id: int
):

        # 🔍 Fetch offer letter
        offer = await self.offer_response_dao.get_offer_by_uuid(user_uuid)
        if not offer:
            raise HTTPException(
                status_code=404,
                detail="Offer letter not found"
            )

        # ❌ Status must be Created
        if offer.status != "Created":
            raise HTTPException(
                status_code=400,
                detail="Offer already processed"
            )

        # 🔍 Fetch approval request
        request = await self.dao.get_request_by_user_uuid(user_uuid)
        if not request:
            raise HTTPException(
                status_code=404,
                detail="Approval request not found"
            )

        # 🔐 Action taker validation
        if request.action_taker_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to take action"
            )

        # ✅ Normalize & validate action
        action = action.upper()
        if action not in {"APPROVED", "REJECTED", "ON_HOLD"}:
            raise HTTPException(
                status_code=422,
                detail="Invalid action"
            )

        # 🔍 Fetch existing action (IMPORTANT)
        existing_action = await self.dao.get_action_by_request_id(request.id)
        if not existing_action:
            raise HTTPException(
                status_code=400,
                detail="No existing action found to update"
            )
        
        # ✅ Update action fields # 🔄 UPDATE action (NOT INSERT)
        await self.dao.update_action(
            action_id=existing_action.id,
            action=action,
            comment=comments
        )
        return {
            "message": "Offer action updated successfully"
        }
    
    async def get_admin_actions(
        self,
        current_user_id: int,
        auth_header: str
    ) -> list[OfferActionAdminResponse]:

        requests = await self.dao.get_requests_for_action_taker(current_user_id)
        user_details = await fetch_admin_users_reformed(token=auth_header)

        response: list[OfferActionAdminResponse] = []

        for req in requests:
            action_taker = next((u for u in user_details if u["user_id"] == req.request_by), None)

            offer = req.offer_letter_details

            # 🔍 Determine action status
            if req.offer_approval_action:
                latest_action = req.offer_approval_action[-1]
                action = latest_action.action
                message = latest_action.comment or "Action taken"
            else:
                action = "PENDING"
                message = "Awaiting approval"

            response.append(
                OfferActionAdminResponse(
                    user_uuid=offer.user_uuid,
                    user_first_name=offer.first_name,
                    user_middle_name=offer.middle_name,
                    user_last_name=offer.last_name,

                    # ✅ request_id = request_by (HR user id)
                    request_id=str(req.request_by),

                    # 🧪 Mock value for now
                    requested_name=action_taker['name'] if action_taker else "Unknown",

                    action=action,
                    message=message
                )
            )

        return response
    async def get_all_my_actions(self, current_user_id, token):
        try:
            rows = await self.dao.get_all_my_actions(current_user_id)

            if not rows:
                return []

            # Convert RowMapping → dict
            actions = [dict(row) for row in rows]

            # ✅ Fetch all admin users once (instead of N calls)
            admin_users = await fetch_admin_users_reformed(token)

            admin_map = {
                u["user_id"]: u["name"]
                for u in admin_users
            }

            # ✅ Map names in O(1)
            for item in actions:
                item["requested_by_name"] = admin_map.get(item["request_by"])

            return actions

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching actions: {str(e)}"
            )

    async def reassign_offer_approval_action(
            self,
            payload: OfferReassignApprovalRequest,
            current_user_id: int
        ) -> OfferReassignApprovalResponse:
            """
            Reassign approver ONLY when approval is pending
            """

            # 🔍 Fetch approval request
            request = await self.dao.get_request_by_user_uuid(payload.user_uuid)

            if not request:
                raise HTTPException(
                    status_code=404,
                    detail="Approval request not found"
                )

           # ❌ Cannot reassign if ANY action is APPROVED
            if request.offer_approval_action:

                for action in request.offer_approval_action:
                    if action.action and action.action.upper() == "APPROVED":
                        raise HTTPException(
                            status_code=400,
                            detail="Cannot reassign because offer is already APPROVED"
                        )


            # 🚫 Same approver check
            if request.action_taker_id == payload.new_approver_id:
                raise HTTPException(
                    status_code=400,
                    detail="Approval already assigned to this user"
                )

            previous_approver_id = request.action_taker_id

            # 🔄 Update approver
            updated = await self.dao.reassign_approval_request(
                user_uuid=payload.user_uuid,
                new_action_taker_id=payload.new_approver_id
            )

            if not updated:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to reassign approval"
                )

            return OfferReassignApprovalResponse(
                id=request.id,
                user_uuid=request.user_uuid,
                previous_approver_id=previous_approver_id,
                new_approver_id=payload.new_approver_id,
                reassigned_by=current_user_id,
                reassigned_by_name=None,
                action="PENDING"
            )
