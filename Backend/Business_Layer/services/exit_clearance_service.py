from fastapi import HTTPException
from Backend.DAL.dao.exit_clearance_dao import ExitClearanceDAO


class ExitClearanceService:

    def __init__(self):
        self.dao = ExitClearanceDAO()


    async def create_clearances(self, db, exit_uuid, employee_uuid):

        try:
            return await self.dao.create_clearances(
                db,
                exit_uuid,
                employee_uuid
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )


    async def get_my_pending(self, db, departments):

        try:
            return await self.dao.get_my_pending(
                db,
                departments
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
    async def update_clearance(self, db, clearance_uuid, status, remarks, user_id):

        try:

            result = await self.dao.update_clearance(
                db,
                clearance_uuid,
                status,
                remarks,
                user_id
            )

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="Clearance not found"
                )

            return result

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
    async def get_employee_clearances(self, db, employee_uuid):
        try:
            return await self.dao.get_employee_clearances(db, employee_uuid)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def get_clearance_history(self, db, exit_uuid):
        try:
            return await self.dao.get_clearance_history(db, exit_uuid)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def get_all_clearances(self, db):
        try:
            return await self.dao.get_all_clearances(db)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))