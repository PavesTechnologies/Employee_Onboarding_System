import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from Backend.DAL.dao.departments_dao import DepartmentsDAO
from Backend.DAL.models.models import Departments
from Backend.API_Layer.interfaces.departments_interface import DepartmentCreate


class DepartmentsService:

    @staticmethod
    async def create_department(db: AsyncSession, department_data: DepartmentCreate):

        existing = await DepartmentsDAO.get_department_by_name(
            db, department_data.department_name
        )

        if existing:
            return None

        department = Departments(
            department_uuid=str(uuid.uuid4()),
            department_name=department_data.department_name,
            description=department_data.description
        )

        return await DepartmentsDAO.create_department(db, department)
    
    @staticmethod
    async def get_all_departments(db: AsyncSession):

        departments = await DepartmentsDAO.get_all_departments(db)

        return departments
    
    @staticmethod
    async def get_department_by_uuid(db: AsyncSession, department_uuid: str):

        result = await db.execute(
            select(Departments).where(
                Departments.department_uuid == department_uuid
            )
        )

        return result.scalar_one_or_none()


    @staticmethod
    async def update_department(db: AsyncSession, department_uuid: str, data):

        department = await DepartmentsDAO.get_department_by_uuid(
            db, department_uuid
        )

        if not department:
            return None

        return await DepartmentsDAO.update_department(db, department, data)
    
    @staticmethod
    async def get_department_by_uuid(db: AsyncSession, department_uuid: str):

        department = await DepartmentsDAO.get_department_by_uuid(
            db,
            department_uuid
        )

        return department
    
    @staticmethod
    async def delete_department(db: AsyncSession, department_uuid: str):

        department = await DepartmentsDAO.get_department_by_uuid(
            db, department_uuid
        )

        if not department:
            return None

        await DepartmentsDAO.delete_department(db, department)

        return department