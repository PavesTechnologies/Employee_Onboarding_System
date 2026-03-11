from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...DAL.dao.employee_pf_dao import EmployeePfDAO
from ...DAL.dao.offerletter_dao import OfferLetterDAO
from ..utils.uuid_generator import generate_uuid7


class EmployeePfService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = EmployeePfDAO(self.db)
        self.offerdao = OfferLetterDAO(self.db)


    async def get_all_pf_details(self):

        try:

            result = await self.dao.get_all_pf_details()

            if not result:
                raise HTTPException(status_code=200, detail="No PF Details Found")

            return result

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def get_pf_details_by_uuid(self, uuid):

        try:

            result = await self.dao.get_pf_details_by_uuid(uuid)

            if not result:
                raise HTTPException(status_code=200, detail="PF Details Not Found")

            return result

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def create_pf_details(self, request_data):

        try:

            employee = await self.offerdao.get_offer_by_user_uuid(
                request_data.user_uuid
            )

            if not employee:
                raise HTTPException(status_code=404, detail="Employee Not Found")


            pf_uuid = generate_uuid7()

            result = await self.dao.create_pf_details(
                pf_uuid,
                request_data
            )

            return {
                "pf_uuid": pf_uuid
            }

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def update_pf_details(self, uuid, request_data):

        try:

            existing = await self.dao.get_pf_details_by_uuid(uuid)

            if not existing:
                raise HTTPException(status_code=404, detail="PF Details Not Found")

            result = await self.dao.update_pf_details(uuid, request_data)

            return result

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def delete_pf_details(self, uuid):

        try:

            existing = await self.dao.get_pf_details_by_uuid(uuid)

            if not existing:
                raise HTTPException(status_code=404, detail="PF Details Not Found")

            result = await self.dao.delete_pf_details(uuid)

            return result

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))