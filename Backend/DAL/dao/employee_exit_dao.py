from Backend.Business_Layer.utils.uuid_generator import generate_uuid7
from ..models.models import EmployeeExit
from sqlalchemy import select

class EmployeeExitDAO:

    async def get_employee_exit_by_employee_uuid(self, db, employee_uuid):
        query = select(EmployeeExit).where(
            EmployeeExit.employee_uuid == employee_uuid
        )
        result = await db.execute(query)
        existing = result.scalars().first()
        return existing

    async def create_employee_exit(self, db, data):

        new_exit = EmployeeExit(

        exit_uuid=str(generate_uuid7()),
        employee_uuid=data.employee_uuid,
        employee_id=data.employee_id,
        first_name=data.first_name,
        last_name=data.last_name,
        department_uuid=data.department_uuid,
        designation_uuid=data.designation_uuid,

        exit_type=data.exit_type,
        resignation_date=data.resignation_date,
        last_working_day=data.last_working_day,
        notice_period=data.notice_period,
        notice_start_date=data.notice_start_date,
        notice_end_date=data.notice_end_date,
        reason=data.reason,
        remarks=data.remarks

    )

        db.add(new_exit)
        await db.commit()
        await db.refresh(new_exit)

        return new_exit
    
    async def get_all_employee_exits(self, db):
        query = select(EmployeeExit)
        result = await db.execute(query)
        existing = result.scalars().all()
        return existing
    async def get_employee_exit_by_exit_uuid(self, db, exit_uuid):
        print("Exit UUID received:", exit_uuid)
        query = select(EmployeeExit).where(
            EmployeeExit.exit_uuid == exit_uuid
        )
        result = await db.execute(query)
        existing = result.scalars().first()
        print("Existing record:", existing)
        return existing
    async def update_employee_exit_by_employee_uuid(self, db, employee_uuid, data):
        query = select(EmployeeExit).where(
            EmployeeExit.employee_uuid == employee_uuid
        )
        result = await db.execute(query)
        existing = result.scalars().first()
        if existing:
            existing.employee_uuid = data.employee_uuid
            existing.employee_id = data.employee_id
            existing.first_name = data.first_name
            existing.last_name = data.last_name
            existing.department_uuid = data.department_uuid
            existing.designation_uuid = data.designation_uuid
            existing.exit_type = data.exit_type
            existing.resignation_date = data.resignation_date
            existing.last_working_day = data.last_working_day
            existing.notice_period = data.notice_period
            existing.notice_start_date = data.notice_start_date
            existing.notice_end_date = data.notice_end_date
            existing.reason = data.reason
            existing.remarks = data.remarks
            await db.commit()
            await db.refresh(existing)
        return existing
    async def update_employee_exit_by_exit_uuid(self, db, exit_uuid, data):
        query = select(EmployeeExit).where(
            EmployeeExit.exit_uuid == exit_uuid
        )
        result = await db.execute(query)
        existing = result.scalars().first()
        if existing:
            existing.employee_uuid = data.employee_uuid
            existing.employee_id = data.employee_id
            existing.first_name = data.first_name
            existing.last_name = data.last_name
            existing.department_uuid = data.department_uuid
            existing.designation_uuid = data.designation_uuid
            existing.exit_type = data.exit_type
            existing.resignation_date = data.resignation_date
            existing.last_working_day = data.last_working_day
            existing.notice_period = data.notice_period
            existing.notice_start_date = data.notice_start_date
            existing.notice_end_date = data.notice_end_date
            existing.reason = data.reason
            existing.remarks = data.remarks
            await db.commit()
            await db.refresh(existing)
        return existing
    async def delete_employee_exit(self, db, exit_uuid):
        query = select(EmployeeExit).where(
            EmployeeExit.exit_uuid == exit_uuid
        )
        result = await db.execute(query)
        existing = result.scalars().first()
        if existing:
            await db.delete(existing)
            await db.commit()
        return existing