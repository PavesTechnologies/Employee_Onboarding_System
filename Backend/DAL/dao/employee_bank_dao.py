from ..models.models import EmployeeBankDetails
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update


class EmployeeBankDAO:

    def __init__(self, db: AsyncSession):
        self.db = db


    async def get_bank_details_by_uuid(self, bank_uuid):
        result = await self.db.execute(
            select(EmployeeBankDetails).where(
                EmployeeBankDetails.bank_uuid == bank_uuid
            )
        )
        return result.scalar_one_or_none()


    async def get_all_bank_details(self):
        result = await self.db.execute(select(EmployeeBankDetails))
        return result.scalars().all()


    async def create_bank_details(self, bank_uuid, request_data):

        bank = EmployeeBankDetails(
            bank_uuid=bank_uuid,
            user_uuid=request_data.user_uuid,
            account_holder_name=request_data.account_holder_name,
            bank_name=request_data.bank_name,
            branch_name=request_data.branch_name,
            account_number=request_data.account_number,
            ifsc_code=request_data.ifsc_code,
            account_type=request_data.account_type
        )

        self.db.add(bank)
        await self.db.commit()
        await self.db.refresh(bank)

        return bank


    async def update_bank_details(self, bank_uuid, request_data):

        result = await self.db.execute(
            select(EmployeeBankDetails).where(
                EmployeeBankDetails.bank_uuid == bank_uuid
            )
        )

        bank = result.scalar_one_or_none()

        if not bank:
            return None

        bank.account_holder_name = request_data.account_holder_name
        bank.bank_name = request_data.bank_name
        bank.branch_name = request_data.branch_name
        bank.account_number = request_data.account_number
        bank.ifsc_code = request_data.ifsc_code
        bank.account_type = request_data.account_type

        await self.db.commit()
        await self.db.refresh(bank)

        return bank


    async def delete_bank_details(self, bank_uuid):

        result = await self.db.execute(
            select(EmployeeBankDetails).where(
                EmployeeBankDetails.bank_uuid == bank_uuid
            )
        )

        bank = result.scalar_one_or_none()

        await self.db.delete(bank)
        await self.db.commit()

        return bank