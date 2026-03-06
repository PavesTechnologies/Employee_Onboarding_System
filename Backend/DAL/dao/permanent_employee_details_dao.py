from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.models.models import EmployeeDetails


class PermanentEmployeeDetailsDAO:

    async def get_last_employee(self, db: AsyncSession):

        result = await db.execute(
            select(EmployeeDetails)
            .order_by(EmployeeDetails.id.desc())
            .limit(1)
        )

        return result.scalars().first()


    async def get_employee_by_user_uuid(self, db: AsyncSession, user_uuid: str):

        result = await db.execute(
            select(EmployeeDetails).where(
                EmployeeDetails.user_uuid == user_uuid
            )
        )

        return result.scalars().first()
    
    async def get_employee_by_email(self, db: AsyncSession, email: str):

        result = await db.execute(
            select(EmployeeDetails).where(
                EmployeeDetails.work_email == email
            )
        )

        return result.scalars().first()


    async def create_employee(self, db: AsyncSession, employee: EmployeeDetails):

        db.add(employee)
        await db.commit()
        await db.refresh(employee)
        return employee
    
    async def get_employee_by_uuid(self, db: AsyncSession, employee_uuid: str):

        result = await db.execute(
            select(EmployeeDetails).where(
                EmployeeDetails.employee_uuid == employee_uuid
            )
        )

        return result.scalars().first()
    
    async def update_employee(self, db: AsyncSession, employee: EmployeeDetails):

        await db.commit()
        await db.refresh(employee)

        return employee
    
    async def get_all_employees(self, db: AsyncSession):

        result = await db.execute(
            select(EmployeeDetails)
        )

        return result.scalars().all()
    
    async def delete_employee(self, db: AsyncSession, employee_uuid: str):

        employee = await self.get_employee_by_uuid(db, employee_uuid)

        if not employee:
            raise ValueError("Employee not found")

        await db.delete(employee)
        await db.commit()