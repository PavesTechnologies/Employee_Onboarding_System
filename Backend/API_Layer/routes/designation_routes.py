from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from Backend.DAL.dao.designation_dao import DesignationsDAO
from Backend.DAL.utils.dependencies import get_db
from Backend.Business_Layer.services.designation_service import DesignationsService
from Backend.API_Layer.interfaces.designation_interface import (
    DesignationCreate,
    DesignationUpdate,
    DesignationResponse
)
from ..utils.role_based import require_roles

router = APIRouter(
    prefix="/masters/designations",
    tags=["Designations"]
)

@router.post("/", response_model=DesignationResponse, dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def create_designation(data: DesignationCreate, db: AsyncSession = Depends(get_db)):
    designation = await DesignationsService.create_designation(db, data)
    if not designation:
        raise HTTPException(status_code=400, detail="Designation already exists")
    return designation


@router.get("/", response_model=List[DesignationResponse], dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def get_all_designations(db: AsyncSession = Depends(get_db)):
    return await DesignationsService.get_all_designations(db)

@staticmethod
async def get_designations_by_department(db, department_uuid):
    return await DesignationsDAO.get_designations_by_department(
        db, department_uuid
    )

@router.get("/department/{department_uuid}",dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def get_designations_by_department(
    department_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    return await DesignationsService.get_designations_by_department(
        db, department_uuid
    )
@router.put("/{designation_uuid}", response_model=DesignationResponse, dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def update_designation(designation_uuid: str, data: DesignationUpdate, db: AsyncSession = Depends(get_db)):
    designation = await DesignationsService.update_designation(
        db,
        designation_uuid,
        data
    )
    if not designation:
        raise HTTPException(status_code=404, detail="Designation not found")
    return designation

@router.delete("/{designation_uuid}", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def delete_designation(designation_uuid: str, db: AsyncSession = Depends(get_db)):
    designation = await DesignationsService.delete_designation(
        db,
        designation_uuid
    )
    if not designation:
        raise HTTPException(status_code=404, detail="Designation not found")
    return {"message": "Designation deleted successfully"}
