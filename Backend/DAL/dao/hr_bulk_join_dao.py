from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from ...DAL.models.models import OfferLetterDetails


class HrBulkJoinDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ✅ get only verified users
    async def get_verified_users_by_emails(self, email_list):
        query = select(OfferLetterDetails).where(
            OfferLetterDetails.mail.in_(email_list),
            OfferLetterDetails.status == "Verified"
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    # ✅ get count of verified users
    async def count_verified_by_emails(self, email_list):
        query = select(OfferLetterDetails).where(
            OfferLetterDetails.mail.in_(email_list),
            OfferLetterDetails.status == "Verified"
        )
        result = await self.db.execute(query)
        return len(result.scalars().all())

    # ✅ update joining date for verified users
    async def update_joining_date_for_verified(self, email_list, joining_date,payload):
        stmt = (
            update(OfferLetterDetails)
            .where(
                OfferLetterDetails.mail.in_(email_list),
            )

            .values(joining_date=joining_date,
                    status="Joining")

            .values(
                joining_date=joining_date,
                reporting_time=payload.reporting_time,
                # location=payload.location,
                # department=payload.department,
                # reporting_time=payload.reporting_time

                )

        )

        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount


    async def update_joining_date_for_user(
        self,
        user_uuid: str,
        new_joining_date,
        reporting_manager
    ):
        stmt = (
            update(OfferLetterDetails)
            .where(OfferLetterDetails.user_uuid == user_uuid)
            .values(
                joining_date=new_joining_date,
                reporting_manager=reporting_manager,
                status="Joining"   # reset status
            )
        )

        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def get_user_by_uuid(self, user_uuid: str):
        query = select(OfferLetterDetails).where(
        OfferLetterDetails.user_uuid == user_uuid
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
        