from Backend.DAL.dao.employee_exit_dao import EmployeeExitDAO
from fastapi import HTTPException


class EmployeeExitService:

    def __init__(self):
        self.dao = EmployeeExitDAO()


    async def create_employee_exit(self, db, data):
        try:
            existing = await self.get_employee_exit_by_employee_uuid(
                db,
                data.employee_uuid
            )

            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="Employee exit already exists"
                )

            return await self.dao.create_employee_exit(db, data)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def get_employee_exit_by_employee_uuid(self, db, employee_uuid):
        try:
            return await self.dao.get_employee_exit_by_employee_uuid(
                db,
                employee_uuid
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def get_all_employee_exits(self, db):
        try:
            return await self.dao.get_all_employee_exits(db)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def get_employee_exit_by_exit_uuid(self, db, exit_uuid):
        try:
            result = await self.dao.get_employee_exit_by_exit_uuid(
                db,
                exit_uuid
            )

            if not result:
                raise HTTPException(
                    status_code=404,
                detail="Employee exit not found"
            )

            return result

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def update_employee_exit_by_employee_uuid(self, db, employee_uuid, data):
        try:
            existing = await self.get_employee_exit_by_employee_uuid(
                db,
                employee_uuid
            )

            if not existing:
                raise HTTPException(
                    status_code=404,
                    detail="Employee exit not found"
                )

            return await self.dao.update_employee_exit_by_employee_uuid(db, employee_uuid, data)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def update_employee_exit_by_exit_uuid(self, db, exit_uuid, data):
        try:
            existing = await self.get_employee_exit_by_exit_uuid(
                db,
                exit_uuid
            )

            if not existing:
                raise HTTPException(
                    status_code=404,
                    detail="Employee exit not found"
                )

            return await self.dao.update_employee_exit_by_exit_uuid(db, exit_uuid, data)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def delete_employee_exit(self, db, exit_uuid):
        try:
            existing = await self.get_employee_exit_by_exit_uuid(
                db,
                exit_uuid
            )

            if not existing:
                raise HTTPException(
                    status_code=404,
                    detail="Employee exit not found"
                )

            return await self.dao.delete_employee_exit(db, exit_uuid)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))