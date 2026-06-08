from sqlalchemy.ext.asyncio import AsyncSession
from Backend.DAL.models.models import OnboardingLinks
from sqlalchemy import select
from Backend.Business_Layer.utils.email_token_utils import hash_token


class TokenVerificationDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_valid_link_by_token(self, raw_token: str) -> OnboardingLinks:
        token_hash = hash_token(raw_token)
        stmt = select(OnboardingLinks).where(OnboardingLinks.token_hash == token_hash)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_uuid_by_token(self, raw_token: str):
        token_hash = hash_token(raw_token)
        stmt = select(OnboardingLinks.user_uuid).where(
            OnboardingLinks.token_hash == token_hash
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
