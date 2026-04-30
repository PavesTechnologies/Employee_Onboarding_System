from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.dao.employee_details_dao import EmployeeDetailsDAO, AddressDAO, EmployeeIdentityDAO, EmployeeSocialLinkDAO, EmployeeAboutDAO
from ...DAL.dao.master_dao import CountryDAO
from ...DAL.dao.offerletter_dao import OfferLetterDAO
from ...DAL.dao.identity_dao import IdentityDAO
from ..utils.validation_utils import validate_date_of_birth, validate_blood_group
from ..utils.uuid_generator import generate_uuid7
from ..utils.postal_code_validator import validate_postal_code
from ...DAL.utils.storage_utils import S3StorageService
import time

from time import perf_counter
class EmployeeDetailsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = EmployeeDetailsDAO(self.db)
        self.countrydao = CountryDAO(self.db)
        self.offerdao = OfferLetterDAO(self.db)
    
    async def get_all_personal_details(self):
            try:
                result = await self.dao.get_all_personal_details()
                return result
            except HTTPException as he:
                raise he
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    
    async def get_personal_details_by_user_uuid(self, uuid):
        try:
            result = await self.dao.get_personal_details_by_uuid(uuid)
            if not result:
                raise HTTPException(status_code=200, detail="No Personal Details Found for this Employee")
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    

    

    async def update_personal_details(self, uuid: str, request_data):
        try:
            api_start = perf_counter()

            # 1️⃣ Get personal record
            start = perf_counter()
            personal = await self.dao.get_personal_details_by_uuid(uuid)
            print("Time taken to get personal details:", perf_counter() - start)

            if not personal:
                raise HTTPException(status_code=404, detail="Personal Details Not Found")

            # 2️⃣ Validate fields
            start = perf_counter()
            validate_blood_group(request_data.blood_group)
            validate_date_of_birth(request_data.date_of_birth)
            print("Validation time:", perf_counter() - start)

            # 3️⃣ Validate nationality country
            start = perf_counter()
            nationality = await self.countrydao.get_country_by_uuid(
                request_data.nationality_country_uuid
            )
            print("Nationality check time:", perf_counter() - start)

            if not nationality:
                raise ValueError("Nationality Country Not Found")

            # 4️⃣ Validate residence country
            start = perf_counter()
            residence = await self.countrydao.get_country_by_uuid(
                request_data.residence_country_uuid
            )
            print("Residence check time:", perf_counter() - start)

            if not residence:
                raise ValueError("Residence Country Not Found")

            # 5️⃣ Update personal details
            start = perf_counter()
            result = await self.dao.update_personal_details(uuid, request_data)
            print("Update query time:", perf_counter() - start)

            if not result:
                raise HTTPException(status_code=404, detail="Personal Details Not Found")

            print("Total API time:", perf_counter() - api_start)

            return result

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def delete_personal_details(self, uuid):
        try:
            existing = await self.dao.get_personal_details_by_uuid(uuid)
            if not existing:
                raise HTTPException(status_code = 404, detail= "Personal Details Not Found")
            result = await self.dao.delete_personal_details(uuid)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Addresses Service
class AddressService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = AddressDAO(self.db)
        self.countrydao = CountryDAO(self.db)
        self.offerdao = OfferLetterDAO(self.db)
    
    async def get_all_addresses(self):
        try:
            result = await self.dao.get_all_addresses()
            if not result:
                raise HTTPException(status_code=200, detail="No Addresses Found")
    
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def get_address_by_address_uuid(self, uuid):
        try:
            result = await self.dao.get_address_by_address_uuid(uuid)
            if not result:
                raise HTTPException(status_code=200, detail="No Address Found for this User")
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
          
    async def update_address(self, uuid, request_data):
        try:
            existing = await self.dao.get_address_by_address_uuid(uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Address Not Found")
            result = await self.dao.update_address(uuid, request_data)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

            
    async def delete_address(self, uuid):
        try:
            existing = await self.dao.get_address_by_address_uuid(uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Address Not Found")
            result = await self.dao.delete_address(uuid)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
class EmployeeIdentityService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.identitydao = IdentityDAO(self.db)
        self.dao = EmployeeIdentityDAO(self.db)

    async def delete_employee_identity(self, document_uuid):
        try:
            existing = await self.dao.get_employee_identity_by_document_uuid(document_uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Employee Identity Document Not Found")
            result = await self.dao.delete_employee_identity(document_uuid)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class EmployeeSocialLinkService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = EmployeeSocialLinkDAO(self.db)

    async def get_social_links(self, user_uuid):
        return await self.dao.get_social_links(user_uuid)

    async def create_social_link(self, user_uuid, request_data):
        social_link_uuid = generate_uuid7()
        return await self.dao.create_social_link(
            social_link_uuid,
            user_uuid,
            request_data
        )

    async def update_social_link(self, social_link_uuid, request_data):
        existing = await self.dao.get_social_link_by_uuid(social_link_uuid)

        if not existing:
            raise HTTPException(status_code=404, detail="Social Link Not Found")

        return await self.dao.update_social_link(
            social_link_uuid,
            request_data
        )

    async def delete_social_link(self, social_link_uuid):
        existing = await self.dao.get_social_link_by_uuid(social_link_uuid)

        if not existing:
            raise HTTPException(status_code=404, detail="Social Link Not Found")

        return await self.dao.delete_social_link(social_link_uuid)
    
class EmployeeAboutService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = EmployeeAboutDAO(self.db)

    async def get_employee_about(self, employee_uuid):
        result = await self.dao.get_employee_about(employee_uuid)

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Employee About Details Not Found"
            )

        return result

    async def save_employee_about(self, employee_uuid, request_data):
        existing = await self.dao.get_employee_about(employee_uuid)

        if existing:
            return await self.dao.update_employee_about(
                employee_uuid,
                request_data
            )

        employee_about_uuid = generate_uuid7()

        return await self.dao.create_employee_about(
            employee_about_uuid,
            employee_uuid,
            request_data
        )
    
    async def delete_employee_about(self, employee_uuid):
        existing = await self.dao.get_employee_about(employee_uuid)

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Employee About Details Not Found"
            )

        return await self.dao.delete_employee_about(employee_uuid)
    