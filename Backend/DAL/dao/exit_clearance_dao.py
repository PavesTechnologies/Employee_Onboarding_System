from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from Backend.Business_Layer.utils.uuid_generator import generate_uuid7
from Backend.DAL.models.models import ExitClearance, EmployeeExit, ExitClearanceItems

from datetime import datetime

class ExitClearanceDAO:


    # Auto Create Clearances
    async def create_clearances(self, db, exit_uuid, employee_uuid):

        try:

            departments = ["Manager", "IT", "HR", "Finance", "Admin"]

            clearances = []

            for dept in departments:

                clearance = ExitClearance(
                    clearance_uuid=str(generate_uuid7()),
                    exit_uuid=exit_uuid,
                    employee_uuid=employee_uuid,
                    department=dept
                )

                db.add(clearance)
                clearances.append(clearance)

            await db.commit()

            return clearances

        except SQLAlchemyError as e:
            await db.rollback()
            raise Exception(str(e))


    # My Pending
    async def get_my_pending(self, db, departments):

        query = select(ExitClearance).where(
            ExitClearance.department.in_(departments),
            ExitClearance.status == "Pending"
        )

        result = await db.execute(query)

        return result.scalars().all()

    async def update_clearance(self, db, clearance_uuid, status, remarks, user_id):

        try:

            query = select(ExitClearance).where(
                ExitClearance.clearance_uuid == clearance_uuid
            )

            result = await db.execute(query)
            clearance = result.scalars().first()

            if not clearance:
                return None

            clearance.status = status
            clearance.remarks = remarks
            clearance.approved_by = user_id
            clearance.approved_at = datetime.utcnow()

            # If clearance approved → update all items
            if status == "Approved":

                items_query = select(ExitClearanceItems).where(
                    ExitClearanceItems.clearance_uuid == clearance_uuid
                )

                items_result = await db.execute(items_query)
                items = items_result.scalars().all()

                for item in items:
                    item.status = "Completed"

            await db.commit()

            # Check all clearances approved
            query = select(ExitClearance).where(
                ExitClearance.exit_uuid == clearance.exit_uuid,
                ExitClearance.status != "Approved"
            )

            result = await db.execute(query)
            pending = result.scalars().first()

            if not pending:

                exit_query = select(EmployeeExit).where(
                    EmployeeExit.exit_uuid == clearance.exit_uuid
                )

                exit_result = await db.execute(exit_query)
                exit_record = exit_result.scalars().first()

                exit_record.status = "FnF Pending"

                await db.commit()

            return clearance

        except Exception as e:
            await db.rollback()
            raise Exception(str(e))
    async def get_employee_clearances(self, db, employee_uuid):
        try:
            query = select(ExitClearance).where(
                ExitClearance.employee_uuid == employee_uuid
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            await db.rollback()
            raise Exception(str(e))
    async def get_clearance_history(self, db, exit_uuid):
        try:
            query = select(ExitClearance).where(
                ExitClearance.exit_uuid == exit_uuid
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            await db.rollback()
            raise Exception(str(e))
    async def get_all_clearances(self, db):
        try:
            query = select(ExitClearance)
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            await db.rollback()
            raise Exception(str(e))