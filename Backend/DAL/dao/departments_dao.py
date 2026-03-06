from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from Backend.DAL.models.models import Departments


class DepartmentsDAO:

    @staticmethod
    async def get_department_by_name(db: AsyncSession, name: str):

        result = await db.execute(
            select(Departments).where(
                Departments.department_name == name
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def create_department(db: AsyncSession, department):

        db.add(department)

        await db.commit()
        await db.refresh(department)
        return department
    
    @staticmethod
    async def get_all_departments(db: AsyncSession):

        result = await db.execute(select(Departments))

        return result.scalars().all()
    
    @staticmethod
    async def get_department_by_uuid(db: AsyncSession, department_uuid: str):

        result = await db.execute(
            select(Departments).where(
                Departments.department_uuid == department_uuid
            )
        )

        return result.scalar_one_or_none()


    @staticmethod
    async def update_department(db: AsyncSession, department, data):

        if data.department_name is not None:
            department.department_name = data.department_name

        if data.description is not None:
            department.description = data.description

        await db.commit()
        await db.refresh(department)

        return department
    
    @staticmethod
    async def delete_department(db: AsyncSession, department):

        await db.delete(department)

        await db.commit()

        return True