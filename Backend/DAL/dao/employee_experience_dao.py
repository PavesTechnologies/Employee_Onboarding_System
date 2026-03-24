from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from ..models.models import EmployeeExperience


class EmployeeExperienceDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ----------------------------------------------------
    # GETTERS
    # ----------------------------------------------------

    async def get_experience_by_uuid(self, experience_uuid: str):
        result = await self.db.execute(
            select(EmployeeExperience).where(
                EmployeeExperience.experience_uuid == experience_uuid
            )
        )
        return result.scalar_one_or_none()

    async def get_experience_by_employee_uuid(self, employee_uuid: str):
        result = await self.db.execute(
            select(EmployeeExperience).where(
                EmployeeExperience.employee_uuid == employee_uuid
            )
        )
        return result.scalars().all()

    async def get_all_experience(self):
        result = await self.db.execute(select(EmployeeExperience))
        return result.scalars().all()

    async def get_current_job(self, employee_uuid: str, exclude_uuid: str | None = None):
        query = select(EmployeeExperience).where(
            EmployeeExperience.employee_uuid == employee_uuid,
            EmployeeExperience.is_current == True
        )

        if exclude_uuid:
            query = query.where(EmployeeExperience.experience_uuid != exclude_uuid)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_experience_by_company(self, employee_uuid: str, company_name: str):
        result = await self.db.execute(
            select(EmployeeExperience).where(
                EmployeeExperience.employee_uuid == employee_uuid,
                EmployeeExperience.company_name == company_name
            )
        )
        return result.scalar_one_or_none()

    # ----------------------------------------------------
    # CREATE
    # ----------------------------------------------------

    async def create_experience(
        self,
        request_data,
        experience_uuid: str,
        exp_certificate_path: str | None,
        payslip_path: str | None,
        internship_certificate_path: str | None,
        contract_aggrement_path: str | None,
    ):
        new_exp = EmployeeExperience(
            experience_uuid=experience_uuid,
            employee_uuid=request_data.employee_uuid,
            company_name=request_data.company_name,
            role_title=request_data.role_title,
            employment_type=request_data.employment_type.value,
            start_date=request_data.start_date,
            end_date=request_data.end_date,
            is_current=request_data.is_current,
            notice_period_days=request_data.notice_period_days,

            exp_certificate_path=exp_certificate_path,
            payslip_path=payslip_path,
            internship_certificate_path=internship_certificate_path,
            contract_aggrement_path=contract_aggrement_path,

            status="uploaded",
            uploaded_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.db.add(new_exp)
        await self.db.commit()
        await self.db.refresh(new_exp)

        return {
            "experience_uuid": experience_uuid,
            "message": "Experience record created successfully",
        }

    # ----------------------------------------------------
    # UPDATE
    async def update_experience_full(
        self,
        experience,
        company_name,
        role_title,
        employment_type,
        start_date,
        end_date,
        is_current,
        notice_period_days,
        paths,
    ):
        experience.company_name = company_name
        experience.role_title = role_title
        experience.employment_type = employment_type.value
        experience.start_date = start_date
        experience.end_date = end_date
        experience.is_current = is_current
        if is_current:
            experience.notice_period_days = notice_period_days
        else:
            experience.notice_period_days = None

        # 🔹 Updated file paths
        experience.exp_certificate_path = paths["exp_certificate_path"]
        experience.payslip_path = paths["payslip_path"]
        experience.internship_certificate_path = paths["internship_certificate_path"]
        experience.contract_aggrement_path = paths["contract_aggrement_path"]

        experience.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(experience)

        return {
            "experience_uuid": experience.experience_uuid,
            "message": "Experience updated successfully",
        }

    
    # ----------------------------------------------------
    # DELETE
    # ----------------------------------------------------

    async def delete_experience(self, experience_uuid: str):
        experience = await self.get_experience_by_uuid(experience_uuid)
        if not experience:
            return None

        await self.db.delete(experience)
        await self.db.commit()

        return experience

    # ----------------------------------------------------
    # CERTIFICATE PATH UPDATE
    # ----------------------------------------------------

    async def update_experience_certificate(self, experience_uuid: str, file_path: str):

        experience = await self.get_experience_by_uuid(experience_uuid)
        if not experience:
            return None

        experience.exp_certificate_path = file_path
        experience.status = "uploaded"
        experience.uploaded_at = datetime.utcnow()
        experience.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(experience)

        return experience
    
    #----------------------------------------------------
    # DELETE CERTIFICATE PATH
    #----------------------------------------------------
    async def delete_experience_certificate(self, experience_uuid: str):
        experience = await self.get_experience_by_uuid(experience_uuid)
        if not experience:
            return None

        experience.exp_certificate_path = None
        experience.status = "uploaded"
        experience.uploaded_at = None
        experience.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(experience)
        return experience

