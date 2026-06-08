# Backend/DAL/dao/auditlogs_dao.py
from ..models.models import AuditTrail
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime
import json


class AuditTrails:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_audit_log(
        self,
        entity_name: str,
        entity_id: str,
        operation: str,
        user_id: str,
        old_data,
        new_data,
        ip_address: str,
        host: str,
        endpoint: str,
    ):
        """Create audit log entry"""

        # Serialize data to JSON if it's a dict
        old_data_json = json.dumps(old_data) if isinstance(old_data, dict) else old_data
        new_data_json = json.dumps(new_data) if isinstance(new_data, dict) else new_data

        audit_log = AuditTrail(
            audit_uuid=str(uuid.uuid4()),
            entity_name=entity_name,
            entity_id=str(entity_id),
            operation=operation,
            user_id=str(user_id),
            old_data=old_data_json,
            new_data=new_data_json,
            ip_address=ip_address,
            host=host,
            endpoint=endpoint,
            created_at=datetime.utcnow(),
        )

        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        return audit_log

    async def get_audit_logs(
        self,
        entity_name: str | None = None,
        entity_id: str | None = None,
        user_id: str | None = None,
        limit: int = 100,
    ):
        """Query audit logs with filters"""
        from sqlalchemy import select

        query = select(AuditTrail)

        if entity_name:
            query = query.where(AuditTrail.entity_name == entity_name)
        if entity_id:
            query = query.where(AuditTrail.entity_id == entity_id)
        if user_id:
            query = query.where(AuditTrail.user_id == user_id)

        query = query.order_by(AuditTrail.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()
