from sqlalchemy import select
from Backend.Business_Layer.utils.uuid_generator import generate_uuid7
from Backend.DAL.models.models import ExitInterview


class ExitInterviewDAO:

    async def create_exit_interview(self, db, data):
        interview = ExitInterview(
            interview_uuid=str(generate_uuid7()),
            exit_uuid=data.exit_uuid,
            employee_uuid=data.employee_uuid,
            reason_for_leaving=data.reason_for_leaving,
            company_feedback=data.company_feedback,
            manager_feedback=data.manager_feedback,
            rating=data.rating
        )

        db.add(interview)
        await db.commit()
        await db.refresh(interview)

        return interview

    async def get_exit_interview(self, db, interview_uuid):
        result = await db.execute(
            select(ExitInterview).where(
                ExitInterview.interview_uuid == interview_uuid
            )
        )
        return result.scalar_one_or_none()

    async def get_exit_interview_by_exit_uuid(self, db, exit_uuid):
        result = await db.execute(
            select(ExitInterview).where(
                ExitInterview.exit_uuid == exit_uuid
            )
        )
        return result.scalar_one_or_none()

    async def update_exit_interview(self, db, interview_uuid, data):
        result = await db.execute(
            select(ExitInterview).where(
                ExitInterview.interview_uuid == interview_uuid
            )
        )

        interview = result.scalar_one_or_none()

        if not interview:
            return None

        update_data = data.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(interview, key, value)

        await db.commit()
        await db.refresh(interview)

        return interview

    async def delete_exit_interview(self, db, interview_uuid):
        result = await db.execute(
            select(ExitInterview).where(
                ExitInterview.interview_uuid == interview_uuid
            )
        )

        interview = result.scalar_one_or_none()

        if not interview:
            return False

        await db.delete(interview)
        await db.commit()

        return True