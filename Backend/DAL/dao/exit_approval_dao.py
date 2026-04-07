from sqlalchemy import select
from Backend.Business_Layer.utils.uuid_generator import generate_uuid7
from ..models.models import ExitApprovals


class ExitApprovalDAO:

    async def create_exit_approval(self, db, data):

        new_approval = ExitApprovals(

            approval_uuid=str(generate_uuid7()),
            exit_uuid=data.exit_uuid,
            approval_type=data.approval_type,
            remarks=data.remarks,
            approved_by=data.approved_by

        )

        db.add(new_approval)
        await db.commit()
        await db.refresh(new_approval)

        return new_approval