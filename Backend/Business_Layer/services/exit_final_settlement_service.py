from fastapi import HTTPException
from Backend.DAL.dao.exit_final_settlement_dao import ExitFinalSettlementDAO


class ExitFinalSettlementService:

    def __init__(self):
        self.dao = ExitFinalSettlementDAO()


    async def create_settlement(self, db, data):

        try:
            return await self.dao.create_settlement(db, data)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def get_settlement(self, db, exit_uuid):

        try:
            return await self.dao.get_settlement(db, exit_uuid)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def approve_settlement(self, db, settlement_uuid, user_id, remarks):

        try:

            result = await self.dao.approve_settlement(
                db,
                settlement_uuid,
                user_id,
                remarks
            )

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="Settlement not found"
                )

            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def mark_paid(self, db, settlement_uuid):

        try:

            result = await self.dao.mark_paid(
                db,
                settlement_uuid
            )

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="Settlement not found"
                )

            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))