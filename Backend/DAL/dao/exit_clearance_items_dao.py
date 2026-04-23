from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from Backend.Business_Layer.utils.uuid_generator import generate_uuid7
from Backend.DAL.models.models import ExitClearanceItems, EmployeeExit, ExitClearance

from datetime import datetime
class ExitClearanceItemsDAO:

    async def create_items(self, db, clearance_uuid, item_name):
        try:
            new_item = ExitClearanceItems(
                clearance_item_uuid=str(generate_uuid7()),
                clearance_uuid=clearance_uuid,
                item_name=item_name
            )
            db.add(new_item)
            await db.commit()
            await db.refresh(new_item)
            return new_item
        except Exception as e:
            await db.rollback()
            raise Exception(str(e))

    async def get_items(self, db, clearance_uuid):

        try:

            query = select(ExitClearanceItems).where(
                ExitClearanceItems.clearance_uuid == clearance_uuid
            )

            result = await db.execute(query)

            return result.scalars().all()

        except Exception as e:
            raise Exception(str(e))


    async def update_item(self, db, data):

        try:

            query = select(ExitClearanceItems).where(
                ExitClearanceItems.clearance_item_uuid == data.clearance_item_uuid
            )

            result = await db.execute(query)
            item = result.scalars().first()

            if not item:
                return None

            item.status = data.status
            item.remarks = data.remarks

            await db.commit()
            await db.refresh(item)

            # Step 1: Check all items completed
            query = select(ExitClearanceItems).where(
                ExitClearanceItems.clearance_uuid == item.clearance_uuid,
                ExitClearanceItems.status != "Completed"
            )

            result = await db.execute(query)
            pending_items = result.scalars().first()

            # Step 2: If all items completed update clearance
            if not pending_items:

                clearance_query = select(ExitClearance).where(
                    ExitClearance.clearance_uuid == item.clearance_uuid
                )

                clearance_result = await db.execute(clearance_query)
                clearance = clearance_result.scalars().first()

                clearance.status = "Approved"
                clearance.approved_by = data.approved_by
                clearance.remarks = "All checklist items completed"
                clearance.approved_at = datetime.utcnow()

                await db.commit()

                # Step 3: Check all department clearances
                query = select(ExitClearance).where(
                    ExitClearance.exit_uuid == clearance.exit_uuid,
                    ExitClearance.status != "Approved"
                )

                result = await db.execute(query)
                pending_clearance = result.scalars().first()

                # Step 4: If all clearances approved update exit
                if not pending_clearance:

                    exit_query = select(EmployeeExit).where(
                        EmployeeExit.exit_uuid == clearance.exit_uuid
                    )

                    exit_result = await db.execute(exit_query)
                    exit_record = exit_result.scalars().first()

                    if exit_record:
                        exit_record.status = "FnF Pending"

                        await db.commit()

            return item

        except Exception as e:
            await db.rollback()
            raise Exception(str(e))
    async def get_all_items(self, db):
        try:
            query = select(ExitClearanceItems)
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            await db.rollback()
            raise Exception(str(e))