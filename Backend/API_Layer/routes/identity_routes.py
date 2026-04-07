import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.utils.dependencies import get_db
from ..interfaces.identity_interfaces import(CountryIdentityDropdownResponse, IdentityCreateRequest, IdentityResponse, IdentityDetails,
                                             CountryIdentityMappingDetails, CountryIdentityMappingRequest, CountryIdentityMappingResponse, EmployeeIdentityDocumentUpdateRequest, EmployeeIdentityDocumentUpdateResponse
                                             )
from ...Business_Layer.services.identity_service import IdentityService
from ..utils.role_based import require_roles

router = APIRouter()

@router.get("", response_model=list[IdentityDetails])
async def get_all_identity_types(db: AsyncSession = Depends(get_db)):
    try:
        service = IdentityService(db)
        result = await service.get_all_identity_types()
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{uuid}", response_model = IdentityDetails)
async def get_identity_type_by_uuid(uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        identity_service = IdentityService(db)
        result = await identity_service.get_identity_type_by_uuid(uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("", response_model = IdentityResponse)
async def create_identity_type(request_data: IdentityCreateRequest, db: AsyncSession = Depends(get_db)):
    try:
        identity_service = IdentityService(db)
        result = await identity_service.create_identity_type(request_data)
        return IdentityResponse(
            identity_type_uuid = result.identity_type_uuid,
            message = "Identity Type Created Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{uuid}", response_model = IdentityResponse)
async def delete_identity_type(uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        identity_service = IdentityService(db)
        await identity_service.delete_identity_type(uuid)
        return IdentityResponse(
            identity_type_uuid = uuid,
            message = "Identity Type Deleted Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{uuid}", response_model = IdentityResponse)
async def update_identity_type(uuid: str, request_data: IdentityCreateRequest, db: AsyncSession = Depends(get_db)):
    try:
        identity_service = IdentityService(db)
        await identity_service.update_identity_type(uuid, request_data)
        return IdentityResponse(
            identity_type_uuid = uuid,
            identity_type_name = request_data.identity_type_name,
            message = "Identity Type Updated Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
### Country Identity Mapping Routes ###

@router.post("/country-mapping", response_model = CountryIdentityMappingResponse)
async def create_country_identity_mapping(request_data: CountryIdentityMappingRequest, db: AsyncSession = Depends(get_db)):
    try:
        identity_service = IdentityService(db)
        result = await identity_service.create_country_identity_mapping(request_data)
        return CountryIdentityMappingResponse(
            mapping_uuid = result.mapping_uuid,
            message = "Country Identity Mapping Created Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/country-mapping/", response_model = list[CountryIdentityMappingDetails])
async def get_all_country_identity_mappings(db: AsyncSession = Depends(get_db)):
    try:
        start = time.perf_counter()
        identity_service = IdentityService(db)
        result = await identity_service.get_all_country_identity_mappings()
        print("TOTAL API TIME:", time.perf_counter() - start)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/country-mapping/{uuid}", response_model = CountryIdentityMappingDetails)
async def get_country_identity_mapping_by_uuid(uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        identity_service = IdentityService(db)
        result = await identity_service.get_country_identity_mapping_by_uuid(uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/country-mapping/{uuid}", response_model= CountryIdentityMappingResponse)
async def update_country_identity_mapping(uuid: str, request_data: CountryIdentityMappingRequest, db: AsyncSession = Depends(get_db)):
    try:
        identity_service = IdentityService(db)
        await identity_service.update_country_identity_mapping(uuid, request_data)
        return CountryIdentityMappingResponse(
            mapping_uuid = uuid,
            message = "country Identity Mapping Updated Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete(
    "/country-mapping/{uuid}",
    response_model=CountryIdentityMappingResponse
)
async def delete_country_identity_mapping(
    uuid: str,
    db: AsyncSession = Depends(get_db)
):
    identity_service = IdentityService(db)
    await identity_service.delete_country_identity_mapping(uuid)

    return CountryIdentityMappingResponse(
        mapping_uuid=uuid,
        message="Country Identity Mapping Deleted Successfully"
    )



@router.get("/country-mapping/identities/{country_uuid}", response_model=list[CountryIdentityDropdownResponse])
async def get_identities_by_country(country_uuid: str, db: AsyncSession = Depends(get_db),):
    try:
        identity_service = IdentityService(db)
        result = await identity_service.get_identities_by_country(country_uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.put("/employee-document/{document_uuid}", response_model=EmployeeIdentityDocumentUpdateResponse)
async def update_employee_identity_document(document_uuid: str, request_data: EmployeeIdentityDocumentUpdateRequest, db: AsyncSession = Depends(get_db)):
    try:
        identity_service = IdentityService(db)

        await identity_service.update_employee_identity_document(
            document_uuid,
            request_data
        )

        return EmployeeIdentityDocumentUpdateResponse(
            document_uuid=document_uuid,
            message="Employee Identity Document Updated Successfully"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))