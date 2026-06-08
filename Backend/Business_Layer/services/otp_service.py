import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import random
from Backend.Business_Layer.utils import email_utils
from Backend.DAL.dao.otp_dao import OtpResponseDAO
from Backend.API_Layer.interfaces.otp_interfaces import OtpResponseStatus
from Backend.DAL.dao.offerresponse_dao import OfferResponseDAO
from Backend.API_Layer.interfaces.otp_interfaces import OtpResponseStatus


class OtpResponseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = OtpResponseDAO(db)
        self.offer = OfferResponseDAO(db)

    async def send_otp_if_allowed(self, email: str) -> OtpResponseStatus:

        print(f"📧 Service: Checking if OTP can be sent to {email}...")
        # 1️⃣ Validate email & offer status
        is_allowed = await self.offer.is_email_accepted(email)

        print(f"📧 Service: is_allowed = {is_allowed}")

        if not is_allowed:
            return OtpResponseStatus(
                status="failed",
                message="OTP cannot be sent. Offer not accepted or invalid email.",
            )

        # 2️⃣ Generate OTP
        otp = "".join(str(random.randint(0, 9)) for _ in range(6))
        expirytime = datetime.utcnow() + timedelta(minutes=5)

        # 3️⃣ Save OTP
        saved = await self.dao.create_or_update_otp(
            email=email, otp=otp, expirytime=expirytime
        )

        if not saved:
            return OtpResponseStatus(
                status="failed", message="Failed to generate OTP. Please try again."
            )

        # 4️⃣ Send OTP email
        email_utils.send_otp_email(to_email=email, otp=otp)

        return OtpResponseStatus(
            status="success", message="OTP sent successfully to your email."
        )

    async def verify_otp(self, email: str, otp: str) -> OtpResponseStatus:
        otp_record = await self.dao.get_otp_by_email(email)

        if not otp_record:
            return OtpResponseStatus(status="FAILED", message="OTP not found")

        try:
            if datetime.utcnow() > otp_record.expirytime:
                return OtpResponseStatus(status="FAILED", message="OTP expired")

            if otp_record.otp != otp:
                return OtpResponseStatus(status="FAILED", message="Incorrect OTP")

            return OtpResponseStatus(
                status="SUCCESS", message="OTP verified successfully"
            )

        finally:
            await self.dao.delete_otp(otp_record)
