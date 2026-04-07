from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.utils.dependencies import get_db
from Backend.Business_Layer.services.employee_exit_service import EmployeeExitService
from Backend.API_Layer.interfaces.employee_exit_interface import EmployeeExitCreate, EmployeeExitResponse

router = APIRouter(
    prefix="/employee-exit",
    tags=["Employee Exit"]
)


# create a employee exit
@router.post("/create", response_model=EmployeeExitResponse)
async def create_employee_exit(
    data: EmployeeExitCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = EmployeeExitService()
        result = await service.create_employee_exit(db, data)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET by employee_uuid
@router.get("/employee/{employee_uuid}", response_model=EmployeeExitResponse)
async def get_employee_exit_by_employee_uuid(
    employee_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = EmployeeExitService()
        result = await service.get_employee_exit_by_employee_uuid(db, employee_uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#Get all exits records
@router.get("/", response_model=list[EmployeeExitResponse])
async def get_all_employee_exits(
    db: AsyncSession = Depends(get_db)
):
    try:
        service = EmployeeExitService()
        result = await service.get_all_employee_exits(db)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#get by exit uuid
@router.get("/exit/{exit_uuid}", response_model=EmployeeExitResponse)
async def get_employee_exit_by_exit_uuid(
    exit_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = EmployeeExitService()
        result = await service.get_employee_exit_by_exit_uuid(db, exit_uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#UPdate the exit record
@router.put("/employee/{employee_uuid}", response_model=EmployeeExitResponse)
async def update_employee_exit(
    employee_uuid: str,
    data: EmployeeExitCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = EmployeeExitService()
        result = await service.update_employee_exit_by_employee_uuid(db, employee_uuid, data)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#update by exit uuid
@router.put("/exit/{exit_uuid}", response_model=EmployeeExitResponse)
async def update_employee_exit(
    exit_uuid: str,
    data: EmployeeExitCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = EmployeeExitService()
        result = await service.update_employee_exit_by_exit_uuid(db, exit_uuid, data)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Delete the exit record
@router.delete("/exit/{exit_uuid}", response_model=EmployeeExitResponse)
async def delete_employee_exit(
    exit_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = EmployeeExitService()
        result = await service.delete_employee_exit(db, exit_uuid)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))