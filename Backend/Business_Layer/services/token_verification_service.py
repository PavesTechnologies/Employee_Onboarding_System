from sqlalchemy.ext.asyncio import AsyncSession
from Backend.DAL.dao.token_verification_dao import TokenVerificationDAO
from Backend.API_Layer.interfaces.token_verification_interfaces import TokenVerificationRequest, TokenVerificationResponse

class OnboardingVerifyLinkService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = TokenVerificationDAO(self.db)
    async def verify_token(self, request: TokenVerificationRequest) -> TokenVerificationResponse:
        try:
            print("📌 Business Layer: Verifying token")

            # ----------------------------
            # 1️⃣ Query DAO for valid link
            # ----------------------------
            valid_link = await self.dao.get_valid_link_by_token(request.raw_token)

            # ----------------------------
            # 2️⃣ Prepare response
            if not valid_link:
                raise ValueError("Invalid or expired token")

            return valid_link.user_uuid
        except Exception as e:
            raise ValueError(f"Error verifying token: {str(e)}")
        
        
    
    async def get_user_uuid_by_token(self, raw_token):
        try:
            return await self.dao.get_user_uuid_by_token(raw_token)
        except Exception as e:
            raise ValueError(f"Error retrieving user UUID: {str(e)}")
        