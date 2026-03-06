# Backend/DAL/dao/master_dao.py

import uuid
from Backend.DAL.utils.database import AsyncSessionLocal
from sqlalchemy import select , exists
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.models.models import Countries, EducationLevel, CountryEducationDocumentMapping, Contacts
from ...API_Layer.interfaces.master_interfaces import CreateEducLevelRequest, EducLevelDetails, UpdateContactRequest
import time

class CountryDAO:
    def __init__(self, db: AsyncSession):
        self.db = db  # Store the session for transaction management
    
    async def get_country_by_code(self, code : str):
        result = await self.db.execute(
            select(Countries).where(Countries.calling_code == code)
        )

        return result.scalar_one_or_none()
    async def create_country(self, uuid: str, calling_code: str, country_name: str):
        new_country = Countries(
            country_uuid = uuid,
            country_name = country_name,
            calling_code = calling_code
        )
        self.db.add(new_country)
        await self.db.commit()
        await self.db.refresh(new_country)
        return new_country
    async def country_exists(self, country_uuid: str) -> bool:
        result = await self.db.execute(
            select(exists().where(Countries.country_uuid == country_uuid))
        )
        return result.scalar()
    
    async def get_country_by_uuid(self, country_uuid: str):
        stmt = select(
            exists().where(Countries.country_uuid == country_uuid)
        )
        result = await self.db.execute(stmt)
        return result.scalar()
    
    
    async def update_country(self, country_uuid: str, is_active: bool):
        result = await self.db.execute(
            select(Countries).where(Countries.country_uuid == country_uuid)
        )
        
        country = result.scalar_one_or_none()
        if country is None:
            return None
        
        country.is_active = 1 if is_active else 0

        await self.db.commit()
        await self.db.refresh(country)

        return country
    async def get_all_countries(self):
        stmt = (
            select(
                Countries.country_uuid,
                Countries.calling_code,
                Countries.country_name,
                Countries.is_active
            )
            .where(Countries.is_active)   #  added filter
            .order_by(Countries.country_name)
        )

        result = await self.db.execute(stmt)

        return [
            {
                "country_uuid": r.country_uuid,
                "calling_code": r.calling_code,
                "country_name": r.country_name,
                "is_active": r.is_active,
            }
            for r in result.all()
        ]

class EducationDAO:
    def __init__(self, db: AsyncSession):
        self.db = db  # Store the session for transaction management
    async def get_education_level_by_eduname(self, education_name):
        result = await self.db.execute(
            select(EducationLevel).where(EducationLevel.education_name == education_name)
        )
        
        return result.scalar_one_or_none()
    async def create_education_level(self, request_data: CreateEducLevelRequest, uuid: str):
        new_edu_level = EducationLevel(
            education_uuid = uuid,
            education_name = request_data.education_name,
            description = request_data.description
        )
        self.db.add(new_edu_level)
        await self.db.commit()
        await self.db.refresh(new_edu_level)
        return new_edu_level

    async def get_all_education_levels(self):
        start = time.perf_counter()

        stmt = select(
            EducationLevel.education_uuid,
            EducationLevel.education_name,
            EducationLevel.description,
            EducationLevel.is_active
        )

        t1 = time.perf_counter()
        result = await self.db.execute(stmt)
        print("⏱ DB execute:", time.perf_counter() - t1)

        t2 = time.perf_counter()
        rows = result.all()
        print("⏱ Result processing:", time.perf_counter() - t2)

        print("⏱ DAO total:", time.perf_counter() - start)

        return [row._mapping for row in rows]

    
    async def get_education_level_by_uuid(self, uuid: str):
        t = time.time()
        res = await self.db.execute(
            select(EducationLevel).where(EducationLevel.education_uuid == uuid)
        )
        print("DB:", round(time.time() - t, 3))
        return res.scalar_one_or_none()


    
    async def get_education_level_by_eduname_and_uuid(self, education_name: str, education_uuid: str):
        result = await self.db.execute(select(EducationLevel).where(EducationLevel.education_name == education_name).where(EducationLevel.education_uuid != education_uuid))
        
        return result.scalar_one_or_none()

    async def update_education_level(self, request_data: EducLevelDetails, uuid: str):
        result = await self.db.execute(
            select(EducationLevel).where(EducationLevel.education_uuid == uuid)
        )
        
        edu_level = result.scalar_one_or_none()
        if edu_level is None:
            return None
        
        edu_level.education_name = request_data.education_name
        edu_level.description = request_data.description
        edu_level.is_active = request_data.is_active

        await self.db.commit()
        await self.db.refresh(edu_level)

        return edu_level
    
    async def delete_education_level(self, uuid: str):
        result = await self.db.execute(select(EducationLevel).where(EducationLevel.education_uuid == uuid))
        edu_level = result.scalar_one_or_none()
        if edu_level is None:
            return None
        await self.db.delete(edu_level)
        await self.db.commit()
        return edu_level
    async def create_education_country_mapping(self, educ_level_uuid, educ_doc_uuid, country_uuid, uuid):
        new_edu_country_mapping = CountryEducationDocumentMapping(
            mapping_uuid = uuid,
            education_uuid = educ_level_uuid,
            education_document_uuid = educ_doc_uuid,
            country_uuid = country_uuid
        )
        self.db.add(new_edu_country_mapping)
        await self.db.commit()
        await self.db.refresh(new_edu_country_mapping)
        return new_edu_country_mapping
    
    async def check_education_country_mapping(self, educ_level_uuid, educ_doc_uuid, country_uuid):
        result = await self.db.execute(select(CountryEducationDocumentMapping).where(
            CountryEducationDocumentMapping.education_document_uuid == educ_doc_uuid).where(
            CountryEducationDocumentMapping.country_uuid == country_uuid).where(
                CountryEducationDocumentMapping.education_uuid == educ_level_uuid))
        
        return result.scalar_one_or_none()
    
    async def get_education_country_mapping_by_uuid(self, mappng_uuid):
        result = await self.db.execute(select(CountryEducationDocumentMapping).where(CountryEducationDocumentMapping.mapping_uuid == mappng_uuid))
        return result.scalar_one_or_none()
    async def delete_education_country_mapping(self, mappng_uuid):
        result = await self.db.execute(select(CountryEducationDocumentMapping).where(CountryEducationDocumentMapping.mapping_uuid == mappng_uuid))
        edu_country_mapping = result.scalar_one_or_none()
        if edu_country_mapping is None:
            return None
        await self.db.delete(edu_country_mapping)
        await self.db.commit()
        return edu_country_mapping
    async def get_all_education_country_mapping(self):
        result = await self.db.execute(select(CountryEducationDocumentMapping))
        return result.scalars().all()

class ContactDAO:
    def __init__(self, db: AsyncSession):
        self.db = db  # Store the session for transaction management

    async def create_contact(self, request_data, uuid):
        new_contact = Contacts(
            contact_uuid = uuid,
            user_uuid = request_data.user_uuid,
            country_uuid = request_data.country_uuid,
            contact_number = request_data.contact_number,
            emergency_contact = request_data.emergency_contact
        )
        self.db.add(new_contact)
        await self.db.commit()
        # await self.db.refresh(new_contact)
        return new_contact
    async def get_contact_by_user_uuid_and_country_uuid(self, user_uuid, country_uuid):
        result = await self.db.execute(select(Contacts).where(Contacts.user_uuid == user_uuid).where(Contacts.country_uuid == country_uuid))
        return result.scalar_one_or_none()
    async def get_all_contacts(self):
        result = await self.db.execute(select(Contacts))
        return result.scalars().all()
    async def get_contact_by_uuid(self, uuid):
        result = await self.db.execute(select(Contacts).where(Contacts.contact_uuid == uuid))
        return result.scalar_one_or_none()
    async def delete_contact(self, uuid):
        result = await self.db.execute(select(Contacts).where(Contacts.contact_uuid == uuid))
        contact = result.scalar_one_or_none()
        if contact is None:
            return None
        await self.db.delete(contact)
        await self.db.commit()
        return contact
    async def update_contact(
        self,
        contact_uuid: str,
        request_data: UpdateContactRequest
    ):
        result = await self.db.execute(
            select(Contacts).where(Contacts.contact_uuid == contact_uuid)
        )
        contact = result.scalar_one_or_none()

        if not contact:
            return None

        # 🔄 Update correct fields
        contact.country_uuid = request_data.country_uuid
        contact.contact_number = request_data.contact_number
        contact.emergency_contact = request_data.emergency_contact
        contact.is_active = request_data.is_active

        await self.db.commit()
        await self.db.refresh(contact)

        return contact
            
