from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from Backend.DAL.models.models import OfferApprovalRequest, OfferApprovalAction


class OfferApprovalRequestDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_approval_request(
        self, user_uuid: str, request_by: int, action_taker_id: int
    ):
        """
        Insert a new offer approval request
        and create initial approval action as Pending
        """

        try:
            # 1️⃣ Create OfferApprovalRequest
            new_request = OfferApprovalRequest(
                user_uuid=user_uuid,
                request_by=request_by,
                action_taker_id=action_taker_id,
            )

            self.db.add(new_request)
            await self.db.flush()
            # flush is IMPORTANT → generates new_request.id without commit

            # 2️⃣ Create OfferApprovalAction using generated request_id
            new_action = OfferApprovalAction(
                request_id=new_request.id,
                action="Pending",
                comment=None,
                action_time=datetime.utcnow(),
            )

            self.db.add(new_action)

            # 3️⃣ Commit both inserts together
            await self.db.commit()

            # Optional refresh
            await self.db.refresh(new_request)

            return new_request

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e

    async def get_request_by_id(self, request_id: int):
        query = select(OfferApprovalRequest).where(
            OfferApprovalRequest.id == request_id
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_requests_by_user_uuid(self, user_uuid: str):
        query = select(OfferApprovalRequest).where(
            OfferApprovalRequest.user_uuid == user_uuid
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def check_request_exists_by_user_uuid(self, user_uuid: str):
        query = select(OfferApprovalRequest).where(
            OfferApprovalRequest.user_uuid == user_uuid
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_user_uuid(self, user_uuid: str):
        query = select(OfferApprovalRequest).where(
            OfferApprovalRequest.user_uuid == user_uuid
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def update_approval_request(
        self, user_uuid: str, request_by: int, action_taker_id: int
    ) -> bool:
        """
        Update existing offer approval request
        """
        try:
            stmt = (
                update(OfferApprovalRequest)
                .where(OfferApprovalRequest.user_uuid == user_uuid)
                .values(request_by=request_by, action_taker_id=action_taker_id)
            )

            result = await self.db.execute(stmt)

            if result.rowcount == 0:
                return False  # No record updated

            await self.db.commit()
            return True

        except Exception:
            await self.db.rollback()
            raise

    async def get_by_user_uuid(self, user_uuid: str):
        stmt = select(OfferApprovalRequest).where(
            OfferApprovalRequest.user_uuid == user_uuid
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def delete_by_user_uuid(self, user_uuid: str) -> bool:
        try:
            stmt = delete(OfferApprovalRequest).where(
                OfferApprovalRequest.user_uuid == user_uuid
            )
            await self.db.execute(stmt)
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False

    async def get_all_requests(self):
        stmt = select(OfferApprovalRequest)
        result = await self.db.execute(stmt)
        return result.scalars().all()
