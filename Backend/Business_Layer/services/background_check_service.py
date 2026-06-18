import io
import zipfile

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from Backend.API_Layer.interfaces.background_check_interfaces import (
    BackgroundCheckCreateRequest,
    FinalBGVDecisionRequest,
    SendToConsultancyRequest,
    BackgroundCheckStatusUpdateRequest,
    BackgroundCheckUpdateRequest,
)
from Backend.Business_Layer.utils.uuid_generator import generate_uuid7
from Backend.DAL.dao.background_check_dao import BackgroundCheckDAO
from Backend.DAL.models.models import (
    BackgroundCheck, BackgroundCheckDocument,
    OfferLetterDetails, PersonalDetails, Countries,
    Addresses, EmployeeBankDetails, EmployeePfDetails,
)
from Backend.DAL.utils.storage_utils import S3StorageService


class BackgroundCheckService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = BackgroundCheckDAO(db)

    def _normalize_check_type(self, label: str, check_type: str | None) -> str:
        if check_type:
            return check_type.strip()
        value = label
        return "_".join(value.strip().upper().split())

    def _check_to_response(self, check: BackgroundCheck) -> dict:
        return {
            "check_uuid": check.check_uuid,
            "user_uuid": check.user_uuid,
            "check_type": check.check_type,
            "label": check.label,
            "group": check.check_group,
            "status": check.status,
            "notes": check.notes or "",
            "details": check.details or {},
            "doc_category": check.doc_category,
            "document_id": check.document_id,
            "created_by": check.created_by,
            "created_at": check.created_at,
            "updated_at": check.updated_at,
        }

    def _document_to_response(self, document: BackgroundCheckDocument) -> dict:
        return {
            "document_id": document.document_id,
            "user_uuid": document.user_uuid,
            "category": document.category,
            "document_name": document.document_name,
            "doc_type": document.doc_type,
            "file_path": document.file_path,
            "uploaded_at": document.uploaded_at,
        }

    async def get_bgv_profile(self, user_uuid: str) -> dict:
        offer_res = await self.db.execute(
            select(OfferLetterDetails).where(OfferLetterDetails.user_uuid == user_uuid)
        )
        offer = offer_res.scalar_one_or_none()
        if not offer:
            raise HTTPException(status_code=404, detail="Employee not found")

        pd_res = await self.db.execute(
            select(PersonalDetails).where(PersonalDetails.user_uuid == user_uuid)
        )
        pd = pd_res.scalar_one_or_none()

        nationality = None
        if pd and pd.nationality_country_uuid:
            nat_res = await self.db.execute(
                select(Countries.country_name).where(
                    Countries.country_uuid == pd.nationality_country_uuid
                )
            )
            nationality = nat_res.scalar_one_or_none()

        addr_res = await self.db.execute(
            select(Addresses, Countries.country_name)
            .outerjoin(Countries, Addresses.country_uuid == Countries.country_uuid)
            .where(Addresses.user_uuid == user_uuid)
        )
        addresses = [
            {
                "address_type": row[0].address_type,
                "address_line1": row[0].address_line1,
                "address_line2": row[0].address_line2,
                "city": row[0].city,
                "state_or_region": row[0].state_or_region,
                "postal_code": row[0].postal_code,
                "country": row[1],
            }
            for row in addr_res.all()
        ]

        bank_res = await self.db.execute(
            select(EmployeeBankDetails).where(EmployeeBankDetails.user_uuid == user_uuid)
        )
        bank = bank_res.scalar_one_or_none()

        pf_res = await self.db.execute(
            select(EmployeePfDetails).where(EmployeePfDetails.user_uuid == user_uuid)
        )
        pf = pf_res.scalar_one_or_none()

        return {
            "offer": {
                "user_uuid": offer.user_uuid,
                "first_name": offer.first_name,
                "last_name": offer.last_name,
                "email": offer.mail,
                "contact_number": offer.contact_number,
                "designation": offer.designation,
                "offer_status": offer.status,
            },
            "personal_details": {
                "date_of_birth": str(pd.date_of_birth) if pd and pd.date_of_birth else None,
                "gender": pd.gender if pd else None,
                "blood_group": pd.blood_group if pd else None,
                "marital_status": pd.marital_status if pd else None,
                "nationality": nationality,
            },
            "addresses": addresses,
            "bank_details": {
                "account_holder_name": bank.account_holder_name,
                "bank_name": bank.bank_name,
                "branch_name": bank.branch_name,
                "account_number": bank.account_number,
                "ifsc_code": bank.ifsc_code,
                "account_type": bank.account_type,
            } if bank else None,
            "pf_details": {
                "pf_member": pf.pf_member,
                "uan_number": pf.uan_number,
            } if pf else None,
        }

    async def create_check(self, request_data: BackgroundCheckCreateRequest, created_by: str | None = None):
        check_type = self._normalize_check_type(request_data.label, request_data.check_type)

        # Upsert: if a record already exists for this (user_uuid, check_type) pair,
        # update it with the incoming values rather than raising 409.
        existing = await self.dao.get_check_by_user_and_check_type(
            request_data.user_uuid, check_type
        )
        if existing:
            if request_data.status is not None:
                existing.status = request_data.status.value
            if request_data.notes is not None:
                existing.notes = request_data.notes
            if request_data.details is not None:
                existing.details = request_data.details
            if request_data.label:
                existing.label = request_data.label
            result = await self.dao.update_check(existing)
            return self._check_to_response(result)

        resolved_created_by = created_by or request_data.created_by
        check = BackgroundCheck(
            check_uuid=generate_uuid7(),
            user_uuid=request_data.user_uuid,
            check_type=check_type,
            label=request_data.label,
            check_group=request_data.group,
            status=request_data.status.value,
            notes=request_data.notes,
            details=request_data.details,
            doc_category=request_data.doc_category,
            document_id=request_data.document_id,
            created_by=resolved_created_by,
        )
        try:
            result = await self.dao.create_check(check)
            return self._check_to_response(result)
        except IntegrityError:
            raise HTTPException(
                status_code=409,
                detail="Background check already exists for this user and check type",
            )

    async def get_checks_by_user_uuid(self, user_uuid: str):
        checks = await self.dao.get_checks_by_user_uuid(user_uuid)
        return [self._check_to_response(check) for check in checks]

    async def get_check_by_uuid(self, check_uuid: str):
        check = await self.dao.get_check_by_uuid(check_uuid)
        if not check:
            raise HTTPException(status_code=404, detail="Background check not found")
        return self._check_to_response(check)

    async def update_check(
        self, check_uuid: str, request_data: BackgroundCheckUpdateRequest
    ):
        check = await self.dao.get_check_by_uuid(check_uuid)
        if not check:
            raise HTTPException(status_code=404, detail="Background check not found")

        if request_data.label is not None:
            check.label = request_data.label
        if request_data.check_type is not None:
            check.check_type = self._normalize_check_type(
                check.label, request_data.check_type
            )
        if request_data.group is not None:
            check.check_group = request_data.group
        if request_data.status is not None:
            check.status = request_data.status.value
        if request_data.notes is not None:
            check.notes = request_data.notes
        if request_data.details is not None:
            check.details = request_data.details
        if request_data.doc_category is not None:
            check.doc_category = request_data.doc_category
        if request_data.document_id is not None:
            check.document_id = request_data.document_id
        if request_data.created_by is not None:
            check.created_by = request_data.created_by

        try:
            result = await self.dao.update_check(check)
            return self._check_to_response(result)
        except IntegrityError:
            raise HTTPException(
                status_code=409,
                detail="Background check already exists for this user and check type",
            )

    async def update_status(
        self, check_uuid: str, request_data: BackgroundCheckStatusUpdateRequest
    ):
        check = await self.dao.get_check_by_uuid(check_uuid)
        if not check:
            raise HTTPException(status_code=404, detail="Background check not found")

        check.status = request_data.status.value
        if request_data.notes is not None:
            check.notes = request_data.notes

        result = await self.dao.update_check(check)
        return self._check_to_response(result)

    async def delete_check(self, check_uuid: str):
        check = await self.dao.get_check_by_uuid(check_uuid)
        if not check:
            raise HTTPException(status_code=404, detail="Background check not found")

        if check.document_id:
            document = await self.dao.get_document_by_id(check.document_id)
            if document:
                storage = S3StorageService()
                await storage.delete_file(document.file_path)
                await self.dao.delete_document(document)

        await self.dao.delete_check(check)
        return {"check_uuid": check_uuid, "message": "Background check deleted"}

    async def upload_document(
        self,
        user_uuid: str,
        category: str,
        file,
        document_name: str | None = None,
        doc_type: str | None = None,
        uploaded_by: str | None = None,
    ):
        storage = S3StorageService()
        file_path = await storage.upload_file(
            file,
            "background_check_documents",
            original_filename=file.filename,
            employee_uuid=user_uuid,
        )
        document = BackgroundCheckDocument(
            document_id=generate_uuid7(),
            user_uuid=user_uuid,
            category=category,
            document_name=document_name or file.filename,
            doc_type=doc_type or file.content_type,
            file_path=file_path,
            uploaded_by=uploaded_by,
        )
        result = await self.dao.create_document(document)
        return self._document_to_response(result)

    async def get_documents_by_user_uuid(self, user_uuid: str):
        documents = await self.dao.get_documents_by_user_uuid(user_uuid)
        return [self._document_to_response(document) for document in documents]

    async def get_document_by_id(self, document_id: str):
        document = await self.dao.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return self._document_to_response(document)

    async def view_document(self, file_path: str):
        document = await self.dao.get_document_by_file_path(file_path)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        storage = S3StorageService()
        return await storage.get_presigned_url(file_path)

    async def delete_document(self, document_id: str):
        document = await self.dao.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        file_path = document.file_path
        storage = S3StorageService()
        await storage.delete_file(file_path)
        await self.dao.delete_document(document)
        return {
            "document_id": document_id,
            "file_path": file_path,
            "message": "Background check document deleted",
        }

    async def send_to_consultancy(self, request_data: SendToConsultancyRequest):
        # Block duplicate sends: check employee bgv_status first
        blocked_statuses = {"AWAITING_BGV_RESULT", "CLEARED", "REJECTED"}
        emp_status_res = await self.db.execute(
            text("SELECT bgv_status FROM employee_details WHERE user_uuid = :uuid"),
            {"uuid": request_data.user_uuid},
        )
        current_bgv_status = emp_status_res.scalar_one_or_none()
        if current_bgv_status in blocked_statuses:
            raise HTTPException(
                status_code=409,
                detail="BGV request has already been sent to the consultancy for this employee. Please wait for the final verification result before sending again.",
            )

        # Also block if any of the selected checks are already IN_REVIEW
        checks = []
        if request_data.check_ids:
            checks = await self.dao.get_checks_by_uuids(request_data.check_ids)
            found_ids = {check.check_uuid for check in checks}
            missing_ids = [
                check_id
                for check_id in request_data.check_ids
                if check_id not in found_ids
            ]
            if missing_ids:
                raise HTTPException(
                    status_code=404,
                    detail=f"Background checks not found: {', '.join(missing_ids)}",
                )
        else:
            checks = await self.dao.get_checks_by_user_uuid(request_data.user_uuid)

        if any(c.status == "IN_REVIEW" for c in checks):
            raise HTTPException(
                status_code=409,
                detail="BGV request has already been sent to the consultancy for this employee. Please wait for the final verification result before sending again.",
            )

        # All real (non-sentinel) checks for this employee must be VERIFIED before sending
        # Always validate against ALL employee checks, not just the selected ones
        def is_sentinel(check):
            return check.check_type and (
                check.check_type.startswith("__session__") or
                check.check_type.startswith("__hidden__")
            )

        all_emp_checks = await self.dao.get_checks_by_user_uuid(request_data.user_uuid)
        all_real_checks = [c for c in all_emp_checks if not is_sentinel(c)]
        if not all_real_checks:
            raise HTTPException(status_code=422, detail="No verification tasks found to send.")
        not_verified = [c for c in all_real_checks if c.status != "VERIFIED"]
        if not_verified:
            raise HTTPException(
                status_code=422,
                detail=f"All verification tasks must be marked as Verified before sending. {len(not_verified)} task(s) are not yet verified.",
            )

        # Persist IN_REVIEW for every selected check
        for check in checks:
            if check.status != "IN_REVIEW":
                check.status = "IN_REVIEW"
                await self.dao.update_check(check)

        # Fetch employee details for the email template
        from Backend.DAL.dao.permanent_employee_details_dao import PermanentEmployeeDetailsDAO
        emp_dao = PermanentEmployeeDetailsDAO()
        emp = await emp_dao.get_employee_by_user_uuid(self.db, request_data.user_uuid)
        emp_name = f"{emp.first_name} {emp.last_name}".strip() if emp else request_data.user_uuid
        emp_id = emp.employee_id if emp else "N/A"

        check_bullets = "\n".join(
            f"  • {check.label}" for check in checks
        ) if checks else "  • No checks selected."

        content = f"""Dear Team,

Please find attached the background verification documents for the employee mentioned below.

Employee Name: {emp_name}
Employee ID: {emp_id}

Verification Checks Requested:
{check_bullets}

Kindly review the submitted documents and perform the required background verification checks.

Please share the verification outcome once the review is completed.

If any additional information or documents are required, please let us know.

Thank you.

Regards,
HR Team
Paves Technologies"""

        # Build ZIP of all uploaded documents for the selected checks
        storage = S3StorageService()
        zip_buffer = io.BytesIO()
        docs_added = 0
        with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for check in checks:
                if not check.document_id:
                    continue
                document = await self.dao.get_document_by_id(check.document_id)
                if not document or not document.file_path:
                    continue
                try:
                    file_bytes = await storage.download_file(document.file_path)
                    # Use original document name; fall back to check label + extension
                    filename = document.document_name or f"{check.label}.bin"
                    # Avoid duplicate filenames in the zip
                    arcname = f"{check.label}_{filename}" if docs_added > 0 else filename
                    zf.writestr(arcname, file_bytes)
                    docs_added += 1
                except Exception as e:
                    print(f"⚠️ Could not download document for check {check.check_uuid}: {e}")

        zip_buffer.seek(0)
        zip_bytes = zip_buffer.read() if docs_added > 0 else None

        cc_emails = (
            [request_data.cc_email]
            if request_data.cc_email and request_data.cc_email.strip()
            else None
        )
        from Backend.Business_Layer.utils.email_utils import send_email

        send_email(
            to_email=request_data.to_email,
            subject=f"Background Verification Request – {emp_name}",
            content=content,
            cc_emails=cc_emails,
            attachment_bytes=zip_bytes,
            attachment_filename="bgv_documents.zip" if zip_bytes else None,
        )

        await self.db.execute(
            text("UPDATE employee_details SET bgv_status = 'AWAITING_BGV_RESULT' WHERE user_uuid = :uuid"),
            {"uuid": request_data.user_uuid},
        )
        await self.db.flush()

        return {
            "user_uuid": request_data.user_uuid,
            "to_email": request_data.to_email,
            "selected_check_count": len(checks),
            "docs_attached": docs_added,
            "message": "Background verification request sent to consultancy",
        }

    async def final_decision(self, user_uuid: str, request_data: FinalBGVDecisionRequest, decided_by: str | None = None):
        decision = request_data.decision.value  # "CLEARED" or "REJECTED"

        if decision not in ("CLEARED", "REJECTED"):
            raise HTTPException(status_code=400, detail="Decision must be CLEARED or REJECTED")

        tasks_updated = 0
        if decision == "CLEARED":
            # Mark all real checks for this employee as VERIFIED
            all_checks = await self.dao.get_checks_by_user_uuid(user_uuid)
            for check in all_checks:
                sentinel = (
                    check.check_type.startswith("__session__") or
                    check.check_type.startswith("__hidden__")
                ) if check.check_type else False
                if not sentinel and check.status != "VERIFIED":
                    check.status = "VERIFIED"
                    await self.dao.update_check(check)
                    tasks_updated += 1

        await self.db.execute(
            text(
                "UPDATE employee_details "
                "SET bgv_status = :status, bgv_remarks = :remarks, bgv_decided_by = :decided_by "
                "WHERE user_uuid = :uuid"
            ),
            {"status": decision, "remarks": request_data.remarks, "decided_by": decided_by, "uuid": user_uuid},
        )
        await self.db.flush()

        return {
            "user_uuid": user_uuid,
            "decision": decision,
            "tasks_updated": tasks_updated,
            "message": f"BGV final decision recorded: {decision}",
        }
