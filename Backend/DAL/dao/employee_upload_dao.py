from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from typing import Optional
from datetime import date
from ...DAL.models.models import (
    CountryIdentityMapping,
    PersonalDetails,
    Addresses,
    EmployeeIdentityDocument,
    RelationMaster,
)
import time


class EmployeeUploadDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_personal_details(self, request_data, uuid):
        personal_details = PersonalDetails(
            personal_uuid=uuid,
            user_uuid=request_data.user_uuid,
            date_of_birth=request_data.date_of_birth,
            gender=request_data.gender,
            marital_status=request_data.marital_status,
            blood_group=request_data.blood_group,
            nationality_country_uuid=request_data.nationality_country_uuid,
            residence_country_uuid=request_data.residence_country_uuid,
            emergency_contact_name=request_data.emergency_contact_name,
            emergency_contact_phone=request_data.emergency_contact_phone,
            emergency_contact_relation_uuid=request_data.emergency_contact_relation_uuid,
        )
        self.db.add(personal_details)
        await self.db.commit()
        # await self.db.refresh(personal_details)
        return personal_details

    async def create_relation(self, request_data, uuid):
        relation = RelationMaster(
            relation_uuid=uuid, relation_name=request_data.relation_name
        )
        self.db.add(relation)
        await self.db.commit()
        # await self.db.refresh(relation)
        return relation

    async def get_relations(self, db: AsyncSession):
        result = await db.execute(
            select(RelationMaster.relation_uuid, RelationMaster.relation_name)
        )

        relations = result.fetchall()

        return [
            {"relation_uuid": r.relation_uuid, "relation_name": r.relation_name}
            for r in relations
        ]

    async def get_address_by_user_uuid_and_address_type(
        self, user_uuid: str, address_type: str
    ):
        start = time.perf_counter()
        stmt = (
            select(Addresses)
            .where(
                (Addresses.user_uuid == user_uuid)
                & (Addresses.address_type == address_type)
            )
            .limit(1)
        )

        result = await self.db.execute(stmt)
        print(f"⏱ Address query: {time.perf_counter() - start:.4f} sec")
        return result.scalar_one_or_none()

    async def create_address(self, request_data, uuid):
        permanent_address = Addresses(
            address_uuid=uuid,
            user_uuid=request_data.user_uuid,
            address_type=request_data.address_type,
            address_line1=request_data.address_line1,
            address_line2=request_data.address_line2,
            city=request_data.city,
            district_or_ward=request_data.district_or_ward,
            state_or_region=request_data.state_or_region,
            country_uuid=request_data.country_uuid,
            postal_code=request_data.postal_code,
        )
        self.db.add(permanent_address)
        await self.db.commit()
        # await self.db.refresh(permanent_address)
        return permanent_address

    async def create_employee_identity(
        self,
        mapping_uuid: str,
        user_uuid: str,
        identity_file_number: Optional[str],
        expiry_date: Optional[date],
        file_path: str,
        uuid: str,
    ):

        employee_identity = EmployeeIdentityDocument(
            document_uuid=uuid,
            mapping_uuid=mapping_uuid,
            user_uuid=user_uuid,
            identity_file_number=identity_file_number,
            expiry_date=expiry_date,
            file_path=file_path,
            status="uploaded",
        )

        self.db.add(employee_identity)
        await self.db.commit()
        # await self.db.refresh(employee_identity)
        return employee_identity

    async def identity_mapping_exists(self, uuid: str) -> bool:
        start = time.perf_counter()

        result = await self.db.execute(
            select(exists().where(CountryIdentityMapping.mapping_uuid == uuid))
        )

        exists_flag = result.scalar()

        print("DAO MAPPING EXISTS TIME:", time.perf_counter() - start)
        return bool(exists_flag)

    async def identity_exists(self, user_uuid: str, mapping_uuid: str) -> bool:
        result = await self.db.execute(
            select(
                exists().where(
                    (EmployeeIdentityDocument.user_uuid == user_uuid)
                    & (EmployeeIdentityDocument.mapping_uuid == mapping_uuid)
                )
            )
        )
        return bool(result.scalar())

    async def get_employee_identity_by_uuid(self, identity_uuid: str):
        result = await self.db.execute(
            select(EmployeeIdentityDocument).where(
                EmployeeIdentityDocument.document_uuid == identity_uuid
            )
        )
        return result.scalar_one_or_none()

    async def update_employee_identity(
        self,
        identity_uuid: str,
        mapping_uuid: str,
        identity_file_number: str,
        user_uuid: str,
        expiry_date: Optional[date],
        file_path: str,
    ):
        result = await self.db.execute(
            select(EmployeeIdentityDocument).where(
                EmployeeIdentityDocument.document_uuid == identity_uuid
            )
        )

        identity = result.scalar_one_or_none()

        if not identity:
            return None

        identity.mapping_uuid = mapping_uuid
        identity.user_uuid = user_uuid
        identity.identity_file_number = identity_file_number
        identity.expiry_date = expiry_date
        identity.file_path = file_path
        identity.status = "pending"

        await self.db.commit()
        await self.db.refresh(identity)

        return identity  # ⚠️ MUST RETURN

    # async def get_address_by_uuid(self, address_uuid: str):
    #  result = await self.db.execute(
    #     select(Addresses).where(Addresses.address_uuid == address_uuid)
    #  )
    #  return result.scalar_one_or_none()

    async def get_address_by_address_uuid(self, address_uuid: str):
        result = await self.db.execute(
            select(Addresses).where(Addresses.address_uuid == address_uuid)
        )
        return result.scalar_one_or_none()

    async def update_address(self, uuid, request_data):
        result = await self.db.execute(
            select(Addresses).where(Addresses.address_uuid == uuid)
        )
        existing = result.scalar_one_or_none()
        if not existing:
            return None

        existing.address_line1 = request_data.address_line1
        existing.address_line2 = request_data.address_line2
        existing.city = request_data.city
        existing.district_or_ward = request_data.district_or_ward
        existing.state_or_region = request_data.state_or_region
        existing.country_uuid = request_data.country_uuid
        existing.postal_code = request_data.postal_code
        await self.db.commit()
        await self.db.refresh(existing)
        return existing
