from sqlalchemy import select

from Backend.DAL.models.models import (
    EmployeeDetails
)


class OrganizationTreeDAO:

    def __init__(self, db):
        self.db = db

    async def get_employee_by_employee_id(
        self,
        employee_id: str
    ):

        result = await self.db.execute(
            select(EmployeeDetails).where(
                EmployeeDetails.employee_id == employee_id
            )
        )

        return result.scalar_one_or_none()

    async def get_employees_under_manager(
        self,
        employee_id: str
    ):

        result = await self.db.execute(
            select(EmployeeDetails).where(
                EmployeeDetails.reporting_manager_uuid
                == employee_id
            )
        )

        return result.scalars().all()