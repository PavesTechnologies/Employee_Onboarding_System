import dbm
from http.client import HTTPException
from tracemalloc import start
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.models import IdentityType, CountryIdentityMapping, EmployeeIdentityDocument, OfferLetterDetails
from sqlalchemy import select, update, exists, delete

import time
class IdentityDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_identity_types(self):

        stmt = select(
            IdentityType.identity_type_uuid,
            IdentityType.identity_type_name,
            IdentityType.description,
            IdentityType.is_active
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        return [row._mapping for row in rows]


    
    async def get_identity_type_by_uuid(self, uuid):
        start = time.perf_counter()
        result = await self.db.scalar(
            select(IdentityType.identity_type_uuid)
            .where(IdentityType.identity_type_uuid == uuid)
            .limit(1)
        )
        print("⏱ DAO get_identity_type_by_uuid:", time.perf_counter() - start)
        return result

    
    async def get_identity_type_by_name_and_status(self, name, is_active):
        result = await self.db.execute(select(IdentityType).where(IdentityType.identity_type_name == name).where(IdentityType.is_active == is_active))
        return result.scalar_one_or_none()
    
    async def get_identity_type_by_name(self, name):
        result = await self.db.execute(select(IdentityType).where(IdentityType.identity_type_name == name))
        return result.scalar_one_or_none()
    async def get_identity_file_number_by_uuid(self, uuid):
        result = await self.db.execute(select(IdentityType).where(IdentityType.identity_type_uuid == uuid))
        return result.scalar_one_or_none()
    
    async def create_identity_type(self, request_data, uuid):
        identity_type = IdentityType(
            identity_type_uuid = uuid,
            identity_type_name = request_data.identity_type_name,
            description = request_data.description,
            is_active = request_data.is_active
        )
        self.db.add(identity_type)
        await self.db.commit()
        await self.db.refresh(identity_type)
        return identity_type
    async def delete_identity_type(self, uuid):
        result = await self.db.execute(select(IdentityType).where(IdentityType.identity_type_uuid == uuid))
        identity_type = result.scalar_one_or_none()
        await self.db.delete(identity_type)
        await self.db.commit()
        return identity_type
    from sqlalchemy import update, select, exists

    async def update_identity_type(self, uuid, request_data):
        # 1️⃣ duplicate name check (FAST)
        dup_stmt = (
            select(exists().where(
                IdentityType.identity_type_name == request_data.identity_type_name,
                IdentityType.identity_type_uuid != uuid
            ))
        )
        dup = await self.db.execute(dup_stmt)
        if dup.scalar():
            raise HTTPException(status_code=422, detail="Identity Type with this name already exists")

        # 2️⃣ update in one DB call
        stmt = (
            update(IdentityType)
            .where(IdentityType.identity_type_uuid == uuid)
            .values(
                identity_type_name=request_data.identity_type_name,
                description=request_data.description,
                is_active=request_data.is_active
            )
        )

        result = await self.db.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Identity Type Not Found")

        await self.db.commit()
        return True

    # Country Identity Mapping DAO Methods
    async def get_country_identity_mapping(self, country_uuid, identity_type_uuid):
        return await self.db.scalar(
            select(CountryIdentityMapping.mapping_uuid)
            .where(
                CountryIdentityMapping.country_uuid == country_uuid,
                CountryIdentityMapping.identity_type_uuid == identity_type_uuid
            )
            .limit(1)
        )


    
    async def create_country_identity_mapping(self, request_data, uuid):
        start = time.perf_counter()
        country_identity_mapping = CountryIdentityMapping(
            mapping_uuid = uuid,
            country_uuid = request_data.country_uuid,
            identity_type_uuid = request_data.identity_type_uuid,
            is_mandatory = request_data.is_mandatory
        )
        print("DAO CREATE MAPPING OBJECT TIME:", time.perf_counter() - start)
        self.db.add(country_identity_mapping)
        await self.db.commit()
        
        return country_identity_mapping

    async def get_country_identity_mapping_by_uuid(self, uuid):
        start = time.perf_counter()

        mapping = await self.db.scalar(
            select(CountryIdentityMapping)
            .where(CountryIdentityMapping.mapping_uuid == uuid)
            .limit(1)
        )

        print("DAO GET MAPPING BY UUID TIME:", time.perf_counter() - start)
        return mapping

    
    async def get_all_country_identity_mappings(self):
        start = time.perf_counter()
        stmt = select(
            CountryIdentityMapping.mapping_uuid,
            CountryIdentityMapping.country_uuid,
            CountryIdentityMapping.identity_type_uuid,
            CountryIdentityMapping.is_mandatory
        )

        result = await self.db.execute(stmt)
        rows =  result.mappings().all()
        print("TOTAL DAO TIME:", time.perf_counter() - start)
        return rows
    
    async def update_country_identity_mapping(self, uuid, request_data):
        result = await self.db.execute(
            select(CountryIdentityMapping)
            .where(CountryIdentityMapping.mapping_uuid == uuid)
        )

        mapping = result.scalar_one_or_none()

        if not mapping:
            raise HTTPException(
                status_code=404,
                detail="Country Identity Mapping Not Found"
            )

        # ✅ SAFE FIELD UPDATES
        if request_data.country_uuid is not None:
            mapping.country_uuid = request_data.country_uuid

        if request_data.identity_type_uuid is not None:
            mapping.identity_type_uuid = request_data.identity_type_uuid

        if request_data.is_mandatory is not None:
            mapping.is_mandatory = request_data.is_mandatory

        # ❌ mapping.mapping_uuid MUST NEVER be changed

        await self.db.commit()
        await self.db.refresh(mapping)

        return mapping

    
    async def delete_country_identity_mapping(self, uuid):
        stmt = (
            delete(CountryIdentityMapping)
            .where(CountryIdentityMapping.mapping_uuid == uuid)
        )

        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.rowcount > 0

    
    async def get_identities_by_country_uuid(self, country_uuid: str):
        stmt = (
            select(
                CountryIdentityMapping.mapping_uuid,
                IdentityType.identity_type_uuid,
                IdentityType.identity_type_name,
                CountryIdentityMapping.is_mandatory
            )
            .join(
                IdentityType,
                CountryIdentityMapping.identity_type_uuid
                == IdentityType.identity_type_uuid
            )
            .where(
                CountryIdentityMapping.country_uuid == country_uuid,
                CountryIdentityMapping.is_mandatory.is_(True)
            )
        )

        result = await self.db.execute(stmt)
        return result.mappings().all()
    
    async def get_employee_identity_documents_by_mapping_uuid(self, mapping_uuid):
        stmt = (
            select(
                OfferLetterDetails.first_name,
                OfferLetterDetails.last_name,
                EmployeeIdentityDocument.mapping_uuid,
                EmployeeIdentityDocument.user_uuid,
                EmployeeIdentityDocument.document_uuid
            )
            .select_from(CountryIdentityMapping)
            .join(
                EmployeeIdentityDocument,
                EmployeeIdentityDocument.mapping_uuid == CountryIdentityMapping.mapping_uuid
            )
            .join(
                OfferLetterDetails,
                OfferLetterDetails.user_uuid == EmployeeIdentityDocument.user_uuid
            )
            .where(
                CountryIdentityMapping.mapping_uuid == mapping_uuid
            )
            .limit(1)
        )

        result = await self.db.execute(stmt)
        return result.all()

    async def get_employee_identity_document_by_uuid(self, document_uuid):
        result = await self.db.execute(
            select(EmployeeIdentityDocument).where(
                EmployeeIdentityDocument.document_uuid == document_uuid
            )
        )

        return result.scalar_one_or_none()

    async def update_employee_identity_document(self, document_uuid, request_data):
        result = await self.db.execute(
            select(EmployeeIdentityDocument).where(
                EmployeeIdentityDocument.document_uuid == document_uuid
            )
        )

        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Employee Identity Document Not Found"
            )

        document.mapping_uuid = request_data.mapping_uuid
        document.identity_file_number = request_data.identity_file_number
        document.expiry_date = request_data.expiry_date
        document.file_path = request_data.file_path

        await self.db.commit()
        await self.db.refresh(document)

        return document    