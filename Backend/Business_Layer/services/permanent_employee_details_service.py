import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.API_Layer.interfaces.permenent_employee_details_interfaces import (
    CreatePermanentEmployeeRequest,
    CreatePermanentEmployeeResponse,
    UpdatePermanentEmployeeRequest
)

from Backend.DAL.dao.permanent_employee_details_dao import PermanentEmployeeDetailsDAO
from Backend.DAL.models.models import EmployeeDetails


class PermanentEmployeeDetailsService:

    def __init__(self):
        self.dao = PermanentEmployeeDetailsDAO()

   

    async def generate_employee_id(self, db: AsyncSession):

        last_employee = await self.dao.get_last_employee(db)

        if last_employee and last_employee.employee_id:
            new_employee_id = int(last_employee.employee_id) + 1
        else:
            new_employee_id = 5100001

        return str(new_employee_id)
    

    async def generate_work_email(self, db: AsyncSession, first_name: str, last_name: str):

        domain = "pavestechnologies.com"

        first_parts = first_name.lower().split()
        last = last_name.lower()

        # possible combinations
        combinations = []

        # ajaykumar.korada
        combinations.append("".join(first_parts) + "." + last)

        # ajay.korada
        combinations.append(first_parts[0] + "." + last)

        # ajayk.korada
        if len(first_parts) > 1:
            combinations.append(first_parts[0] + first_parts[1][0] + "." + last)

        # akorada
        combinations.append(first_parts[0][0] + last)

        # try combinations first
        for combo in combinations:

            email = f"{combo}@{domain}"

            existing = await self.dao.get_employee_by_email(db, email)

            if not existing:
                return email

        # if all combinations exist → add number
        base = combinations[0]

        counter = 1

        while True:

            email = f"{base}{counter}@{domain}"

            existing = await self.dao.get_employee_by_email(db, email)

            if not existing:
                return email

            counter += 1
    async def create_employee(self, db: AsyncSession, request: CreatePermanentEmployeeRequest):

        # check if employee already exists for this user
        existing = await self.dao.get_employee_by_user_uuid(db, request.user_uuid)

        if existing:
            raise ValueError("Employee already created for this user")

        employee_id = await self.generate_employee_id(db)

        work_email = await self.generate_work_email(db, request.first_name, request.last_name)
        employee = EmployeeDetails(

            employee_uuid=str(uuid.uuid4()),
            user_uuid=request.user_uuid,
            employee_id=employee_id,

            first_name=request.first_name,
            middle_name=request.middle_name,
            last_name=request.last_name,
            date_of_birth=request.date_of_birth,
            work_email=work_email,
            contact_number=request.contact_number,

            department_uuid=request.department_uuid,
            designation_uuid=request.designation_uuid,
            reporting_manager_uuid=request.reporting_manager_uuid,

            employment_type=request.employment_type,
            joining_date=request.joining_date,
            location=request.location,
            work_mode=request.work_mode,
            employment_status=request.employment_status,

            blood_group=request.blood_group,
            gender=request.gender,
            marital_status=request.marital_status,

            total_experience=request.total_experience,

            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )

        employee = await self.dao.create_employee(db, employee)

        return CreatePermanentEmployeeResponse(
            employee_uuid=employee.employee_uuid,
            employee_id=employee.employee_id,
            work_email=employee.work_email,
            message="Employee created successfully"
        )
    
    async def get_employee_by_uuid(self, db: AsyncSession, employee_uuid: str):

        employee = await self.dao.get_employee_by_uuid(db, employee_uuid)

        if not employee:
            raise ValueError("Employee not found")

        return {
            "user_uuid": employee.user_uuid,
            "employee_uuid": employee.employee_uuid,
            "employee_id": employee.employee_id,
            "first_name": employee.first_name,
            "middle_name": employee.middle_name,
            "last_name": employee.last_name,
            "date_of_birth": employee.date_of_birth,
            "work_email": employee.work_email,
            "contact_number": employee.contact_number,
            "department_uuid": employee.department_uuid,
            "designation_uuid": employee.designation_uuid,
            "reporting_manager_uuid": employee.reporting_manager_uuid,
            "employment_type": employee.employment_type,
            "joining_date": employee.joining_date,
            "location": employee.location,
            "work_mode": employee.work_mode,
            "employment_status": employee.employment_status,
            "blood_group": employee.blood_group,
            "gender": employee.gender,
            "marital_status": employee.marital_status,
            "total_experience": employee.total_experience
        }
    
    async def get_all_employees(self, db: AsyncSession):

        employees = await self.dao.get_all_employees(db)

        response = []

        for emp in employees:
            response.append({
                "user_uuid": emp.user_uuid,
                "employee_uuid": emp.employee_uuid,
                "employee_id": emp.employee_id,
                "first_name": emp.first_name,
                "middle_name": emp.middle_name,
                "last_name": emp.last_name,
                "date_of_birth": emp.date_of_birth,
                "work_email": emp.work_email,
                "contact_number": emp.contact_number,
                "department_uuid": emp.department_uuid,
                "designation_uuid": emp.designation_uuid,
                "employment_type": emp.employment_type,
                "joining_date": emp.joining_date,
                "location": emp.location,
                "work_mode": emp.work_mode,
                "employment_status": emp.employment_status,
                "blood_group": emp.blood_group,
                "gender": emp.gender,
                "marital_status": emp.marital_status
            })

        return response
    
    # async def update_employee(
    #     self,
    #     db: AsyncSession,
    #     employee_uuid: str,
    #     request: UpdatePermanentEmployeeRequest
    # ):

    #     employee = await self.dao.get_employee_by_uuid(db, employee_uuid)

    #     if not employee:
    #         raise ValueError("Employee not found")

    #     employee.first_name = request.first_name
    #     employee.middle_name = request.middle_name
    #     employee.last_name = request.last_name
    #     employee.date_of_birth = request.date_of_birth
    #     employee.contact_number = request.contact_number

    #     employee.department_uuid = request.department_uuid
    #     employee.designation_uuid = request.designation_uuid
    #     employee.reporting_manager_uuid = request.reporting_manager_uuid

    #     employee.employment_type = request.employment_type
    #     employee.joining_date = request.joining_date
    #     employee.location = request.location
    #     employee.work_mode = request.work_mode
    #     employee.employment_status = request.employment_status

    #     employee.blood_group = request.blood_group
    #     employee.gender = request.gender
    #     employee.marital_status = request.marital_status

    #     employee.total_experience = request.total_experience
    #     employee.updated_at = datetime.datetime.utcnow()

    #     employee = await self.dao.update_employee(db, employee)

    #     return {
    #         "employee_uuid": employee.employee_uuid,
    #         "employee_id": employee.employee_id,
    #         "message": "Employee updated successfully"
    #     }
    async def update_employee(
        self,
        db: AsyncSession,
        employee_uuid: str,
        request: UpdatePermanentEmployeeRequest
        ):

        employee = await self.dao.get_employee_by_uuid(db, employee_uuid)

        if not employee:
            raise ValueError("Employee not found")

        if request.first_name is not None:
            employee.first_name = request.first_name

        if request.middle_name is not None:
            employee.middle_name = request.middle_name

        if request.last_name is not None:
            employee.last_name = request.last_name

        if request.date_of_birth is not None:
            employee.date_of_birth = request.date_of_birth

        if request.contact_number is not None:
            employee.contact_number = request.contact_number

        if request.department_uuid is not None:
            employee.department_uuid = request.department_uuid

        if request.designation_uuid is not None:
            employee.designation_uuid = request.designation_uuid

        if request.reporting_manager_uuid is not None:
            employee.reporting_manager_uuid = request.reporting_manager_uuid

        if request.employment_type is not None:
            employee.employment_type = request.employment_type

        if request.joining_date is not None:
            employee.joining_date = request.joining_date

        if request.location is not None:
            employee.location = request.location

        if request.work_mode is not None:
            employee.work_mode = request.work_mode

        if request.employment_status is not None:
            employee.employment_status = request.employment_status

        if request.blood_group is not None:
            employee.blood_group = request.blood_group

        if request.gender is not None:
            employee.gender = request.gender

        if request.marital_status is not None:
            employee.marital_status = request.marital_status

        if request.total_experience is not None:
            employee.total_experience = request.total_experience

        employee.updated_at = datetime.datetime.utcnow()

        employee = await self.dao.update_employee(db, employee)

        return {
            "employee_uuid": employee.employee_uuid,
            "employee_id": employee.employee_id,
            "message": "Employee updated successfully"
        }
    
    async def delete_employee(self, db: AsyncSession, employee_uuid: str):

        employee = await self.dao.get_employee_by_uuid(db, employee_uuid)

        if not employee:
            raise ValueError("Employee not found")

        await self.dao.delete_employee(db, employee_uuid)

        return {"message": "Employee deleted successfully"}