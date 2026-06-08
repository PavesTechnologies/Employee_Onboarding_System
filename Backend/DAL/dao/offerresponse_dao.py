from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.models.models import OfferLetterDetails


class OfferResponseDAO:
    def __init__(self, db: AsyncSession):
        self.db = db  # Store the session for transaction management

    async def update_offer_acceptance_from_webhook(self, update_data: dict):
        """
        Update offer letter fields when PandaDoc webhook notifies completion.
        """

        doc_id = update_data["doc_id"]
        new_status = update_data["new_status"]
        signed_at = update_data["offer_response_at"]

        # 1. Fetch record by doc_id (stored in pandadoc_draft_id)
        result = await self.db.execute(
            select(OfferLetterDetails).where(
                OfferLetterDetails.pandadoc_draft_id == doc_id
            )
        )
        offer = result.scalar_one_or_none()

        if not offer:
            print(f"❌ DAO: No offer found for PandaDoc doc_id: {doc_id}")
            return None

        # 2. Update fields
        offer.status = new_status  # "Accepted"
        offer.offer_response_at = signed_at  # datetime from webhook

        # 3. Commit + refresh
        await self.db.commit()
        await self.db.refresh(offer)

        print(f"✅ DAO: Updated offer {offer.user_uuid} successfully.")

        return offer

    async def update_offer_expiration_from_webhook(self, update_data: dict):
        """
        Update offer letter fields when PandaDoc webhook notifies expiration.
        """

        doc_id = update_data["doc_id"]
        new_status = update_data["new_status"]  # "Expired"
        expired_at = update_data["offer_response_at"]  # datetime from webhook

        # 1. Fetch record by doc_id (stored in pandadoc_draft_id)
        result = await self.db.execute(
            select(OfferLetterDetails).where(
                OfferLetterDetails.pandadoc_draft_id == doc_id
            )
        )
        offer = result.scalar_one_or_none()

        if not offer:
            print(f"❌ DAO: No offer found for PandaDoc doc_id (expiration): {doc_id}")
            return None

        # 2. Update fields
        offer.status = new_status  # "Expired"
        offer.offer_response_at = expired_at  # datetime when expiration occurred

        # 3. Commit + refresh
        await self.db.commit()
        await self.db.refresh(offer)

        print(f"🧊 DAO: Marked offer {offer.user_uuid} as Expired successfully.")

        return offer

    async def get_fullname_email_by_docid(self, doc_id: str):
        """
        Fetch candidate full name and email by PandaDoc document ID.
        """
        result = await self.db.execute(
            select(OfferLetterDetails).where(
                OfferLetterDetails.pandadoc_draft_id == doc_id
            )
        )
        offer = result.scalar_one_or_none()

        if not offer:
            return None

        first_name = offer.first_name
        last_name = offer.last_name
        uuid = offer.user_uuid

        return {
            "fullname": f"{first_name} {last_name}".strip(),
            "email": offer.mail,
            "uuid": uuid,
        }

    async def is_email_accepted(self, email: str) -> bool:
        result = await self.db.execute(
            select(OfferLetterDetails).where(OfferLetterDetails.mail == email)
        )
        offer = result.scalar_one_or_none()

        if not offer:
            return False

        return offer.status == "Accepted"

    async def get_offer_by_uuid(self, user_uuid: str):
        """
        Fetch offer letter details by user UUID.
        """
        result = await self.db.execute(
            select(OfferLetterDetails).where(OfferLetterDetails.user_uuid == user_uuid)
        )
        offer = result.scalar_one_or_none()

        return offer
