from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.models.models import BackgroundCheck, BackgroundCheckDocument


class BackgroundCheckDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_checks_by_user_uuid(self, user_uuid: str):
        result = await self.db.execute(
            select(BackgroundCheck)
            .where(BackgroundCheck.user_uuid == user_uuid)
            .order_by(BackgroundCheck.created_at.asc())
        )
        return result.scalars().all()

    async def get_check_by_uuid(self, check_uuid: str):
        result = await self.db.execute(
            select(BackgroundCheck).where(BackgroundCheck.check_uuid == check_uuid)
        )
        return result.scalar_one_or_none()

    async def get_check_by_user_and_check_type(self, user_uuid: str, check_type: str):
        result = await self.db.execute(
            select(BackgroundCheck).where(
                BackgroundCheck.user_uuid == user_uuid,
                BackgroundCheck.check_type == check_type,
            )
        )
        return result.scalar_one_or_none()

    async def get_checks_by_uuids(self, check_ids: list[str]):
        result = await self.db.execute(
            select(BackgroundCheck).where(BackgroundCheck.check_uuid.in_(check_ids))
        )
        return result.scalars().all()

    async def create_check(self, check: BackgroundCheck):
        self.db.add(check)
        await self.db.flush()
        await self.db.refresh(check)
        return check

    async def update_check(self, check: BackgroundCheck):
        await self.db.flush()
        await self.db.refresh(check)
        return check

    async def delete_check(self, check: BackgroundCheck):
        await self.db.delete(check)
        await self.db.flush()

    async def get_documents_by_user_uuid(self, user_uuid: str):
        result = await self.db.execute(
            select(BackgroundCheckDocument)
            .where(BackgroundCheckDocument.user_uuid == user_uuid)
            .order_by(BackgroundCheckDocument.uploaded_at.desc())
        )
        return result.scalars().all()

    async def get_document_by_id(self, document_id: str):
        result = await self.db.execute(
            select(BackgroundCheckDocument).where(
                BackgroundCheckDocument.document_id == document_id
            )
        )
        return result.scalar_one_or_none()

    async def get_document_by_file_path(self, file_path: str):
        result = await self.db.execute(
            select(BackgroundCheckDocument).where(
                BackgroundCheckDocument.file_path == file_path
            )
        )
        return result.scalar_one_or_none()

    async def create_document(self, document: BackgroundCheckDocument):
        self.db.add(document)
        await self.db.flush()
        await self.db.refresh(document)
        return document

    async def delete_document(self, document: BackgroundCheckDocument):
        await self.db.delete(document)
        await self.db.flush()
