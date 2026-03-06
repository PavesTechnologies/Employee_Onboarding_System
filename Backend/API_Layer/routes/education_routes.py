import time
from time import perf_counter
from tracemalloc import start
from typing import Optional
import uuid
from Backend.API_Layer.interfaces.identity_interfaces import CountryIdentityDropdownResponse
from Backend.Business_Layer.utils.uuid_generator import generate_uuid7
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from ...Business_Layer.services.education_service import EducationDocService
from ...DAL.utils.dependencies import get_db
from ...DAL.utils.storage_utils import S3StorageService
from ...API_Layer.interfaces.education_interfaces import (CountryEducationMappingResponse, CreateEducDocRequest, EducDocResponse, EmployeEduDoc,DeleteEmpEducResponse,
                                                          EducDocDetails, UploadFileResponse, EmployeEduDocDetails, DegreeMasterResponse, DegreeMasterRequest)
from ..utils.role_based import require_roles
start = time.perf_counter()
router = APIRouter()

@router.post("/create_education_document", response_model=EducDocResponse, dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def create_education_document(request_data: CreateEducDocRequest, db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.create_education_document(request_data)
        return EducDocResponse(
            education_document_uuid =result.education_document_uuid,
            message="Education Document Created Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/education-document", response_model=list[EducDocDetails], dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def get_all_education_documents(db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.get_all_education_documents()
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/education-document/{uuid}", response_model = CreateEducDocRequest, dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def get_education_document_by_uuid(uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.get_education_document_by_uuid(uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/education-document/{uuid}", response_model = EducDocResponse, dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def update_education_document(uuid: str, request_data: CreateEducDocRequest, db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.update_education_document(uuid, request_data)

        if result is None:
            raise HTTPException(status_code=404, detail="Education document not found")

        return EducDocResponse(
        education_document_uuid=result.education_document_uuid,
        message="Education Document Updated Successfully"
    )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/education-document/{uuid}", response_model = EducDocResponse, dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def delete_education_document_by_uuid(uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.delete_education_document_by_uuid(uuid)
        return EducDocResponse(
            education_document_uuid = result.education_document_uuid,
            message = "Education Document Deleted Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
## Employee Education Documents ##
    
# creating employee eductaion documents and related details
@router.post("/employee-education-document", response_model=UploadFileResponse)
async def create_employee_education_document(
    mapping_uuid: str = Form(...),
    user_uuid: str = Form(...),
    institution_name: str = Form(...),
    institute_location: str = Form(...),
    degree_uuid: str = Form(...),
    specialization: str = Form(...),
    education_mode: str = Form(...),
    start_year : int = Form(...),
    year_of_passing: int = Form(...),
    delay_reason: Optional[str] = Form(None),
    percentage_cgpa: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)):
    try:      
        print("ROUTE RECEIVED:", mapping_uuid, institution_name, file.filename)

        education_service = EducationDocService(db)
        request_data = {
            "mapping_uuid": mapping_uuid,   
            "user_uuid": user_uuid,
            "institution_name": institution_name,
            "institute_location": institute_location,
            "degree_uuid": degree_uuid,
            "specialization": specialization,
            "education_mode": education_mode,
            "start_year": start_year,
            "year_of_passing": year_of_passing,
            "delay_reason": delay_reason,
            "percentage_cgpa": percentage_cgpa
        }

        result,uuid = await education_service.create_employee_education_document(request_data, file)
        return UploadFileResponse(
            document_uuid = uuid,
            file_path = result,
            message = "Employee Education Document Created Successfully"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/employee-education-document/{document_uuid}", response_model=UploadFileResponse)
async def update_employee_education_document(
    document_uuid: str,
    mapping_uuid: str = Form(...),
    institution_name: str = Form(...),
    institute_location: str = Form(...),
    degree_uuid: str = Form(...),
    specialization: str = Form(...),
    education_mode: str = Form(...),
    start_year : int = Form(...),
    year_of_passing: int = Form(...),
    delay_reason: Optional[str] = Form(None),
    percentage_cgpa: str = Form(...),
    file: UploadFile | None = File(None),   # 👈 optional
    db: AsyncSession = Depends(get_db)
):
    try:
        start_time = time.perf_counter()
        education_service = EducationDocService(db)

        request_data = {
            "mapping_uuid": mapping_uuid,
            "institution_name": institution_name,
            "institute_location": institute_location,
            "degree_uuid": degree_uuid,
            "specialization": specialization,
            "education_mode": education_mode,
            "start_year": start_year,
            "year_of_passing": year_of_passing,
            "delay_reason": delay_reason,
            "percentage_cgpa": percentage_cgpa,
        }

        file_path = await education_service.update_employee_education_document(
            document_uuid, request_data, file
        )
        end_time = time.perf_counter()
        print(f"Time taken to update employee education document: {end_time - start_time}")
        return UploadFileResponse(
            document_uuid=document_uuid,
            file_path=file_path,
            message="Employee Education Document Updated Successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get all employee education documents
@router.get("/employee-education-document", response_model=list[EmployeEduDocDetails])
async def get_all_employee_education_documents(db: AsyncSession = Depends(get_db)):
    try:
        print("entering routes")
        education_service = EducationDocService(db)
        result = await education_service.get_all_employee_education_documents()
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get employee education document by uuid
@router.get("/employee-education-document/{document_uuid}", response_model=EmployeEduDocDetails, dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def get_employee_education_document_by_uuid(uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.get_employee_education_document_by_uuid(uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        
# delete employee education document by uuid
@router.delete("/employee-education-document/{uuid}", response_model=DeleteEmpEducResponse, dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def delete_employee_education_document_by_uuid(uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.delete_employee_education_document_by_uuid(uuid)
        return DeleteEmpEducResponse(
            document_uuid = uuid,
            file_path = result,
            message = "Successfully Deleted Employee Education Document"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/country-mapping/{country_uuid}",response_model=list[CountryEducationMappingResponse])
async def get_education_identity_mappings_by_country_uuid(country_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        print("In route")
        education_service = EducationDocService(db)
        result = await education_service.get_education_identity_mappings_by_country_uuid(country_uuid)
        print("⏱ FULL REQUEST:", time.perf_counter() - start)

        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# create a degree master and generate a uuid for degree master
@router.post("/degree-master", response_model=DegreeMasterResponse)
async def create_degree_master(request_data:DegreeMasterRequest, db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.create_degree_master(request_data)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/degree-master",response_model=list[DegreeMasterResponse])
async def get_degree_master(db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.get_degree_master()
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/degree-master/{education_uuid}",response_model=list[DegreeMasterResponse])
async def get_degree_master_by_education_uuid(education_uuid: str, db: AsyncSession = Depends(get_db)):
    try:
        education_service = EducationDocService(db)
        result = await education_service.get_degree_master_by_education_uuid(education_uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

