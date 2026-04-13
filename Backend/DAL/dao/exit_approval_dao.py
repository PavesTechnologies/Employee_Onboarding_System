from sqlalchemy import select
from Backend.Business_Layer.utils.uuid_generator import generate_uuid7
from ..models.models import ExitApprovals, EmployeeExit
from sqlalchemy.exc import SQLAlchemyError
from Backend.Business_Layer.services.exit_clearance_service import ExitClearanceService
from datetime import datetime
class ExitApprovalDAO:

    async def create_exit_approval(self, db, data):
        try:

            manager_approval = ExitApprovals(
                approval_uuid=str(generate_uuid7()),
                exit_uuid=data.exit_uuid,
                approval_type="Manager"
            )

            hr_approval = ExitApprovals(
                approval_uuid=str(generate_uuid7()),
                exit_uuid=data.exit_uuid,
                approval_type="HR"
            )

            db.add(manager_approval)
            db.add(hr_approval)

            await db.commit()

            await db.refresh(manager_approval)
            await db.refresh(hr_approval)

            return [manager_approval, hr_approval]

        except SQLAlchemyError as e:
            await db.rollback()
            raise Exception(f"Database error: {str(e)}")

        except Exception as e:
            await db.rollback()
            raise Exception(f"Error creating approvals: {str(e)}")
    async def manager_approve(
        self,
        db,
        approval_uuid,
        user_id,
        status,
        remarks
    ):
        try:

            query = select(ExitApprovals).where(
                ExitApprovals.approval_uuid == approval_uuid,
                ExitApprovals.approval_type == "Manager"
            )

            result = await db.execute(query)
            approval = result.scalars().first()

            if not approval:
                return None

            approval.status = status
            approval.remarks = remarks
            approval.approved_by = user_id
            approval.approved_at = datetime.utcnow()

            # Update Employee Exit Status
            if status == "Approved":
                exit_query = select(EmployeeExit).where(
                    EmployeeExit.exit_uuid == approval.exit_uuid
                )

                exit_result = await db.execute(exit_query)
                exit_record = exit_result.scalars().first()

                if exit_record:
                    exit_record.status = "Manager Approved"

            await db.commit()
            await db.refresh(approval)

            return approval

        except Exception as e:
            await db.rollback()
            raise Exception(str(e))

    async def hr_approve(
        self,
        db,
        approval_uuid,
        user_id,
        status,
        remarks
    ):
        try:

            query = select(ExitApprovals).where(
                ExitApprovals.approval_uuid == approval_uuid,
                ExitApprovals.approval_type == "HR"
            )

            result = await db.execute(query)
            approval = result.scalars().first()

            if not approval:
                return None

            approval.status = status
            approval.remarks = remarks
            approval.approved_by = user_id
            approval.approved_at = datetime.utcnow()

            # Update Employee Exit Status
            if status == "Approved":
                exit_query = select(EmployeeExit).where(
                    EmployeeExit.exit_uuid == approval.exit_uuid
                )

                exit_result = await db.execute(exit_query)
                exit_record = exit_result.scalars().first()

                if exit_record:
                    exit_record.status = "Clearance Pending"

                    # Auto Create Clearances
                    clearance_service = ExitClearanceService()

                    await clearance_service.create_clearances(
                        db,
                        approval.exit_uuid,
                        exit_record.employee_uuid
                    )

            await db.commit()
            await db.refresh(approval)

            return approval

        except Exception as e:
            await db.rollback()
            raise Exception(str(e))    
    async def get_all_approvals(self, db):
        try:
            query = select(ExitApprovals)
            result = await db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            raise Exception(str(e))
    async def get_approvals_by_exit_uuid(self, db, exit_uuid):
        try:
            query = select(ExitApprovals).where(ExitApprovals.exit_uuid == exit_uuid)
            result = await db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            raise Exception(str(e))
    async def get_approvals_by_employee_uuid(self, db, employee_uuid):
        try:

            query = (
                select(ExitApprovals)
                .join(EmployeeExit, ExitApprovals.exit_uuid == EmployeeExit.exit_uuid)
                .where(EmployeeExit.employee_uuid == employee_uuid)
            )

            result = await db.execute(query)

            return result.scalars().all()

        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")

        except Exception as e:
            raise Exception(str(e))
    async def get_my_pending_approvals(self, db, role):
        try:
            print("Role received in DAO:", role)

            query = select(ExitApprovals).where(
                ExitApprovals.approval_type == role,
                ExitApprovals.status == "Pending"
            )

            result = await db.execute(query)

            data = result.scalars().all()

            print("DAO result:", data)

            return data

        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")

        except Exception as e:
            raise Exception(str(e))
    async def get_approvals_history(self, db, exit_uuid):
        try:
            query = select(ExitApprovals).where(ExitApprovals.exit_uuid == exit_uuid)
            result = await db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            raise Exception(str(e))