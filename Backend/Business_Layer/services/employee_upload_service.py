from datetime import date
from typing import Optional
from Backend.API_Layer.interfaces.employee_details_interfaces import (
    PersonalDetailsRequest,
)
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.dao.master_dao import CountryDAO
from ...DAL.dao.offerletter_dao import OfferLetterDAO
from ...DAL.dao.employee_upload_dao import EmployeeUploadDAO
from ...DAL.dao.identity_dao import IdentityDAO
from ..utils.validation_utils import validate_date_of_birth, validate_blood_group
from ..utils.uuid_generator import generate_uuid7
from ..utils.postal_code_validator import validate_postal_code
from ...DAL.utils.storage_utils import S3StorageService
import time


class EmployeeUploadService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = EmployeeUploadDAO(self.db)
        self.countrydao = CountryDAO(self.db)
        self.offerdao = OfferLetterDAO(self.db)
        self.identitydao = IdentityDAO(self.db)

    async def create_personal_details(self, request_data: PersonalDetailsRequest):

        try:
            validate_blood_group(request_data.blood_group)
            validate_date_of_birth(request_data.date_of_birth)

            offer = await self.offerdao.get_offer_by_uuid(request_data.user_uuid)

            if not offer:
                raise HTTPException(status_code=404, detail="User Not Found")

            nationality = await self.countrydao.country_exists(
                request_data.nationality_country_uuid
            )

            if not nationality:
                raise HTTPException(
                    status_code=404, detail="Nationality Country Not Found"
                )

            residence = await self.countrydao.country_exists(
                request_data.residence_country_uuid
            )

            if not residence:
                raise HTTPException(
                    status_code=404, detail="Residence Country Not Found"
                )

            result = await self.dao.create_personal_details(
                request_data, generate_uuid7()
            )

            return result

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def create_relation(self, request_data):
        try:
            result = await self.dao.create_relation(request_data, generate_uuid7())
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_relations(self, db: AsyncSession):
        try:
            result = await self.dao.get_relations(db)
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def create_address(self, request_data):
        start_total = time.perf_counter()

        try:
            # 🔹 User check timing
            t1 = time.perf_counter()
            existing_user = await self.offerdao.get_offer_by_uuid(
                request_data.user_uuid
            )
            print(f"⏱ User query: {time.perf_counter() - t1:.4f} sec")

            if not existing_user:
                raise HTTPException(status_code=404, detail="User Not Found")

            # 🔹 Country exists timing
            t2 = time.perf_counter()
            country_exists = await self.countrydao.country_exists(
                request_data.country_uuid
            )
            print(f"⏱ Country exists query: {time.perf_counter() - t2:.4f} sec")

            if not country_exists:
                raise HTTPException(status_code=404, detail="Country Not Found")

            # 🔹 Postal validation timing
            t3 = time.perf_counter()
            calling_code = existing_user["country_code"]
            validate_postal_code(calling_code, request_data.postal_code)
            print(f"⏱ Postal validation: {time.perf_counter() - t3:.4f} sec")

            # 🔹 Existing address lookup timing
            t4 = time.perf_counter()
            existing = await self.dao.get_address_by_user_uuid_and_address_type(
                request_data.user_uuid, request_data.address_type
            )
            print(f"⏱ Existing address query: {time.perf_counter() - t4:.4f} sec")

            # 🟢 INSERT timing
            if not existing:
                uuid = generate_uuid7()

                t5 = time.perf_counter()
                result = await self.dao.create_address(request_data, uuid)
                print(f"⏱ Insert + commit: {time.perf_counter() - t5:.4f} sec")

                print(
                    f"🚀 TOTAL SERVICE TIME: {time.perf_counter() - start_total:.4f} sec"
                )
                return result

            # 🔵 UPDATE timing
            t6 = time.perf_counter()
            existing.address_line1 = request_data.address_line1
            existing.address_line2 = request_data.address_line2
            existing.city = request_data.city
            existing.district_or_ward = request_data.district_or_ward
            existing.state_or_region = request_data.state_or_region
            existing.country_uuid = request_data.country_uuid
            existing.postal_code = request_data.postal_code

            await self.db.commit()
            print(f"⏱ Update + commit: {time.perf_counter() - t6:.4f} sec")

            print(f"🚀 TOTAL SERVICE TIME: {time.perf_counter() - start_total:.4f} sec")
            return existing

        except HTTPException:
            raise

        except Exception as e:
            await self.db.rollback()
            print(
                f"❌ Service error after: {time.perf_counter() - start_total:.4f} sec"
            )
            raise HTTPException(status_code=500, detail=str(e))

    async def update_address(self, uuid, request_data):
        try:
            existing = await self.dao.get_address_by_address_uuid(uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Address Not Found")
            existing_user = await self.offerdao.get_offer_by_uuid(
                request_data.user_uuid
            )
            if not existing_user:
                raise HTTPException(status_code=404, detail="User Not Found")
            country_existing = await self.countrydao.get_country_by_uuid(
                request_data.country_uuid
            )
            if not country_existing:
                raise HTTPException(status_code=404, detail="Country Not Found")

            calling_code = country_existing.calling_code
            validate_postal_code(calling_code, request_data.postal_code)
            result = await self.dao.update_address(uuid, request_data)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def create_employee_identity(
        self, mapping_uuid, user_uuid, identity_file_number, expiry_date, file
    ):
        start_total = time.perf_counter()

        try:
            # 🔹 Mapping lookup timing
            t1 = time.perf_counter()
            existing = await self.dao.identity_mapping_exists(mapping_uuid)
            print(f"⏱ Mapping lookup: {time.perf_counter() - t1:.4f} sec")

            if not existing:
                raise HTTPException(status_code=404, detail="Mapping Not Found")

            # 🔹 Identity existence check timing
            t2 = time.perf_counter()
            existing = await self.dao.identity_exists(user_uuid, mapping_uuid)
            print(f"⏱ Identity exists check: {time.perf_counter() - t2:.4f} sec")

            if existing:
                raise HTTPException(
                    status_code=409, detail="Employee identity mapping already found"
                )

            # 🔹 S3 upload timing (usually biggest part)
            t3 = time.perf_counter()
            blob_service = S3StorageService()
            folder = "identity_documents"
            file_path = await blob_service.upload_file(
                file, folder, original_filename=file.filename, employee_uuid=user_uuid
            )
            print(f"⏱ S3 upload: {time.perf_counter() - t3:.4f} sec")

            # 🔹 DB insert timing
            t4 = time.perf_counter()
            uuid = generate_uuid7()
            result = await self.dao.create_employee_identity(
                mapping_uuid,
                user_uuid,
                identity_file_number,
                expiry_date,
                file_path,
                uuid,
            )
            print(f"⏱ Insert + commit: {time.perf_counter() - t4:.4f} sec")

            # 🔹 Total service time
            print(f"🚀 TOTAL SERVICE TIME: {time.perf_counter() - start_total:.4f} sec")

            return result

        except HTTPException:
            raise

        except Exception as e:
            print(f"❌ Failed after: {time.perf_counter() - start_total:.4f} sec")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_employee_identity(
        self,
        identity_uuid: str,
        mapping_uuid: str,
        user_uuid: str,
        identity_file_number: str,
        expiry_date: Optional[date],
        file: Optional[UploadFile],
    ):
        existing = await self.dao.get_employee_identity_by_uuid(identity_uuid)

        if not existing:
            raise HTTPException(status_code=404, detail="Document not found")

        file_path = existing.file_path

        if file:
            blob_service = S3StorageService()
            file_path = await blob_service.upload_file(
                file,
                "identity_documents",
                original_filename=file.filename or "",
                employee_uuid=user_uuid,
            )

        return await self.dao.update_employee_identity(
            identity_uuid,
            mapping_uuid,
            identity_file_number,
            user_uuid,
            expiry_date,
            file_path,
        )
