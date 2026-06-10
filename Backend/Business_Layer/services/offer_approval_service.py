from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.dao.offer_approval_request import OfferApprovalRequestDAO
from Backend.API_Layer.interfaces.offer_request_interfaces import (
    OfferRequestCreateResponse,
    OfferRequestUpdateResponse,
    OfferRequestDelete,
)


class OfferApprovalRequestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = OfferApprovalRequestDAO(self.db)

    async def create_offer_approval_requests(
        self, request_list: list[OfferRequestCreateResponse]
    ):
        """
        Create multiple offer approval requests (bulk)
        """
        try:
            if not request_list:
                raise ValueError("Request list cannot be empty")

            for request in request_list:
                # 🔴 VALIDATION: Check duplicate request
                existing_request = await self.dao.check_request_exists_by_user_uuid(
                    request.user_uuid
                )

            if existing_request:
                raise HTTPException(
                    status_code=400, detail="Approval request already exists for users"
                )

            created_requests = []

            for request in request_list:
                result = await self.dao.create_approval_request(
                    user_uuid=request.user_uuid,
                    request_by=request.request_by,
                    action_taker_id=request.action_taker_id,
                )

                if not result:
                    raise Exception(
                        f"Failed to create approval request for user_uuid: {request.user_uuid}"
                    )

                created_requests.append(result)

            return {
                "message": "Offer approval requests created successfully",
                "count": len(created_requests),
            }

        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def update_offer_approval_requests(
        self, data_list: list[OfferRequestUpdateResponse], current_user_id: int
    ):
        """
        Bulk update offer approval requests
        """
        if not data_list:
            raise HTTPException(status_code=422, detail="Request list cannot be empty")

        updated_count = 0
        not_found_users = []

        for data in data_list:
            # 🔍 Check if record exists
            existing_request = await self.dao.get_by_user_uuid(data.user_uuid)

            if not existing_request:
                not_found_users.append(data.user_uuid)
                continue

            updated = await self.dao.update_approval_request(
                user_uuid=data.user_uuid,
                request_by=current_user_id,  # always current user
                action_taker_id=data.action_taker_id,
            )

            if updated:
                updated_count += 1

        if updated_count == 0:
            raise HTTPException(status_code=400, detail="No records were updated")

        return {
            "message": "Offer approval requests updated successfully",
            "updated_count": updated_count,
        }

    async def delete_offer_approval_requests(
        self, data_list: list[OfferRequestDelete], current_user_id: int
    ):
        """
        Bulk delete offer approval requests
        """
        if not data_list:
            raise HTTPException(status_code=422, detail="Request list cannot be empty")

        deleted_count = 0
        not_found_users = []

        for data in data_list:
            existing = await self.dao.get_by_user_uuid(data.user_uuid)

            if not existing:
                not_found_users.append(data.user_uuid)
                continue

            deleted = await self.dao.delete_by_user_uuid(data.user_uuid)

            if deleted:
                deleted_count += 1

        if deleted_count == 0:
            raise HTTPException(status_code=400, detail="No records were deleted")

        return {
            "message": "Offer approval requests deleted successfully",
            "deleted_count": deleted_count,
            "deleted_by": current_user_id,
        }
