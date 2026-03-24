from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.utils.dependencies import get_db
from Backend.Business_Layer.services.analytics_service import (
    get_demographics,
    get_worker_department,
    get_gender_department,
    get_employment_department
)
from Backend.API_Layer.interfaces.analytics_interfaces import DashboardResponse

router = APIRouter( tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(db: AsyncSession = Depends(get_db)):
    return {
        "demographics": await get_demographics(db),
        "workerDept": await get_worker_department(db),
        "genderDept": await get_gender_department(db),
        "employmentDept": await get_employment_department(db),
    }




# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession

# from Backend.DAL.utils.dependencies import get_db
# from Backend.Business_Layer.services.analytics_service import get_demographics
# from Backend.API_Layer.interfaces.analytics_interfaces import DemographicsResponse

# router = APIRouter( tags=["Analytics"])


# @router.get("/demographics", response_model=DemographicsResponse)
# async def demographics(db: AsyncSession = Depends(get_db)):
#     return await get_demographics(db)