from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from Backend.DAL.models.models import Designations


class DesignationsDAO:

    @staticmethod
    async def get_designation_by_name(db: AsyncSession, name: str):

        result = await db.execute(
            select(Designations).where(
                Designations.designation_name == name
            )
        )

        return result.scalar_one_or_none()


    @staticmethod
    async def create_designation(db: AsyncSession, designation):

        db.add(designation)
        await db.commit()
        await db.refresh(designation)

        return designation


    @staticmethod
    async def get_all_designations(db: AsyncSession):

        result = await db.execute(select(Designations))

        return result.scalars().all()


    @staticmethod
    async def get_designation_by_uuid(db: AsyncSession, designation_uuid: str):

        result = await db.execute(
            select(Designations).where(
                Designations.designation_uuid == designation_uuid
            )
        )

        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_designations_by_department(db: AsyncSession, department_uuid: str):

        result = await db.execute(
            select(Designations).where(
                Designations.department_uuid == department_uuid
            )
        )

        return result.scalars().all()


    @staticmethod
    async def update_designation(db: AsyncSession, designation, data):

        if data.designation_name is not None:
            designation.designation_name = data.designation_name

        if data.department_uuid is not None:
            designation.department_uuid = data.department_uuid

        if data.description is not None:
            designation.description = data.description

        await db.commit()
        await db.refresh(designation)

        return designation


    @staticmethod
    async def delete_designation(db: AsyncSession, designation):

        await db.delete(designation)
        await db.commit()

        return True