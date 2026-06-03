from Backend.API_Layer.interfaces import exit_final_settlement_interface
from datetime import date

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...DAL.dao.hr_bulk_join_dao import HrBulkJoinDAO
from ...Business_Layer.services.document_service import DocumentService
from Backend.Business_Layer.utils.email_utils import send_joining_email


class HrBulkJoinService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = HrBulkJoinDAO(self.db)

    async def resolve_reporting_manager(self, reporting_manager):
        manager = await self.dao.get_employee_by_manager_value(reporting_manager)

        if not manager:
            raise HTTPException(
                status_code=400,
                detail="Invalid reporting manager selected"
            )

        return {
            "employee_id": manager.employee_id,
            "name": f"{manager.first_name} {manager.last_name}".strip()
        }

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

    def build_joining_pdf_data(
        self,
        user,
        joining_date,
        location: str,
        reporting_time: str,
        department: str,
        reporting_manager_name: str,
        custom_message: str | None = None
    ):
        return {
            "user_uuid": user.user_uuid,
            "first_name": user.first_name,
            "middle_name": user.middle_name,
            "last_name": user.last_name,
            "mail": user.mail,
            "country_code": user.country_code,
            "contact_number": user.contact_number,
            "designation": user.designation,
            "department": department,
            "joining_date": joining_date.strftime("%d %B %Y"),
            "reporting_time": reporting_time,
            "location": location,
            "reporting_manager": reporting_manager_name,
            "custom_message": custom_message
        }

    # ✅ First-time Bulk Joining
    async def generate_bulk_join_preview(self, payload):

        if not payload.user_emails_list:
            raise HTTPException(
                status_code=400,
                detail="No users selected"
            )

        verified_users = await self.dao.get_verified_users_by_emails(
            payload.user_emails_list
        )

        if not verified_users:
            raise HTTPException(
                status_code=400,
                detail="No VERIFIED candidates found"
            )

        user = verified_users[0]
        reporting_manager = await self.resolve_reporting_manager(
            payload.reporting_manager
        )

        joining_pdf_data = self.build_joining_pdf_data(
            user=user,
            joining_date=payload.joining_date,
            location=payload.location,
            reporting_time=payload.reporting_time,
            department=payload.department,
            reporting_manager_name=reporting_manager["name"],
            custom_message=payload.custom_message
        )

        return DocumentService().generate_joining_pdf(joining_pdf_data)

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

        reporting_manager = await self.resolve_reporting_manager(
            payload.reporting_manager
        )

        updated_rows = await self.dao.update_joining_date_for_verified(
            payload.user_emails_list,
            payload.joining_date,
            payload,
            status,
            reporting_manager["employee_id"]
        )

        print("UPDATED ROWS :", updated_rows)

        joining_date_str = payload.joining_date.strftime("%d %B %Y")
        document_service = DocumentService()

        for user in verified_users:

            print(f"SENDING EMAIL TO : {user.mail}")
            joining_pdf_data = self.build_joining_pdf_data(
                user=user,
                joining_date=payload.joining_date,
                location=payload.location,
                reporting_time=payload.reporting_time,
                department=payload.department,
                reporting_manager_name=reporting_manager["name"],
                custom_message=payload.custom_message
            )
            pdf_path = document_service.generate_joining_pdf(joining_pdf_data)

            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()

            send_joining_email(
                to_email=user.mail,
                name=user.first_name,
                joining_date_str=joining_date_str,
                location=payload.location,
                reporting_time=payload.reporting_time,
                department=payload.department,
                reporting_manager=reporting_manager["name"],
                custom_message=payload.custom_message,
                attachment_bytes=pdf_bytes,
                attachment_filename=f"joining_letter_{user.user_uuid}.pdf"
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

        reporting_manager = await self.resolve_reporting_manager(
            payload.reporting_manager
        )

        await self.dao.update_joining_date_for_user(
            payload.user_uuid,
            payload,
            status,
            reporting_manager["employee_id"]
        )

        print("DATABASE UPDATED SUCCESSFULLY")

        joining_date_str = payload.new_joining_date.strftime("%d %B %Y")
        document_service = DocumentService()
        joining_pdf_data = self.build_joining_pdf_data(
            user=user,
            joining_date=payload.new_joining_date,
            location=payload.location,
            reporting_time=payload.reporting_time,
            department=payload.department,
            reporting_manager_name=reporting_manager["name"],
            custom_message=payload.joining_comments
        )
        pdf_path = document_service.generate_joining_pdf(joining_pdf_data)

        with open(pdf_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        print(f"SENDING EMAIL TO : {user.mail}")

        send_joining_email(
            to_email=user.mail,
            name=user.first_name,
            joining_date_str=joining_date_str,
            reporting_time=payload.reporting_time,
            location=payload.location,
            department=payload.department,
            reporting_manager=reporting_manager["name"],
            custom_message=payload.joining_comments,
            attachment_bytes=pdf_bytes,
            attachment_filename=f"joining_letter_{user.user_uuid}.pdf"
        )

        return {
            "message": "Joining date reassigned successfully",
            "status": status,
            "user_uuid": payload.user_uuid
        }
    

    async def get_employees_under_manager(self, employee_id: str):
        """
        Given a manager's employee_id, return all employees
        whose reporting_manager_uuid equals that employee_id.
        """
        employees = await self.dao.get_employees_under_manager(employee_id)

        return [
            {
                "employee_id": employee.employee_id,
                "user_uuid": employee.user_uuid,
                "name": " ".join(
                    part for part in [
                        employee.first_name,
                        employee.middle_name,
                        employee.last_name
                    ]
                    if part
                ).strip()
            }
            for employee in employees
        ]
