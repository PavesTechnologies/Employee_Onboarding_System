from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.API_Layer.interfaces.weekly_dashboard_interface import DashboardResponse
from Backend.Business_Layer.services.weekly_dashboard_service import get_dashboard_data
from Backend.DAL.utils.dependencies import get_db

router = APIRouter()


@router.get("/", response_model=DashboardResponse)
async def dashboard(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    # ✅ Validation
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date cannot be greater than end_date")

    return await get_dashboard_data(db, start_date, end_date)