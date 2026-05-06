from datetime import date

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...DAL.dao.hr_bulk_join_dao import HrBulkJoinDAO
from Backend.Business_Layer.utils.email_utils import send_joining_email


class HrBulkJoinService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = HrBulkJoinDAO(self.db)

    # ✅ Status Logic
    def get_joining_status(self, new_joining_date, is_reassigned=False):
        today = date.today()

        print("\n========== STATUS DEBUG ==========")
        print("TODAY :", today)
        print("JOINING DATE :", new_joining_date)
        print("IS REASSIGNED :", is_reassigned)

        # Joining date already passed
        if new_joining_date < today:
            print("RETURNING STATUS : Joining Pending")
            return "Joining Pending"

        # Only when HR changes existing joining date
        if is_reassigned:
            print("RETURNING STATUS : Rescheduled")
            return "Rescheduled"

        # First-time joining letter
        print("RETURNING STATUS : Joining")
        return "Joining"

    # ✅ First-time Bulk Joining
    async def process_bulk_join(self, payload, current_user_id: int):

        print("\n========== BULK JOIN API CALLED ==========")
        print("CURRENT USER ID :", current_user_id)
        print("PAYLOAD :", payload)

        if not payload.user_emails_list:
            raise HTTPException(
                status_code=400,
                detail="No users selected"
            )

        print("USER EMAIL LIST :", payload.user_emails_list)

        verified_users = await self.dao.get_verified_users_by_emails(
            payload.user_emails_list
        )

        print("VERIFIED USERS FOUND :", len(verified_users))

        if not verified_users:
            raise HTTPException(
                status_code=400,
                detail="No VERIFIED candidates found"
            )

        # ✅ First-time joining
        status = self.get_joining_status(
            payload.joining_date
        )

        print("FINAL STATUS FROM FUNCTION :", status)

        updated_rows = await self.dao.update_joining_date_for_verified(
            payload.user_emails_list,
            payload.joining_date,
            payload,
            status
        )

        print("UPDATED ROWS :", updated_rows)

        joining_date_str = payload.joining_date.strftime("%d %B %Y")

        for user in verified_users:

            print(f"SENDING EMAIL TO : {user.mail}")

            send_joining_email(
                to_email=user.mail,
                name=user.first_name,
                joining_date_str=joining_date_str,
                location=payload.location,
                reporting_time=payload.reporting_time,
                department=payload.department,
                reporting_manager=payload.reporting_manager,
                custom_message=payload.custom_message
            )

        skipped = len(payload.user_emails_list) - updated_rows

        print("SKIPPED USERS :", skipped)

        return {
            "message": "Bulk Join processed successfully",
            "joining_date": payload.joining_date,
            "status": status,
            "updated_verified_users": updated_rows,
            "skipped_not_verified": skipped
        }

    # ✅ Reassign Joining Date
    async def reassign_joining(self, payload, current_user_id: int):

        print("\n========== REASSIGN API CALLED ==========")
        print("CURRENT USER ID :", current_user_id)
        print("PAYLOAD :", payload)

        user = await self.dao.get_user_by_uuid(
            payload.user_uuid
        )

        print("USER FOUND :", user)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # ✅ Reassigned joining date
        status = self.get_joining_status(
            payload.new_joining_date,
            is_reassigned=True
        )

        print("FINAL STATUS FROM FUNCTION :", status)

        await self.dao.update_joining_date_for_user(
            payload.user_uuid,
            payload,
            status
        )

        print("DATABASE UPDATED SUCCESSFULLY")

        joining_date_str = payload.new_joining_date.strftime("%d %B %Y")

        print(f"SENDING EMAIL TO : {user.mail}")

        send_joining_email(
            to_email=user.mail,
            name=user.first_name,
            joining_date_str=joining_date_str,
            reporting_time=payload.reporting_time,
            location=payload.location,
            department=payload.department,
            reporting_manager=payload.reporting_manager,
            custom_message=payload.joining_comments
        )

        return {
            "message": "Joining date reassigned successfully",
            "status": status,
            "user_uuid": payload.user_uuid
        }
    

    # ✅ Get employees under reporting manager
    async def get_employees_under_manager(
        self,
        user_uuid: str
    ):
        # Step 1 — Find manager using UUID
        manager = await self.dao.get_user_by_uuid(user_uuid)

        if not manager:
            raise HTTPException(
                status_code=404,
                detail="Manager not found"
            )

        # Step 2 — Create manager full name
        manager_name = (
            f"{manager.first_name} {manager.last_name}"
        ).strip()

        # Step 3 — Find employees under manager
        employees = await self.dao.get_employees_under_manager(
            manager_name
        )

        # Step 4 — Return response
        return [
            {
                "user_uuid": emp.user_uuid,
                "name": f"{emp.first_name} {emp.last_name}".strip(),
                "employee_id": getattr(emp, "employee_id", None)
            }
            for emp in employees
        ]