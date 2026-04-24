from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select, update
from sqlalchemy.orm import selectinload

from Backend.DAL.models.models import OfferApprovalRequest, OfferApprovalAction, OfferLetterDetails


class OfferApprovalActionDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_request_with_latest_action(self, user_uuid: str):
    # 1️⃣ Get request (light query)
        stmt_req = (
            select(
                OfferApprovalRequest.id,
                OfferApprovalRequest.user_uuid,
                OfferApprovalRequest.action_taker_id,
            )
            .where(OfferApprovalRequest.user_uuid == user_uuid)
            .limit(1)
        )

        result = await self.db.execute(stmt_req)
        req = result.first()

        if not req:
            return None

        # 2️⃣ Get latest action (only 1 row)
        stmt_action = (
            select(
                OfferApprovalAction.action,
                OfferApprovalAction.comment
            )
            .where(OfferApprovalAction.request_id == req.id)  
            .order_by(OfferApprovalAction.id.desc())
            .limit(1)
        )

        result_action = await self.db.execute(stmt_action)
        action = result_action.first()

        return {
            "user_uuid": req.user_uuid,
            "action_taker_id": req.action_taker_id,
            "action": action.action if action else None,
            "comment": action.comment if action else None,
        }


    async def get_all_requests_with_actions(self):
        stmt = (
            select(OfferApprovalRequest)
            .options(selectinload(OfferApprovalRequest.offer_approval_action))
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()
    async def get_request_by_user_uuid(self, user_uuid: str):
        stmt = select(OfferApprovalRequest).where(
            OfferApprovalRequest.user_uuid == user_uuid
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_action(
        self,
        request_id: int,
        action: str,
        comment: str | None
    ):
        new_action = OfferApprovalAction(
            request_id=request_id,
            action=action,
            comment=comment
        )

        try:
            self.db.add(new_action)
            await self.db.commit()
            await self.db.refresh(new_action)
            return new_action
        except Exception:
            await self.db.rollback()
            return None
        
    async def has_action_for_request(self, request_id: int) -> bool:
        stmt = select(OfferApprovalAction.id).where(
            OfferApprovalAction.request_id == request_id
        )
        result = await self.db.execute(stmt)
        return result.scalar() is not None
    
    async def get_action_by_request_id(self, request_id: int):
        stmt = select(OfferApprovalAction).where(
            OfferApprovalAction.request_id == request_id
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def update_action(
        self,
        action_id: int,
        action: str,
        comment: str | None
    ) -> bool:
        stmt = (
            update(OfferApprovalAction)
            .where(OfferApprovalAction.id == action_id)
            .values(
                action=action,
                comment=comment
            )
        )
        await self.db.execute(stmt)
        await self.db.commit()
        return True
    
    async def get_requests_for_action_taker(self, action_taker_id: int):
        """
        Fetch all approval requests assigned to this user
        """
        stmt = (
            select(OfferApprovalRequest)
            .where(OfferApprovalRequest.action_taker_id == action_taker_id)
            .options(
                selectinload(OfferApprovalRequest.offer_approval_action),
                selectinload(OfferApprovalRequest.offer_letter_details)
            )
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()
    async def get_all_my_actions(self, current_user_id):
        stmt = (
            select(
                OfferApprovalRequest.id,
                OfferApprovalRequest.user_uuid,
                OfferApprovalRequest.request_by,
                OfferLetterDetails.first_name,
                OfferLetterDetails.middle_name,
                OfferLetterDetails.last_name,
                OfferLetterDetails.mail,
                OfferLetterDetails.designation,
                OfferApprovalAction.action
            )
            .join(
                OfferApprovalAction,
                OfferApprovalAction.request_id == OfferApprovalRequest.id
            )
            .join(
                OfferLetterDetails,
                OfferLetterDetails.user_uuid == OfferApprovalRequest.user_uuid
            )
            .where(OfferApprovalRequest.action_taker_id == current_user_id)
        )

        result = await self.db.execute(stmt)
        return result.mappings().all()

    async def reassign_approval_request(
        self,
        user_uuid: str,
        new_action_taker_id: int
    ) -> bool:
        """
        Reassign approver for a pending approval request
        """

        stmt = (
            update(OfferApprovalRequest)
            .where(
                and_(
                    OfferApprovalRequest.user_uuid == user_uuid,
                    OfferApprovalRequest.action_taker_id != new_action_taker_id
                )
            )
            .values(
                action_taker_id=new_action_taker_id
            )
        )

        result = await self.db.execute(stmt)

        if result.rowcount == 0:
            await self.db.rollback()
            return False

        await self.db.commit()
        return True
