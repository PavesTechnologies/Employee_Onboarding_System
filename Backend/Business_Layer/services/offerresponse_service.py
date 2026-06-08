from datetime import datetime
from ...API_Layer.interfaces.offerresponse_interface import (
    PandaDocWebhookRequest,
    PandaDocWebhookResponse,
    PandaDocExpirationData,
)
from ...DAL.dao.offerresponse_dao import OfferResponseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from ...Business_Layer.utils import email_utils
from ...DAL.dao.onboarding_links_dao import OnboardingLinkDAO
from ...config.env_loader import get_env_var

ONBOARDING_LINK_BASE_URL = get_env_var("ONBOARDING_LINK_BASE_URL")


class OfferResponseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = OfferResponseDAO(self.db)
        self.onboarding_links_dao = OnboardingLinkDAO(self.db)

    async def process_offer_acceptance_webhook(self, payload: PandaDocWebhookRequest):
        """
        Business logic:
        - Validate event
        - Extract PandaDoc document ID
        - Convert timestamps
        - Prepare update payload
        - Send to DAO layer
        """

        print("📌 Business Layer: Processing webhook")

        # ----------------------------
        # 1️⃣ Validate document completion
        # ----------------------------
        if payload.data.status != "document.completed":
            print(f"⚠ Ignoring webhook: status={payload.data.status}")
            return PandaDocWebhookResponse(status="ignored")

        # ----------------------------
        # 2️⃣ Extract PandaDoc document ID
        # ----------------------------
        doc_id = payload.data.id
        print(f"➡ Document ID (doc_id): {doc_id}")

        # ----------------------------
        # 3️⃣ Extract & convert timestamp
        # ----------------------------
        signing_timestamp_raw = payload.data.action_date
        signing_timestamp = None

        if signing_timestamp_raw:
            try:
                signing_timestamp = datetime.fromisoformat(
                    signing_timestamp_raw.replace("Z", "+00:00")
                )
            except:
                signing_timestamp = datetime.utcnow()

        print(f"➡ Signing Timestamp: {signing_timestamp}")

        # ----------------------------
        # 4️⃣ Prepare update data for DAO
        # ----------------------------
        update_data = {
            "doc_id": doc_id,
            "new_status": "Accepted",
            "offer_response_at": signing_timestamp,
        }

        print("📦 Prepared update data:", update_data)

        # ----------------------------
        # 5️⃣ Call DAO using constructor-injected DB
        # ----------------------------
        result = await self.dao.update_offer_acceptance_from_webhook(update_data)
        if result:
            userdetails = await self.dao.get_fullname_email_by_docid(
                update_data["doc_id"]
            )
            print("User details fetched:", userdetails)

            raw_token = await self.onboarding_links_dao.get_or_create_onboarding_link(
                user_uuid=userdetails["uuid"],
                email=userdetails["email"],
                expires_in_hours=24,
            )
            print("Onboarding link created with token:", raw_token)

            onboarding_url = f"{ONBOARDING_LINK_BASE_URL}?token={raw_token}"

            email_utils.send_offer_accepted_email(
                to_email=userdetails["email"],
                name=userdetails["fullname"],
                onboarding_url=onboarding_url,
            )
        print("✅ Business Layer: Update request sent to DAO")

        # ----------------------------
        # 6️⃣ Return response to PandaDoc
        # ----------------------------
        return PandaDocWebhookResponse(status="ok")

    async def process_offer_expiration_webhook(self, payload: PandaDocExpirationData):
        """
        Business logic for offer expiration:
        - Validate event
        - Extract PandaDoc document ID
        - Convert expiration timestamp
        - Prepare update payload
        - Send to DAO layer
        """

        print("📌 Business Layer: Processing EXPIRATION webhook")

        # ----------------------------
        # 1️⃣ Validate document expiration
        # ----------------------------
        if payload.status != "document.voided":
            print(f"⚠ Ignoring webhook (not expiration): status={payload.status}")
            return PandaDocWebhookResponse(status="ignored")

        # ----------------------------
        # 2️⃣ Extract PandaDoc document ID
        # ----------------------------
        doc_id = payload.id
        print(f"➡ Document ID (doc_id): {doc_id}")

        # ----------------------------
        # 3️⃣ Extract & convert expiration timestamp
        # ----------------------------
        expiration_timestamp_raw = payload.expiration_date
        expiration_timestamp = None

        if expiration_timestamp_raw:
            try:
                expiration_timestamp = datetime.fromisoformat(
                    expiration_timestamp_raw.replace("Z", "+00:00")
                )
            except:
                expiration_timestamp = datetime.utcnow()

        print(f"➡ Expiration Timestamp: {expiration_timestamp}")

        # ----------------------------
        # 4️⃣ Prepare update data for DAO
        # ----------------------------
        update_data = {
            "doc_id": doc_id,
            "new_status": "Expired",
            "offer_response_at": expiration_timestamp,
        }

        print("📦 Prepared expiration update data:", update_data)

        # ----------------------------
        # 5️⃣ Call DAO using constructor-injected DB
        # ----------------------------
        await self.dao.update_offer_expiration_from_webhook(update_data)

        print("🧊 Business Layer: Expiration update sent to DAO")

        # ----------------------------
        # 6️⃣ Return response to PandaDoc
        # ----------------------------
        return PandaDocWebhookResponse(status="ok")
