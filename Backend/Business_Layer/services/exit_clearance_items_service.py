from fastapi import HTTPException
from Backend.DAL.dao.exit_clearance_items_dao import ExitClearanceItemsDAO


class ExitClearanceItemsService:

    def __init__(self):
        self.dao = ExitClearanceItemsDAO()


    async def create_items(self, db, data):

        try:
            return await self.dao.create_items(
                db,
                data.clearance_uuid,
                data.item_name
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def get_items(self, db, clearance_uuid):

        try:
            return await self.dao.get_items(db, clearance_uuid)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def update_item(self, db, data):

        try:
            result = await self.dao.update_item(db, data)

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="Clearance item not found"
                )

            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    async def get_all_items(self, db):
        try:
            return await self.dao.get_all_items(db)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))