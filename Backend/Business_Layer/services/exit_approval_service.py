from Backend.DAL.dao.exit_approval_dao import ExitApprovalDAO
from fastapi import HTTPException


class ExitApprovalService:

    def __init__(self):
        self.dao = ExitApprovalDAO()

    async def create_exit_approval(self, db, data):
        try:
            return await self.dao.create_exit_approval(db, data)

        except Exception as e:
            raise HTTPException(status_code=500,detail=str(e))

    async def manager_approve(
        self,
        db,
        approval_uuid,
        user_id,
        status,
        remarks
    ):
        try:

            approval = await self.dao.manager_approve(
                db,
                approval_uuid,
                user_id,
                status,
                remarks
            )

            if not approval:
                raise HTTPException(
                    status_code=404,
                    detail="Manager approval not found"
                )

            return approval

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
    async def hr_approve(
        self,
        db,
        approval_uuid,
        user_id,
        status,
        remarks
    ):
        try:

            approval = await self.dao.hr_approve(
                db,
                approval_uuid,
                user_id,
                status,
                remarks
            )

            if not approval:
                raise HTTPException(
                    status_code=404,
                    detail="HR approval not found"
                )

            return approval

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
    async def get_all_approvals(self, db):
        try:
            return await self.dao.get_all_approvals(db)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def get_approvals_by_exit_uuid(self, db, exit_uuid):
        try:
            return await self.dao.get_approvals_by_exit_uuid(db, exit_uuid)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def get_approvals_by_employee_uuid(self, db, employee_uuid):
        try:
            return await self.dao.get_approvals_by_employee_uuid(db, employee_uuid)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def get_my_pending_approvals(self, db, role):
        try:
            result = await self.dao.get_my_pending_approvals(db, role)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def get_approvals_history(self, db, exit_uuid):
        try:
            return await self.dao.get_approvals_history(db, exit_uuid)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))