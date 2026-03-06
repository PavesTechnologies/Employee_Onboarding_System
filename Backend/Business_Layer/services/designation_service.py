import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from Backend.DAL.dao.designation_dao import DesignationsDAO
from Backend.DAL.models.models import Designations


class DesignationsService:

    @staticmethod
    async def create_designation(db: AsyncSession, data):

        existing = await DesignationsDAO.get_designation_by_name(
            db,
            data.designation_name
        )

        if existing:
            return HTTPException(status_code=400, detail="Designation already exists")

        designation = Designations(
            designation_uuid=str(uuid.uuid4()),
            designation_name=data.designation_name,
            department_uuid=data.department_uuid,
            description=data.description
        )

        return await DesignationsDAO.create_designation(db, designation)


    @staticmethod
    async def get_all_designations(db: AsyncSession):

        return await DesignationsDAO.get_all_designations(db)
    
    @staticmethod
    async def get_designation_by_uuid(db, designation_uuid):

        designation = await DesignationsDAO.get_designation_by_uuid(
            db, designation_uuid
        )

        if not designation:
            raise HTTPException(status_code=404, detail="Designation not found")

        return designation
    
    @staticmethod
    async def get_designation_by_uuid(db, designation_uuid):

        designation = await DesignationsDAO.get_designation_by_uuid(
            db, designation_uuid
        )

        if not designation:
            raise HTTPException(status_code=404, detail="Designation not found")

        return designation
    
    @staticmethod
    async def get_designations_by_department(db: AsyncSession, department_uuid: str):

        designations = await DesignationsDAO.get_designations_by_department(
            db,
            department_uuid
        )

        return designations


    @staticmethod
    async def update_designation(db: AsyncSession, designation_uuid: str, data):

        designation = await DesignationsDAO.get_designation_by_uuid(
            db,
            designation_uuid
        )

        if not designation:
            raise HTTPException(status_code=404, detail="Designation not found")

        return await DesignationsDAO.update_designation(db, designation, data)


    @staticmethod
    async def delete_designation(db: AsyncSession, designation_uuid: str):

        designation = await DesignationsDAO.get_designation_by_uuid(
            db,
            designation_uuid
        )

        if not designation:
            return HTTPException(status_code=404, detail="Designation not found")

        await DesignationsDAO.delete_designation(db, designation)

        return {"message": "Designation deleted successfully"}