
from Backend.DAL.dao.dashboard_dao import DashboardDAO

from ...API_Layer.interfaces.dashboard_interfaces import DashboardResponse
class DashboardService:

    def __init__(self, dao: DashboardDAO):
        self.dao = dao

    async def get_summary(self, start_date=None, end_date=None):
        return await self.dao.get_dashboard_summary(
            start_date=start_date,
            end_date=end_date
        )