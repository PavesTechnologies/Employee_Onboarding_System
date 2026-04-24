from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
import datetime

from Backend.DAL.models.models import EmployeeTasks, OfferLetterDetails


class EmployeeTasksDAO:

    @staticmethod
    async def create_employee_task(
        db: AsyncSession,
        request
    ):

        result = await db.execute(
            select(OfferLetterDetails).where(
                OfferLetterDetails.user_uuid == request.user_uuid
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            return None

        # -----------------------------------
        # Create Task Object
        # -----------------------------------
        new_task = EmployeeTasks(
            task_uuid=str(uuid4()),
            user_uuid=request.user_uuid,

            task_title=request.task_title,
            task_type=request.task_type,
            description=request.description,

            assigned_to=request.assigned_to,
            assigned_team=request.assigned_team,

            priority=request.priority,
            status=request.status,
            progress=request.progress,

            due_date=request.due_date,
            reminder_date=request.reminder_date,

            send_notification=request.send_notification,

            escalation_owner=request.escalation_owner,

            internal_notes=request.internal_notes,
            comments=request.comments,

            created_by=request.created_by,
            created_at=datetime.datetime.utcnow()
        )

        # -----------------------------------
        # Save to DB (Async)
        # -----------------------------------
        db.add(new_task)

        await db.commit()
        await db.refresh(new_task)

        return new_task
    
    @staticmethod
    async def update_employee_task(db, task_uuid, request):
        # Find task
        result = await db.execute(
            select(EmployeeTasks).where(
                EmployeeTasks.task_uuid == task_uuid
            )
        )

        task = result.scalar_one_or_none()

        if not task:
            return None

        # Update only provided fields
        for field, value in request.dict(exclude_unset=True).items():
            setattr(task, field, value)

        task.updated_at = datetime.datetime.utcnow()

        # If completed
        if request.status == "Completed":
            task.completed_at = datetime.datetime.utcnow()
            task.completed_by = request.updated_by

        await db.commit()
        await db.refresh(task)

        return task


    @staticmethod
    async def get_all_employee_tasks(db):
        result = await db.execute(
            select(EmployeeTasks)
        )

        tasks = result.scalars().all()
        return tasks

    

    @staticmethod
    async def get_tasks_by_user(db, user_uuid: str):
        result = await db.execute(
            select(EmployeeTasks).where(
                EmployeeTasks.user_uuid == user_uuid
            )
        )

        return result.scalars().all()


    @staticmethod
    async def delete_employee_task(db, task_uuid: str):
        result = await db.execute(
            select(EmployeeTasks).where(
                EmployeeTasks.task_uuid == task_uuid
            )
        )

        task = result.scalar_one_or_none()

        if not task:
            return None

        await db.delete(task)
        await db.commit()

        return task