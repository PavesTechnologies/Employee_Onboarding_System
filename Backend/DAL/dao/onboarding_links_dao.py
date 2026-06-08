from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from sqlalchemy import select
from Backend.Business_Layer.utils.email_token_utils import (
    generate_mixed_month_time_token,
    hash_token,
)
from Backend.DAL.models.models import OnboardingLinks


class OnboardingLinkDAO:
    def __init__(self, db: AsyncSession):
        self.db = db  # Store the session for transaction management

    async def get_or_create_onboarding_link(
        self,
        user_uuid: str,
        email: str,
        expires_in_hours: int = 24,
    ) -> str:
        """
        If a valid token exists for the user → regenerate token safely.
        If no token or expired → create new token.
        Returns RAW token (only time raw token is available).
        """

        now = datetime.utcnow()

        stmt = select(OnboardingLinks).where(
            OnboardingLinks.user_uuid == user_uuid,
            OnboardingLinks.expires_at > now,
        )

        result = await self.db.execute(stmt)
        existing_link = result.scalar_one_or_none()

        raw_token = generate_mixed_month_time_token()
        token_hash = hash_token(raw_token)
        expires_at = now + timedelta(hours=expires_in_hours)

        try:
            if existing_link:
                # Token exists → rotate token
                existing_link.token_hash = token_hash
                existing_link.expires_at = expires_at
            else:
                # No token → create new
                new_link = OnboardingLinks(
                    user_uuid=user_uuid,
                    email=email,
                    token_hash=token_hash,
                    expires_at=expires_at,
                )
                self.db.add(new_link)

            await self.db.commit()
            return raw_token

        except IntegrityError:
            await self.db.rollback()
            raise
