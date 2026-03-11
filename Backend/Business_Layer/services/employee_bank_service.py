from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...DAL.dao.employee_bank_dao import EmployeeBankDAO
from ...DAL.dao.offerletter_dao import OfferLetterDAO
from ..utils.uuid_generator import generate_uuid7


class EmployeeBankService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = EmployeeBankDAO(self.db)
        self.offerdao = OfferLetterDAO(self.db)


    async def get_all_bank_details(self):
        try:
            result = await self.dao.get_all_bank_details()

            if not result:
                raise HTTPException(status_code=200, detail="No Bank Details Found")

            return result

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def get_bank_details_by_uuid(self, uuid):
        try:
            result = await self.dao.get_bank_details_by_uuid(uuid)

            if not result:
                raise HTTPException(status_code=200, detail="Bank Details Not Found")

            return result

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def create_bank_details(self, request_data):

        try:

            # Validate employee exists
            employee = await self.offerdao.get_offer_by_user_uuid(
                request_data.user_uuid
            )

            if not employee:
                raise HTTPException(status_code=404, detail="Employee Not Found")


            bank_uuid = generate_uuid7()

            result = await self.dao.create_bank_details(
                bank_uuid,
                request_data
            )

            return {
                "bank_uuid": bank_uuid
            }

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def update_bank_details(self, uuid, request_data):

        try:

            existing = await self.dao.get_bank_details_by_uuid(uuid)

            if not existing:
                raise HTTPException(status_code=404, detail="Bank Details Not Found")

            result = await self.dao.update_bank_details(uuid, request_data)

            return result

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def delete_bank_details(self, uuid):

        try:

            existing = await self.dao.get_bank_details_by_uuid(uuid)

            if not existing:
                raise HTTPException(status_code=404, detail="Bank Details Not Found")

            result = await self.dao.delete_bank_details(uuid)

            return result

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))