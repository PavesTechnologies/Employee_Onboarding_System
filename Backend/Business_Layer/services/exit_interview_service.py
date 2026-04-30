from fastapi import HTTPException
from Backend.DAL.dao.exit_interview_dao import ExitInterviewDAO


class ExitInterviewService:

    def __init__(self):
        self.dao = ExitInterviewDAO()

    async def create_exit_interview(self, db, data):
        existing = await self.dao.get_exit_interview_by_exit_uuid(
            db, data.exit_uuid
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Exit interview already exists for this exit process"
            )

        return await self.dao.create_exit_interview(db, data)

    async def get_exit_interview(self, db, interview_uuid):
        interview = await self.dao.get_exit_interview(db, interview_uuid)

        if not interview:
            raise HTTPException(
                status_code=404,
                detail="Exit interview not found"
            )

        return interview

    async def update_exit_interview(self, db, interview_uuid, data):
        interview = await self.dao.update_exit_interview(
            db, interview_uuid, data
        )

        if not interview:
            raise HTTPException(
                status_code=404,
                detail="Exit interview not found"
            )

        return interview

    async def delete_exit_interview(self, db, interview_uuid):
        deleted = await self.dao.delete_exit_interview(
            db, interview_uuid
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Exit interview not found"
            )

        return {
            "message": "Exit interview deleted successfully"
        }