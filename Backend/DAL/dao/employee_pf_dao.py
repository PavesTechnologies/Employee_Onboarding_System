from ..models.models import EmployeePfDetails
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class EmployeePfDAO:

    def __init__(self, db: AsyncSession):
        self.db = db


    async def get_pf_details_by_uuid(self, pf_uuid):
        result = await self.db.execute(
            select(EmployeePfDetails).where(
                EmployeePfDetails.pf_uuid == pf_uuid
            )
        )
        return result.scalar_one_or_none()


    async def get_all_pf_details(self):
        result = await self.db.execute(select(EmployeePfDetails))
        return result.scalars().all()


    async def create_pf_details(self, pf_uuid, request_data):

        pf = EmployeePfDetails(
            pf_uuid=pf_uuid,
            user_uuid=request_data.user_uuid,
            pf_member=request_data.pf_member,
            uan_number=request_data.uan_number
        )

        self.db.add(pf)
        await self.db.commit()
        await self.db.refresh(pf)

        return pf


    async def update_pf_details(self, pf_uuid, request_data):

        result = await self.db.execute(
            select(EmployeePfDetails).where(
                EmployeePfDetails.pf_uuid == pf_uuid
            )
        )

        pf = result.scalar_one_or_none()

        if not pf:
            return None

        pf.pf_member = request_data.pf_member
        pf.uan_number = request_data.uan_number

        await self.db.commit()
        await self.db.refresh(pf)

        return pf


    async def delete_pf_details(self, pf_uuid):

        result = await self.db.execute(
            select(EmployeePfDetails).where(
                EmployeePfDetails.pf_uuid == pf_uuid
            )
        )

        pf = result.scalar_one_or_none()

        await self.db.delete(pf)
        await self.db.commit()

        return pf