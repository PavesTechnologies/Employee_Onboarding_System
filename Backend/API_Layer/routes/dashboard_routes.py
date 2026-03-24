from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.utils.dependencies import get_db
from ...DAL.dao.dashboard_dao import DashboardDAO
from ...Business_Layer.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/onboarding-summary")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    start_date: str = Query(None),   # optional filter
    end_date: str = Query(None)
):
    """
    Get onboarding dashboard summary:
    - Overview (offer stats)
    - Pipeline
    - Pending actions
    - Metrics
    - Documents (verified counts)
    - Aging
    - Recent activity
    """

    dao = DashboardDAO(db)
    service = DashboardService(dao)

    return await service.get_summary(
        start_date=start_date,
        end_date=end_date
    )