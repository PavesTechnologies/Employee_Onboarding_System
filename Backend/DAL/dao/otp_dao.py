from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Backend.DAL.models.models import Otptable
from Backend.DAL.models.models import Otptable

from sqlalchemy import select, delete


class OtpResponseDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_or_update_otp(self, email: str, otp: str, expirytime):
        # Remove old OTPs for same email
        await self.db.execute(delete(Otptable).where(Otptable.email == email))

        new_otp = Otptable(email=email, otp=otp, expirytime=expirytime)
        try:
            self.db.add(new_otp)
            await self.db.commit()
            await self.db.refresh(new_otp)
            return True
        except Exception as e:
            await self.db.rollback()
            return False

    async def get_otp_by_email(self, email: str):
        query = select(Otptable).where(Otptable.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def delete_otp(self, otp_record: Otptable):
        try:
            await self.db.delete(otp_record)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            return False
