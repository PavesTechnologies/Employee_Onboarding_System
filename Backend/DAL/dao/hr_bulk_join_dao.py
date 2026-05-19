from typing import List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...DAL.models.models import EmployeeDetails, OfferLetterDetails


class HrBulkJoinDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_verified_users_by_emails(self, email_list: List[str]):
        query = select(OfferLetterDetails).where(
            OfferLetterDetails.mail.in_(email_list),
            OfferLetterDetails.status == "Verified"
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count_verified_by_emails(self, email_list: List[str]):
        query = select(OfferLetterDetails).where(
            OfferLetterDetails.mail.in_(email_list),
            OfferLetterDetails.status == "Verified"
        )
        result = await self.db.execute(query)
        return len(result.scalars().all())

    async def update_joining_date_for_verified(
        self,
        email_list: List[str],
        joining_date,
        payload,
        status,
        reporting_manager
    ):
        stmt = (
            update(OfferLetterDetails)
            .where(OfferLetterDetails.mail.in_(email_list))
            .values(
                joining_date=joining_date,
                reporting_manager=reporting_manager,
                joining_comments=getattr(payload, "joining_comments", None),
                status=status
            )
        )

        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def update_joining_date_for_user(
        self,
        user_uuid: str,
        payload,
        status: str,
        reporting_manager
    ):
        stmt = (
            update(OfferLetterDetails)
            .where(OfferLetterDetails.user_uuid == user_uuid)
            .values(
                joining_date=payload.new_joining_date,
                reporting_manager=reporting_manager,
                joining_comments=payload.joining_comments,
                status=status
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
        print(result.scalars().all())
        return result.scalars().all()

    async def get_employee_by_manager_value(self, reporting_manager: str):
        if reporting_manager is None:
            return None

        manager_value = str(reporting_manager).strip()
        if not manager_value:
            return None

        filters = [
            EmployeeDetails.employee_id == manager_value,
            EmployeeDetails.employee_uuid == manager_value,
            EmployeeDetails.user_uuid == manager_value
        ]

        if manager_value.isdigit():
            filters.insert(0, EmployeeDetails.id == int(manager_value))

        for filter_condition in filters:
            query = select(EmployeeDetails).where(filter_condition)
            result = await self.db.execute(query)
            employee = result.scalar_one_or_none()
            if employee:
                return employee

        return None

    async def get_employees_under_manager(self, manager_employee_id: str):
        """
        Fetch all employees whose reporting_manager_uuid
        contains the manager's employee_id.
        Example:
            manager_employee_id = "5100001"
            reporting_manager_uuid = "5100001"
        """
        query = (
            select(EmployeeDetails)
            .where(
                EmployeeDetails.reporting_manager_uuid == manager_employee_id
            )
            .order_by(EmployeeDetails.first_name)
        )

        result = await self.db.execute(query)
        return result.scalars().all()
