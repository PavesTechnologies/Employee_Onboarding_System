# Backend/DAL/dao/offerletter_dao.py
import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.models.models import OfferApprovalAction, OfferApprovalRequest, OfferCompensation, OfferLetterDetails
from ...API_Layer.interfaces.offerletter_interfaces import OfferCreateRequest
import time


class OfferLetterDAO:
    def __init__(self, db: AsyncSession):
        self.db = db  # Store the session for transaction management

    async def get_offer_by_user_uuid(self, user_uuid: str):
        result = await self.db.execute(
            select(OfferLetterDetails).where(
                OfferLetterDetails.user_uuid == user_uuid
            )
        )
        offer = result.scalar_one_or_none()

        if offer and offer.cc_emails:
            offer.cc_mails = [
                mail.strip()
                for mail in offer.cc_emails.split(",")
                if mail.strip()
            ]
        else:
            offer.cc_mails = []

        return offer

    async def create_offer(self, uuid: str, request_data: OfferCreateRequest, current_user_id: int) -> OfferLetterDetails:
        """
        Create a single offer with immediate commit.
        Use for single offer creation.
        """
        new_offer = OfferLetterDetails(
            user_uuid=uuid,
            first_name=request_data.first_name,
            middle_name=request_data.middle_name,
            last_name=request_data.last_name,
            mail=request_data.mail,
            country_code=request_data.country_code,
            created_by=current_user_id,
            contact_number=request_data.contact_number,
            designation=request_data.designation,
            employee_type=request_data.employee_type,
            # package=request_data.package,
            # currency=request_data.currency,
            total_ctc=request_data.total_ctc,
            cc_emails=",".join(request_data.cc_mails) if request_data.cc_mails else None,
        )
        self.db.add(new_offer)

        # ensure offer exists before children
        await self.db.flush()

        #save compensation components
        for comp in request_data.compensation_components:
                row = OfferCompensation(
                    offer_uuid=uuid,
                    name=comp.name,
                    type=comp.type,
                    frequency=comp.frequency,
                    amount=comp.amount
                )
                self.db.add(row)
         
        return new_offer

    async def create_offer_no_commit(self, uuid: str, request_data: OfferCreateRequest, current_user_id: int) -> OfferLetterDetails:
        """
        Create a single offer WITHOUT committing.
        Use inside a transaction context for bulk operations.
        Caller is responsible for committing the transaction.
        """
        new_offer = OfferLetterDetails(
            user_uuid=uuid,
            first_name=request_data.first_name,
            last_name=request_data.last_name,
            mail=request_data.mail,
            country_code=request_data.country_code,
            created_by=current_user_id,
            contact_number=request_data.contact_number,
            designation=request_data.designation,
            employee_type=request_data.employee_type,
            package=request_data.package,
            currency=request_data.currency,
            cc_emails=",".join(request_data.cc_mails) if request_data.cc_mails else None,
        )
        self.db.add(new_offer)
        # Don't commit - let the caller handle it
        return new_offer

    async def get_offer_by_email(self, mail: str):
        """
        Get a single offer by email.
        """
        result = await self.db.execute(
            select(1).where(OfferLetterDetails.mail == mail)
        )
        return result.first()

    async def get_offers_by_emails(self, emails: list) -> list:
        """
        Get all offers matching any email in the list.
        Returns list of email addresses that already exist.
        """
        if not emails:
            return []
        
        result = await self.db.execute(
            select(OfferLetterDetails.mail).where(OfferLetterDetails.mail.in_(emails))
        )
        return result.scalars().all()

    async def get_all_offers(self):
        """
        Get all offers.
        """
        result = await self.db.execute(select(OfferLetterDetails))
        return result.scalars().all()

    async def get_offer_by_user_id(self, user_id: int):
        start = time.perf_counter()

        stmt = (
            select(
                OfferLetterDetails.user_uuid,
                OfferLetterDetails.first_name,
                OfferLetterDetails.middle_name,   
                OfferLetterDetails.last_name,
                OfferLetterDetails.mail,
                OfferLetterDetails.country_code,
                OfferLetterDetails.contact_number,
                OfferLetterDetails.designation,
                OfferLetterDetails.employee_type,
                # OfferLetterDetails.package,
                # OfferLetterDetails.currency,
                OfferLetterDetails.total_ctc,
                OfferLetterDetails.created_by,
                OfferLetterDetails.status,
                OfferLetterDetails.cc_emails
            )
            .where(OfferLetterDetails.created_by == user_id)
        )

        t1 = time.perf_counter()
        result = await self.db.execute(stmt)
        print("⏱ DB execute:", time.perf_counter() - t1)

        t2 = time.perf_counter()
        rows = result.all()
        print("⏱ Result processing:", time.perf_counter() - t2)

        print("⏱ DAO total:", time.perf_counter() - start)

        return rows

    async def get_offer_by_uuid(self, user_uuid: str):
        start = time.perf_counter()
            
        stmt = (
                 select(OfferLetterDetails)
                .where(OfferLetterDetails.user_uuid == user_uuid)
                .limit(1)
            )

        result = await self.db.execute(stmt)
        offer = result.scalar_one_or_none()

        if not offer:
             return None

        # 2️⃣ Fetch compensation rows
        comp_stmt = (
                    select(OfferCompensation)
                    .where(OfferCompensation.offer_uuid == user_uuid)
                )

        comp_result = await self.db.execute(comp_stmt)
        compensations = comp_result.scalars().all()

        # 3️⃣ Convert compensation rows to list of dicts
        compensation_list = [
                {
                    "name": c.name,
                    "type": c.type,
                    "frequency": c.frequency,
                    "amount": float(c.amount)
                }
                for c in compensations
            ]

        print("⏱ DAO total:", time.perf_counter() - start)

        # 4️⃣ Return structured response 
        return {
                
            "user_uuid": offer.user_uuid,
            "first_name": offer.first_name,
            "middle_name":offer.middle_name,
            "last_name": offer.last_name,
            "mail": offer.mail,
            "country_code": offer.country_code,
            "contact_number": offer.contact_number,
            "designation": offer.designation,
            "employee_type": offer.employee_type,
            "package": offer.package,
            "currency": offer.currency,
            "created_by": offer.created_by,
            "status": offer.status,
            
            "cc_mails": offer.cc_emails.split(",") if offer.cc_emails else [],
            "total_ctc": offer.total_ctc,
            "compensation_components": compensation_list
        }

    async def update_offer_by_uuid(
        self,
        user_uuid: str,
        request_data: OfferCreateRequest,
        current_user_id: int,
    ):

        stmt = (
            update(OfferLetterDetails)
            .where(OfferLetterDetails.user_uuid == user_uuid)
            .values(
                first_name=request_data.first_name,
                last_name=request_data.last_name,
                mail=request_data.mail,
                country_code=request_data.country_code,
                contact_number=request_data.contact_number,
                designation=request_data.designation,
                employee_type=request_data.employee_type,
                package=request_data.package,
                currency=request_data.currency,
                job_id=request_data.job_id,
                cc_emails=",".join(request_data.cc_emails) if request_data.cc_emails else None,
            )
        )

        result = await self.db.execute(stmt)

        # If no rows updated → record does not exist
        if result.rowcount == 0:
            return None
        await self.db.commit()

        return True

    async def fetch_created_offerletters(self, created_by: int):
        """
        Returns all offer letters:
        - status = 'created'
        - created_by = <current user>
        """

        query = (
            select(OfferLetterDetails)
            .where(
                OfferLetterDetails.status == "Created",
                OfferLetterDetails.created_by == created_by
            )
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_offerletter_status(self, user_uuid: str, new_status: str, current_user_id: int):
        """
        Update only the status of an offer letter by UUID.
        """

        # 1. Fetch record
        result = await self.db.execute(
            select(OfferLetterDetails).where(OfferLetterDetails.user_uuid == user_uuid)
        )
        offer = result.scalar_one_or_none()

        if not offer:
            return None

        # 2. Update fields
        offer.status = new_status
        offer.created_by = current_user_id

        # 3. Commit
        await self.db.commit()
        return offer

    async def update_pandadoc_draft_id(self, user_uuid: str, draft_id: str):
        """
        Update the PandaDoc draft ID for an offer letter by user UUID.
        """

        # 1. Fetch record
        result = await self.db.execute(
            select(OfferLetterDetails).where(OfferLetterDetails.user_uuid == user_uuid)
        )
        offer = result.scalar_one_or_none()

        if not offer:
            return None

        # 2. Update fields
        offer.pandadoc_draft_id = draft_id

        # 3. Commit
        await self.db.commit()
        return offer

    async def get_pandadoc_draft_id(self, user_uuid: str):
        """
        Fetch only the PandaDoc draft ID for an offer letter by user UUID.
        """

        # 1. Fetch only the draft_id column
        result = await self.db.execute(
            select(OfferLetterDetails.pandadoc_draft_id)
            .where(OfferLetterDetails.user_uuid == user_uuid)
        )
        draft_id = result.scalar_one_or_none()

        # 2. Return the value
        return draft_id

    async def get_upcoming_joinings(self):

        today = datetime.date.today()
        three_days_later = today + datetime.timedelta(days=3)
    
        stmt = (
            select(OfferLetterDetails)
            .where(
                OfferLetterDetails.joining_date == three_days_later
            )
        )

        result = await self.db.execute(stmt)

        return result.scalars().all()

    async def get_approval_request_by_user_uuid(self, user_uuid:str):
        stmt = (
            select(OfferApprovalRequest)
            .where(OfferApprovalRequest.user_uuid == user_uuid)
            .limit(1)

        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_approval_action(self, request_id: int):
        stmt = (
            select(OfferApprovalAction)
            .where(OfferApprovalAction.id == request_id)
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_offer_letter(self, user_uuid: str):
        """
        Delete an offer letter by user UUID.
        """

        # 1. Fetch record
        result = await self.db.execute(
            select(OfferLetterDetails).where(OfferLetterDetails.user_uuid == user_uuid)
        )
        offer = result.scalar_one_or_none()

        if not offer:
            return None

        # 2. Delete the record
        await self.db.delete(offer)
        return True
