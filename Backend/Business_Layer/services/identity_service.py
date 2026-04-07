from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.API_Layer.interfaces.identity_interfaces import CountryIdentityDropdownResponse
from ...DAL.dao.identity_dao import IdentityDAO
from ...DAL.dao.master_dao import CountryDAO
from ..utils.uuid_generator import generate_uuid7
import time
class IdentityService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = IdentityDAO(db)
        self.country_dao = CountryDAO(db)
        
    async def get_all_identity_types(self):
        try:
            result = await self.dao.get_all_identity_types()
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_identity_type_by_uuid(self, uuid):
        try:
            result = await self.dao.get_identity_type_by_uuid(uuid)
            if not result:
                raise HTTPException(status_code=200, detail="No Identity Type Found for this employee")
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def create_identity_type(self, request_data):
        try:
            existing = await self.dao.get_identity_type_by_name(request_data.identity_type_name)
            if existing:
                raise HTTPException(status_code=422, detail="Identity Type with this name already exists")
            uuid = generate_uuid7()

            result = await self.dao.create_identity_type(request_data, uuid)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def delete_identity_type(self, uuid):
        try:
            existing = await self.dao.get_identity_type_by_uuid(uuid)
            if not existing:
                raise HTTPException(status_code=404, detail = "Identity Type not Found")
            return await self.dao.delete_identity_type(uuid)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def update_identity_type(self, uuid, request_data):
        await self.dao.update_identity_type(uuid, request_data)
        

        
    # Country Identity Mapping Services
    async def create_country_identity_mapping(self, request_data):
        try:
           
            existing = await self.dao.get_identity_type_by_uuid(request_data.identity_type_uuid)
            if not existing:
                raise HTTPException(status_code=404, detail="Identity Type Not Found")
            
            mapping_existing = await self.dao.get_country_identity_mapping(request_data.country_uuid, request_data.identity_type_uuid)
            if mapping_existing:
                raise HTTPException(status_code=422, detail="Mapping already exists for this country and identity type")
            uuid = generate_uuid7()
            result = await self.dao.create_country_identity_mapping(request_data, uuid)
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def get_all_country_identity_mappings(self):
        try:
            result = await self.dao.get_all_country_identity_mappings()
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def get_country_identity_mapping_by_uuid(self, uuid):
        try:
            result = await self.dao.get_country_identity_mapping_by_uuid(uuid)
            if not result:
                raise HTTPException(status_code=200, detail="No Country Identity Mapping Found")
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def update_country_identity_mapping(self, uuid, request_data):
        try:
            # 🔒 Check mapping exists
            existing_mapping = await self.dao.get_country_identity_mapping_by_uuid(uuid)
            if not existing_mapping:
                raise HTTPException(status_code=404, detail="Country Identity Mapping Not Found")

            # 🔒 Validate country
            existing_country = await self.country_dao.get_country_by_uuid(
                request_data.country_uuid
            )
            if not existing_country:
                raise HTTPException(status_code=404, detail="Country Not Found")

            # 🔒 Validate identity type
            existing_identity = await self.dao.get_identity_type_by_uuid(
                request_data.identity_type_uuid
            )
            if not existing_identity:
                raise HTTPException(status_code=404, detail="Identity Type Not Found")

            return await self.dao.update_country_identity_mapping(uuid, request_data)

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

            
    async def delete_country_identity_mapping(self, uuid):

        employee_existing = await self.dao.get_employee_identity_documents_by_mapping_uuid(uuid)

        if employee_existing:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Cannot delete mapping as it is associated with employee identity documents",
                    "employees": [
                        {
                            "user_uuid": row.user_uuid,
                            "mapping_uuid": row.mapping_uuid,
                            "first_name": row.first_name,
                            "last_name": row.last_name,
                            "document_uuid": row.document_uuid
                        }
                        for row in employee_existing
                    ]
                }
            )

        deleted = await self.dao.delete_country_identity_mapping(uuid)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Country Identity mapping not found"
            )


  
    # async def get_identities_by_country(self, country_uuid: str):
    #     try:
    #         existing_country = await self.country_dao.get_country_by_uuid(country_uuid)
    #         if not existing_country:
    #             raise HTTPException(status_code=404, detail="Country Not Found")
    #         result = await self.dao.get_identities_by_country_uuid(country_uuid)
    #         return result
    #     except HTTPException as he:
    #         raise he
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=str(e))
        
    async def get_identities_by_country(self, country_uuid: str):
        rows = await self.dao.get_identities_by_country_uuid(country_uuid)

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="Country not found or no identities configured"
            )

        return rows
    async def update_employee_identity_document(self, document_uuid, request_data):
        try:
            existing = await self.dao.get_employee_identity_document_by_uuid(
                document_uuid
            )

            if not existing:
                raise HTTPException(
                    status_code=404,
                    detail="Employee Identity Document Not Found"
                )

            return await self.dao.update_employee_identity_document(
                document_uuid,
                request_data
            )

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))