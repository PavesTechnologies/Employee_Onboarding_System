from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List

from ...DAL.models.models import OfferLetterDetails


class HrBulkJoinDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ✅ Get only verified users
    async def get_verified_users_by_emails(self, email_list: List[str]):
        query = select(OfferLetterDetails).where(
            OfferLetterDetails.mail.in_(email_list),
            OfferLetterDetails.status == "Verified"
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    # ✅ Count verified users
    async def count_verified_by_emails(self, email_list: List[str]):
        query = select(OfferLetterDetails).where(
            OfferLetterDetails.mail.in_(email_list),
            OfferLetterDetails.status == "Verified"
        )
        result = await self.db.execute(query)
        return len(result.scalars().all())

    # ✅ Update joining details for multiple users
    async def update_joining_date_for_verified(
        self,
        email_list: List[str],
        joining_date,
        payload
    ):
        stmt = (
            update(OfferLetterDetails)
            .where(OfferLetterDetails.mail.in_(email_list))
            .values(
                joining_date=joining_date,
                status="Joining",
                reporting_time=payload.reporting_time,
                location=payload.location,
                department=payload.department,
                reporting_manager=payload.reporting_manager,
                joining_comments=getattr(payload, "joining_comments", None)
            )
        )

        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    # ✅ Update joining details for single user
    async def update_joining_date_for_user(
        self,
        user_uuid: str,
        payload
    ):
        stmt = (
            update(OfferLetterDetails)
            .where(OfferLetterDetails.user_uuid == user_uuid)
            .values(
                joining_date=payload.new_joining_date,
                reporting_manager=payload.reporting_manager,
                reporting_time=payload.reporting_time,
                location=payload.location,
                department=payload.department,
                joining_comments=getattr(payload, "comment", None),
                status="Joining"
            )
        )

        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    # ✅ Get user by UUID
    async def get_user_by_uuid(self, user_uuid: str):
        query = select(OfferLetterDetails).where(
            OfferLetterDetails.user_uuid == user_uuid
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()