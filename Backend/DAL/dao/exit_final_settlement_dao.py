from sqlalchemy import select
from datetime import datetime
from Backend.Business_Layer.utils.uuid_generator import generate_uuid7
from Backend.DAL.models.models import ExitFinalSettlement, EmployeeExit


class ExitFinalSettlementDAO:


    async def create_settlement(self, db, data):

        net_payable = (
            data.last_salary +
            data.leave_encashment +
            data.bonus -
            data.deductions
        )

        settlement = ExitFinalSettlement(

            settlement_uuid=str(generate_uuid7()),
            exit_uuid=data.exit_uuid,
            employee_uuid=data.employee_uuid,
            last_salary=data.last_salary,
            leave_encashment=data.leave_encashment,
            bonus=data.bonus,
            deductions=data.deductions,
            net_payable=net_payable
        )

        db.add(settlement)
        await db.commit()
        await db.refresh(settlement)

        return settlement


    async def get_settlement(self, db, exit_uuid):

        query = select(ExitFinalSettlement).where(
            ExitFinalSettlement.exit_uuid == exit_uuid
        )

        result = await db.execute(query)

        return result.scalars().first()


    async def approve_settlement(self, db, settlement_uuid, user_id, remarks):

        query = select(ExitFinalSettlement).where(
            ExitFinalSettlement.settlement_uuid == settlement_uuid
        )

        result = await db.execute(query)
        settlement = result.scalars().first()

        if not settlement:
            return None

        settlement.status = "Approved"
        settlement.approved_by = user_id
        settlement.approved_at = datetime.utcnow()

        await db.commit()

        # Update employee exit status
        exit_query = select(EmployeeExit).where(
            EmployeeExit.exit_uuid == settlement.exit_uuid
        )

        exit_result = await db.execute(exit_query)
        exit_record = exit_result.scalars().first()

        settlement.status = "Approved"
        exit_record.status = "Settlement Approved"

        await db.commit()

        return settlement


    async def mark_paid(self, db, settlement_uuid):

        query = select(ExitFinalSettlement).where(
            ExitFinalSettlement.settlement_uuid == settlement_uuid
        )

        result = await db.execute(query)
        settlement = result.scalars().first()

        if not settlement:
            return None

        settlement.status = "Paid"

        await db.commit()

        # update employee exit
        exit_query = select(EmployeeExit).where(
            EmployeeExit.exit_uuid == settlement.exit_uuid
        )

        exit_result = await db.execute(exit_query)
        exit_record = exit_result.scalars().first()

        exit_record.status = "Paid"

        await db.commit()

        return settlement