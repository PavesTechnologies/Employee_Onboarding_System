from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.utils.dependencies import get_db
from Backend.Business_Layer.services.organisationtree_service import (
    OrganizationTreeService,
)

router = APIRouter(prefix="/hr", tags=["Organization Tree"])


@router.get("/organization-hierarchy/{employee_id}")
async def get_organization_hierarchy(
    employee_id: str, db: AsyncSession = Depends(get_db)
):

    service = OrganizationTreeService(db)

    return await service.get_organization_hierarchy(employee_id)
