from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.dao.offerletter_dao import OfferLetterDAO
from ...DAL.dao.master_dao import CountryDAO, EducationDAO, ContactDAO
from ...DAL.dao.education_dao import EducationDocDAO
from ..utils.validation_utils import (
    validate_alphabets_only,
    validate_phone_number,
    get_country_name,
)
from ..utils.uuid_generator import generate_uuid7
from ...API_Layer.interfaces.master_interfaces import (
    CreateEducLevelRequest,
    EducLevelDetails,
    UpdateContactRequest,
)
import time


class CountryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = CountryDAO(self.db)

    async def create_country(self, calling_code: str):
        try:
            country_name = get_country_name(calling_code)
            existing = await self.dao.get_country_by_code(calling_code)

            if existing:
                raise ValueError("Country Already Exists")
            uuid = generate_uuid7()
            country = await self.dao.create_country(uuid, calling_code, country_name)
            return uuid
        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_country_uuid(self, country_uuid: str):
        try:
            if not country_uuid:
                raise ValueError("Not Empty Country uuid")
            result = await self.dao.get_country_by_uuid(country_uuid)
            if not result:
                raise ValueError("Not Country Details Found")
            return result
        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def update_country(self, country_uuid: str, is_active: bool):
        updated = await self.dao.update_country(country_uuid, is_active)

        if not updated:
            raise HTTPException(status_code=404, detail="Country does not exist")

        return "Successfully Activated" if is_active else "Successfully Deactivated"

    async def get_all_countries(self):
        try:
            result = await self.dao.get_all_countries()
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


class EducationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = EducationDAO(self.db)
        self.educationdao = EducationDocDAO(self.db)
        self.countrydao = CountryDAO(self.db)

    async def create_education_level(self, request_data: CreateEducLevelRequest):
        try:
            education_name = validate_alphabets_only(request_data.education_name)
            education_name = await self.dao.get_education_level_by_eduname(
                education_name
            )
            uuid = generate_uuid7()
            if education_name:
                raise HTTPException(
                    status_code=404, detail="Education Level Already Exist"
                )
            return await self.dao.create_education_level(request_data, uuid)
        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_all_education_levels(self):
        try:
            result = await self.dao.get_all_education_levels()
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_education_level_by_uuid(self, uuid: str):
        try:
            result = await self.dao.get_education_level_by_uuid(uuid)
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def update_education_level(self, request_data: EducLevelDetails, uuid: str):
        try:
            education_name = validate_alphabets_only(request_data.education_name)
            education_name = await self.dao.get_education_level_by_eduname_and_uuid(
                education_name, uuid
            )
            if education_name:
                raise HTTPException(
                    status_code=404, detail="Education Level Already Exist"
                )
            return await self.dao.update_education_level(request_data, uuid)
        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_education_level(self, uuid: str):
        try:
            result = await self.dao.get_education_level_by_uuid(uuid)
            if not result:
                raise HTTPException(status_code=404, detail="Education Level Not Found")
            return await self.dao.delete_education_level(uuid)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def create_education_country_mapping(
        self, educ_level_uuid, educ_doc_uuid, country_uuid
    ):
        try:
            existing = await self.dao.get_education_level_by_uuid(educ_level_uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Education Level Not Found")
            existing = await self.educationdao.get_education_document_by_uuid(
                educ_doc_uuid
            )
            print("country uuid", country_uuid)
            if not existing:
                raise HTTPException(
                    status_code=404, detail="Education Document Not Found"
                )
            existing = await self.countrydao.get_country_by_uuid(country_uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Country Not Found")
            existing = await self.dao.check_education_country_mapping(
                educ_level_uuid, educ_doc_uuid, country_uuid
            )
            if existing:
                raise HTTPException(status_code=404, detail="Mapping Already Exists")
            uuid = generate_uuid7()
            result = await self.dao.create_education_country_mapping(
                educ_level_uuid, educ_doc_uuid, country_uuid, uuid
            )
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_education_country_mapping(self, mapping_uuid):
        try:
            result = await self.dao.get_education_country_mapping_by_uuid(mapping_uuid)
            if not result:
                raise HTTPException(status_code=404, detail="Mapping Not Found")
            return await self.dao.delete_education_country_mapping(mapping_uuid)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_all_education_country_mapping(self):
        try:
            result = await self.dao.get_all_education_country_mapping()
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


class ContactService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = ContactDAO(self.db)
        self.offerdao = OfferLetterDAO(self.db)
        self.countrydao = CountryDAO(self.db)

    async def create_contact(self, request_data):
        start_total = time.perf_counter()

        try:
            # ================= USER CHECK =================
            t0 = time.perf_counter()
            existing_user = await self.offerdao.get_offer_by_uuid(
                request_data.user_uuid
            )
            print(f"[TIMING] User lookup: {time.perf_counter() - t0:.4f}s")

            if not existing_user:
                raise ValueError("User Not Found")

            # ================= COUNTRY CHECK =================
            t0 = time.perf_counter()
            existing_country = await self.countrydao.get_country_by_uuid(
                request_data.country_uuid
            )
            print(f"[TIMING] Country lookup: {time.perf_counter() - t0:.4f}s")

            if not existing_country:
                raise ValueError("Country Not Found")

            if existing_country.is_active is False:
                raise ValueError("Country is Inactive")

            # ================= PHONE VALIDATION =================
            t0 = time.perf_counter()
            calling_code = existing_country.calling_code
            validate_phone_number(
                calling_code, request_data.contact_number, "contact number"
            )
            validate_phone_number(
                calling_code, request_data.emergency_contact, "emergency contact"
            )
            print(f"[TIMING] Phone validation: {time.perf_counter() - t0:.4f}s")

            # ================= DUPLICATE CHECK =================
            t0 = time.perf_counter()
            existing = await self.dao.get_contact_by_user_uuid_and_country_uuid(
                request_data.user_uuid, request_data.country_uuid
            )
            print(f"[TIMING] Duplicate check: {time.perf_counter() - t0:.4f}s")

            if existing:
                raise ValueError(
                    "Contact with this user_uuid and country_uuid already exists"
                )

            # ================= INSERT =================
            t0 = time.perf_counter()
            uuid = generate_uuid7()
            result = await self.dao.create_contact(request_data, uuid)
            print(f"[TIMING] DB Insert: {time.perf_counter() - t0:.4f}s")

            return result

        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))

        except HTTPException as he:
            raise he

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        finally:
            print(
                f"[TIMING] Total create_contact time: {time.perf_counter() - start_total:.4f}s"
            )

    async def get_all_contacts(self):
        try:
            result = await self.dao.get_all_contacts()
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_contact_by_uuid(self, uuid):
        try:
            result = await self.dao.get_contact_by_uuid(uuid)
            if not result:
                raise ValueError("Contact Not Found")
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_contact(self, uuid):
        try:
            result = await self.dao.get_contact_by_uuid(uuid)
            if not result:
                raise ValueError("Contact Not Found")
            return await self.dao.delete_contact(uuid)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def update_contact(
        self, contact_uuid: str, request_data: UpdateContactRequest
    ):
        # 🔍 Check if contact exists
        contact = await self.dao.get_contact_by_uuid(contact_uuid)

        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        # 🔄 Call DAO update
        updated_contact = await self.dao.update_contact(contact_uuid, request_data)

        return updated_contact
