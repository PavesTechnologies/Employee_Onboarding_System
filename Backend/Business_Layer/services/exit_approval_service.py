from Backend.DAL.dao.exit_approval_dao import ExitApprovalDAO
from fastapi import HTTPException


class ExitApprovalService:

    def __init__(self):
        self.dao = ExitApprovalDAO()

    async def create_exit_approval(self, db, data):
        try:
            return await self.dao.create_exit_approval(db, data)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))