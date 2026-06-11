from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.dao.organisationtree_dao import OrganizationTreeDAO

from Backend.DAL.dao.departments_dao import DepartmentsDAO

from Backend.DAL.dao.designation_dao import DesignationsDAO


class OrganizationTreeService:

    def __init__(self, db: AsyncSession):

        self.db = db
        self.dao = OrganizationTreeDAO(db)

    async def get_organization_hierarchy(self, employee_id: str):

        manager = await self.dao.get_employee_by_employee_id(employee_id)

        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")

        manager_department = await DepartmentsDAO.get_department_by_uuid(
            self.db, manager.department_uuid
        )

        manager_designation = await DesignationsDAO.get_designation_by_uuid(
            self.db, manager.designation_uuid
        )

        employees = await self.dao.get_employees_under_manager(employee_id)

        employee_response = []

        for employee in employees:

            department_data = await DepartmentsDAO.get_department_by_uuid(
                self.db, employee.department_uuid
            )

            designation_data = await DesignationsDAO.get_designation_by_uuid(
                self.db, employee.designation_uuid
            )

            employee_response.append(
                {
                    "employee_id": employee.employee_id,
                    "user_uuid": employee.user_uuid,
                    "name": " ".join(
                        part
                        for part in [
                            employee.first_name,
                            employee.middle_name,
                            employee.last_name,
                        ]
                        if part
                    ).strip(),
                    "department": (
                        department_data.department_name if department_data else None
                    ),
                    "designation": (
                        designation_data.designation_name if designation_data else None
                    ),
                    "location": employee.location,
                }
            )

        return {
            "manager": {
                "employee_id": manager.employee_id,
                "user_uuid": manager.user_uuid,
                "name": " ".join(
                    part
                    for part in [
                        manager.first_name,
                        manager.middle_name,
                        manager.last_name,
                    ]
                    if part
                ).strip(),
                "department": (
                    manager_department.department_name if manager_department else None
                ),
                "designation": (
                    manager_designation.designation_name
                    if manager_designation
                    else None
                ),
                "location": manager.location,
            },
            "employees": employee_response,
        }
