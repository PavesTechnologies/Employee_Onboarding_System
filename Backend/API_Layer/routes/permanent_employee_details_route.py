from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.API_Layer.interfaces.permenent_employee_details_interfaces import CreatePermanentEmployeeRequest, CreatePermanentEmployeeResponse, UpdatePermanentEmployeeRequest
from Backend.Business_Layer.services.permanent_employee_details_service import PermanentEmployeeDetailsService

from ...DAL.utils.dependencies import get_db
from Backend.API_Layer.utils.role_based import require_roles
from Backend.DAL.utils.database import get_read_db


router = APIRouter(
    prefix="/core-employee-details",
    tags=["Permanent Employees"]
)

service = PermanentEmployeeDetailsService()


@router.post("/", response_model=CreatePermanentEmployeeResponse)
async def create_employee(
        payload: CreatePermanentEmployeeRequest,
        request: Request,
        db: AsyncSession = Depends(get_db)
):

    try:
        current_user_id = request.state.user.get("employee_id")
        print("Current user id",current_user_id)
        return await service.create_employee(db, payload, current_user_id)

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@router.get("/{employee_uuid}")
async def get_employee(
    employee_uuid: str,
    db: AsyncSession = Depends(get_db)
    ):
    try:
        return await service.get_employee_by_uuid(db, employee_uuid)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
@router.get("/")
async def get_all_employees(
    db: AsyncSession = Depends(get_db)
):
    return await service.get_all_employees(db)

@router.put("/{employee_uuid}")
async def update_employee(
    employee_uuid: str,
    request: UpdatePermanentEmployeeRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await service.update_employee(db, employee_uuid, request)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
            
@router.delete("/{employee_uuid}")
async def delete_employee(
    employee_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await service.delete_employee(db, employee_uuid)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
def get_current_employee_id(request: Request) -> str:
    employee_id = request.state.user.get("employee_id")
    if not employee_id:
        raise HTTPException(status_code=401, detail="Employee ID missing in token")
    return str(employee_id)
@router.post("/bulk-direct-upload")
async def bulk_direct_upload(
    request : Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        current_user_id = get_current_employee_id(request)
        print("Uploaded by",current_user_id)
        return await service.bulk_direct_upload(db, file, current_user_id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bulk-template/")
async def download_bulk_template(
    db: AsyncSession = Depends(get_read_db),
):
    try:
        return await service.download_bulk_template(db)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

