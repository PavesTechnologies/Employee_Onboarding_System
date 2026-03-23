from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.utils.dependencies import get_db
from Backend.Business_Layer.services.departments_service import DepartmentsService
from Backend.API_Layer.interfaces.departments_interface import DepartmentCreate, DepartmentResponse, DepartmentUpdate
from ..utils.role_based import require_roles


router = APIRouter(
    prefix="/masters/departments",
    tags=["Departments"]
)


@router.post("/", response_model=DepartmentResponse, dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def create_department(
    department: DepartmentCreate,
    db: AsyncSession = Depends(get_db)
):

    dept = await DepartmentsService.create_department(db, department)

    if not dept:
        raise HTTPException(status_code=400, detail="Department already exists")

    return dept

@staticmethod
@router.get("/", response_model=List[DepartmentResponse],dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def get_departments(db: AsyncSession = Depends(get_db)):

    departments = await DepartmentsService.get_all_departments(db)

    return departments

@router.put("/{department_uuid}", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def update_department(
    department_uuid: str,
    data: DepartmentUpdate,
    db: AsyncSession = Depends(get_db)
):

    department = await DepartmentsService.update_department(
        db,
        department_uuid,
        data
    )

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    return department

@router.get("/{department_uuid}", response_model=DepartmentResponse, dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def get_department_by_uuid(
    department_uuid: str,
    db: AsyncSession = Depends(get_db)
):

    department = await DepartmentsService.get_department_by_uuid(
        db,
        department_uuid
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return department

@router.delete("/{department_uuid}", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def delete_department(
    department_uuid: str,
    db: AsyncSession = Depends(get_db)
):

    department = await DepartmentsService.delete_department(
        db,
        department_uuid
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return {"message": "Department deleted successfully"}