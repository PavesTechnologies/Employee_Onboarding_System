from ...DAL.dao.offerresponse_dao import OfferResponseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from ...Business_Layer.utils import email_utils
from ...DAL.dao.onboarding_links_dao import OnboardingLinkDAO
from ...config.env_loader import get_env_var
from datetime import datetime
from ...API_Layer.interfaces.offerresponse_interface import PandaDocWebhookResponse

ONBOARDING_LINK_BASE_URL = get_env_var("ONBOARDING_LINK_BASE_URL")


class DocuSignWebhookService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = OfferResponseDAO(self.db)
        self.onboarding_links_dao = OnboardingLinkDAO(self.db)

    async def process_offer_acceptance_webhook_docusign(self, payload: dict):

        print("📌 Service: Processing DocuSign webhook")

        # ----------------------------
        # 1️⃣ Extract core data
        # ----------------------------
        event = payload.get("event", "").lower()
        data = payload.get("data", {})

        envelope_id = data.get("envelopeId")
        envelope_summary = data.get("envelopeSummary", {})
        status = envelope_summary.get("status", "").lower()

        if not envelope_id or not status:
            print("⚠️ Missing envelopeId or status")
            return PandaDocWebhookResponse(status="ignored")

        print(f"➡ Envelope ID: {envelope_id}")
        print(f"➡ Event: {event}, Status: {status}")

        # ----------------------------
        # 2️⃣ Validate completion / signing
        # ----------------------------
        valid_events = {"envelope-completed", "envelope-signed"}
        valid_statuses = {"completed", "signed"}

        if event not in valid_events or status not in valid_statuses:
            print(f"ℹ️ Ignoring webhook: event={event}, status={status}")
            return PandaDocWebhookResponse(status="ignored")

        print(f"✅ Envelope accepted: {envelope_id}")

        # ----------------------------
        # 3️⃣ Extract & convert timestamp
        # ----------------------------
        signing_timestamp_raw = envelope_summary.get(
            "completedDateTime"
        ) or envelope_summary.get("statusChangedDateTime")

        if signing_timestamp_raw:
            try:
                signing_timestamp = datetime.fromisoformat(
                    signing_timestamp_raw.replace("Z", "+00:00")
                )
            except Exception:
                signing_timestamp = datetime.utcnow()
        else:
            signing_timestamp = datetime.utcnow()

        print(f"➡ Signing Timestamp: {signing_timestamp}")

        # ----------------------------
        # 4️⃣ Prepare update data (UNCHANGED CONTRACT)
        # ----------------------------
        update_data = {
            "doc_id": envelope_id,  # envelopeId replaces PandaDoc doc_id
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
