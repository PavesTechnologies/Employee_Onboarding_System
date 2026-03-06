from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..interfaces.master_interfaces import (CreateCountryResponse, CountryDetails, CountryAllDetails,
                                            CreateEducLevelResponse, CreateEducLevelRequest, EducLevelDetails, AllEducLevelDetails,
                                            CountryEductionMapping, CountryEducationMappingDetails,
                                            CreateContactResponse, CreateContactRequest, ContactDetails, UpdateContactRequest)
from ...Business_Layer.services.master_services import CountryService, EducationService, ContactService
from ...DAL.utils.dependencies import get_db
from ..utils.role_based import require_roles

router = APIRouter()
## COUNTRY ROUTES START ##
@router.post("/country", response_model= CreateCountryResponse)
async def create_country(
    calling_code: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        print("country details", calling_code)
        country_service = CountryService(db)
        country_id = await country_service.create_country(calling_code)
        return CreateCountryResponse(
            message = "Created Country Successfully",
            country_uuid = country_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# deactivate country by country uuid
from fastapi import Query

@router.put("/country/deactivateoractivate/{country_uuid}", response_model=CreateCountryResponse)
async def update_country(
    country_uuid: str,
    is_active: bool = Query(...),   # 👈 IMPORTANT
    db: AsyncSession = Depends(get_db)
):
    country_service = CountryService(db)
    message = await country_service.update_country(country_uuid, is_active)
    return CreateCountryResponse(message=message, country_uuid=country_uuid)

# get country details by uuid
@router.get("/country/{country_uuid}", response_model=CountryDetails)
async def get_country_uuid(
    country_uuid: str,
    db: AsyncSession = Depends(get_db)):
    try:
        country_service = CountryService(db)
        result = await country_service.get_country_uuid(country_uuid)
        return CountryDetails(
            country_code = result.calling_code,
            country_name = result.country_name,
            is_active = result.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/country", response_model=list[CountryAllDetails])
async def get_all_countries(
    db: AsyncSession = Depends(get_db)
):
    try:
        country_service = CountryService(db)
        result = await country_service.get_all_countries()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
## COUNTRY ROUTES END ##

## EDUCATION LEVEL ROUTES ##

@router.post("/education-level/", response_model= CreateEducLevelResponse)
async def create_education_level(
    request_data: CreateEducLevelRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
    
        education_service = EducationService(db)
        result = await education_service.create_education_level(request_data)
        return CreateEducLevelResponse(
            education_uuid= result.education_uuid,
            message = "Education Level Created Successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get all education levels
@router.get("/education-level", response_model=list[AllEducLevelDetails])

async def get_all_education_levels(
    db: AsyncSession = Depends(get_db)
):
    try:
        education_service = EducationService(db)
        result = await education_service.get_all_education_levels()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# get education details with uuid
import time

@router.get("/education-level/{education_uuid}", response_model=EducLevelDetails)
async def get_education_level_by_uuid(
    education_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    t0 = time.time()
    print("➡️ route start")

    education_service = EducationService(db)
    t1 = time.time()
    print("service init:", round(t1 - t0, 3))

    result = await education_service.get_education_level_by_uuid(education_uuid)
    t2 = time.time()
    print("service call:", round(t2 - t1, 3))

    print("TOTAL ROUTE:", round(t2 - t0, 3))
    return result

    
# edit education details with uuid
@router.put("/education-level/{education_uuid}", response_model=CreateEducLevelResponse)
async def update_education_level(
    request_data: EducLevelDetails,
    education_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        education_service = EducationService(db)
        result = await education_service.update_education_level(request_data, education_uuid)
        return CreateEducLevelResponse(
            education_uuid = result.education_uuid,
            message = "Education Level Updated Successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# delete education with uuid
@router.delete("/education-level/{education_uuid}", response_model= CreateCountryResponse)
async def delete_education_level(
    education_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        education_service = EducationService(db)
        result = await education_service.delete_education_level(education_uuid)

        return CreateCountryResponse(
            country_uuid = education_uuid,
            message = "Education Level Deleted Successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Education Country Mapping
@router.post("/{educ_level_uuid}/{educ_doc_uuid}/{country_uuid}", response_model=CountryEductionMapping)
async def create_education_country_mapping(
    educ_level_uuid: str,
    educ_doc_uuid: str,
    country_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        education_service = EducationService(db)
        result = await education_service.create_education_country_mapping(educ_level_uuid, educ_doc_uuid, country_uuid)
        return CountryEductionMapping(
            mapping_uuid = result.mapping_uuid,
            message= "Education Country Mapping Created Successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/mapping/{mapping_uuid}", response_model=CountryEductionMapping)
async def delete_education_country_mapping(
    mapping_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        education_service = EducationService(db)
        result = await education_service.delete_education_country_mapping(mapping_uuid)
        return CountryEductionMapping(
            mapping_uuid = result.mapping_uuid,
            message = "Education Country Mapping Deleted Successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/all-mapping", response_model=list[CountryEducationMappingDetails])
async def get_all_education_country_mapping(
    db: AsyncSession = Depends(get_db)
):
    try:
        education_service = EducationService(db)
        result = await education_service.get_all_education_country_mapping()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
## EDUCATION LEVEL AND MAPPING ROUTES ENDS ##

## CONTACTS ROUTES BEGINS ##
# Create contect details
@router.post("/contacts", response_model= CreateContactResponse)
async def create_contact(request_data: CreateContactRequest, db: AsyncSession = Depends(get_db)):
    try:
        contact_service = ContactService(db)
        result = await contact_service.create_contact(request_data)
        return CreateContactResponse(
            contact_uuid = result.contact_uuid,
            message = "Contact Created Successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# get all contacts details
@router.get("/contacts", response_model= list[ContactDetails])
async def get_all_contacts(db: AsyncSession = Depends(get_db)):
    try:
        contact_service = ContactService(db)
        result = await contact_service.get_all_contacts()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# get contact details by uuid
@router.get("/contacts/{contact_uuid}", response_model=ContactDetails)
async def get_contact_by_uuid(contact_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        contact_service = ContactService(db)
        result = await contact_service.get_contact_by_uuid(contact_uuid)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# delete contact details by uuid
@router.delete("/contacts/{contact_uuid}", response_model= CreateContactResponse)
async def delete_contact(contact_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        contact_service = ContactService(db)
        result = await contact_service.delete_contact(contact_uuid)
        return CreateContactResponse(
            contact_uuid = result.contact_uuid,
            message = "Contact Deleted Successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# update contact details by uuid
@router.put("/contacts/{contact_uuid}", response_model=CreateContactResponse)
async def update_contact(
    contact_uuid: str,
    request_data: UpdateContactRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        contact_service = ContactService(db)

        result = await contact_service.update_contact(
            contact_uuid,
            request_data
        )

        return CreateContactResponse(
            contact_uuid=result.contact_uuid,
            message="Contact Updated Successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
