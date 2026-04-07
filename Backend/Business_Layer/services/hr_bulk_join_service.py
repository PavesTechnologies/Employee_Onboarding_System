
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.dao.hr_bulk_join_dao import HrBulkJoinDAO
from Backend.Business_Layer.utils.email_utils import send_joining_email

class HrBulkJoinService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = HrBulkJoinDAO(self.db)

    async def process_bulk_join(self, payload, current_user_id: int):

        if not payload.user_emails_list:
            raise HTTPException(status_code=400, detail="No users selected")

        verified_users = await self.dao.get_verified_users_by_emails(
            payload.user_emails_list
        )

        if not verified_users:
            raise HTTPException(
                status_code=400,
                detail="No VERIFIED candidates found"
            )

        # ✅ 1. STORE JOINING DATE 
        updated_rows = await self.dao.update_joining_date_for_verified(
            payload.user_emails_list,
            payload.joining_date,
            payload
        )
        joining_date_str = payload.joining_date.strftime("%d %B %Y")

        # ✅ 2. SEND EMAIL FROM BACKEND 
        for user in verified_users:
            send_joining_email(
                
                to_email=user.mail,
                name=user.first_name,
                joining_date_str = joining_date_str,
                location=payload.location,
                reporting_time=payload.reporting_time,
                department=payload.department,
                reporting_manager=payload.reporting_manager,
                custom_message=payload.custom_message
            )

        skipped = len(payload.user_emails_list) - updated_rows

        return {
            "message": "Bulk Join processed successfully",
            "joining_date": payload.joining_date,
            "updated_verified_users": updated_rows,
            "skipped_not_verified": skipped
        }


    async def reassign_joining(self, payload, current_user_id: int):

        user = await self.dao.get_user_by_uuid(payload.user_uuid)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # ✅ Update only required fields
        await self.dao.update_joining_date_for_user(
            payload.user_uuid,
            payload.new_joining_date,
            payload.reporting_time
        )

        # ✅ Keep existing values from DB
        joining_date_str = payload.new_joining_date.strftime("%d %B %Y")

        send_joining_email(
           to_email=user.mail,
        name=user.first_name,

        # ✅ updated values
        joining_date_str=joining_date_str,
        reporting_time=payload.reporting_time,

        # ✅ fresh frontend values
        location=payload.location,
        department=payload.department,
        reporting_manager=payload.reporting_manager,

        custom_message=payload.joining_comments
        )

        return {
            "message": "Joining date reassigned successfully",
            "user_uuid": payload.user_uuid
        }