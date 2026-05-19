import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from Backend.Business_Layer.utils.excel_parcer import parse_excel
from Backend.Business_Layer.utils.uuid_generator import generate_uuid7
from Backend.API_Layer.interfaces.permenent_employee_details_interfaces import (
    CreatePermanentEmployeeRequest,
    CreatePermanentEmployeeResponse,
    UpdatePermanentEmployeeRequest
)
from io import BytesIO
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.workbook.defined_name import DefinedName
from Backend.DAL.dao.permanent_employee_details_dao import PermanentEmployeeDetailsDAO
from Backend.DAL.models.models import EmployeeDetails
from openpyxl.utils import get_column_letter
from datetime import datetime


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

    async def resolve_reporting_manager_employee_id(self, db: AsyncSession, reporting_manager):
        if reporting_manager is None or str(reporting_manager).strip() == "":
            return None

        manager = await self.dao.get_employee_by_manager_value(
            db,
            reporting_manager
        )

        if not manager:
            raise ValueError("Invalid reporting manager selected")

        return manager.employee_id

    async def create_employee(self, db: AsyncSession, payload: CreatePermanentEmployeeRequest, current_user_id: str):

        # check if employee already exists for this user
        existing = await self.dao.get_employee_by_user_uuid(db, payload.user_uuid)

        if existing:
            raise ValueError("Employee already created for this user")

        employee_id = await self.generate_employee_id(db)

        work_email = await self.generate_work_email(db, payload.first_name, payload.last_name)
        reporting_manager_employee_id = await self.resolve_reporting_manager_employee_id(
            db,
            payload.reporting_manager_uuid
        )
        print("Generated user ID:",current_user_id )
        employee = EmployeeDetails(

            employee_uuid=str(uuid.uuid4()),
            user_uuid=payload.user_uuid,
            employee_id=employee_id,

            first_name=payload.first_name,
            middle_name=payload.middle_name,
            last_name=payload.last_name,
            date_of_birth=payload.date_of_birth,
            work_email=work_email,
            contact_number=payload.contact_number,

            department_uuid=payload.department_uuid,
            designation_uuid=payload.designation_uuid,
            reporting_manager_uuid=reporting_manager_employee_id,

            employment_type=payload.employment_type,
            joining_date=payload.joining_date,
            location=payload.location,
            work_mode=payload.work_mode,
            employment_status=payload.employment_status,

            blood_group=payload.blood_group,
            gender=payload.gender,
            marital_status=payload.marital_status,

            total_experience=payload.total_experience,
            created_by=current_user_id,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )

        print("Employee object to be created", employee)
        employee = await self.dao.create_employee(db, employee)
        print("Employee created in DB", employee)
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
                               "user_uuid": emp["user_uuid"],  # Now this works!
                "employee_uuid": emp["employee_uuid"],
                "employee_id": emp.get("employee_id"),
                "first_name": emp.get("first_name"),
                "middle_name": emp.get("middle_name"),
                "last_name": emp.get("last_name"),
                "date_of_birth": str(emp["date_of_birth"]) if emp.get("date_of_birth") else None,
                "work_email": emp.get("work_email"),
                "contact_number": emp.get("contact_number"),
                "department_uuid": emp.get("department_uuid"),
                "designation_uuid": emp.get("designation_uuid"),
                "reporting_manager_uuid": emp.get("reporting_manager_uuid"),
                "employment_type": emp.get("employment_type"),
                "joining_date": str(emp["joining_date"]) if emp.get("joining_date") else None,
                "location": emp.get("location"),
                "work_mode": emp.get("work_mode"),
                "employment_status": emp.get("employment_status"),
                "blood_group": emp.get("blood_group"),
                "gender": emp.get("gender"),
                "marital_status": emp.get("marital_status"),
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
            employee.reporting_manager_uuid = await self.resolve_reporting_manager_employee_id(
                db,
                request.reporting_manager_uuid
            )

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

    CURRENCIES = ["INR", "USD", "EUR", "GBP", "AED", "SGD", "AUD", "CAD"]
    EMPLOYEE_TYPES = ["Full-Time", "Part-Time", "Intern", "Contractor", "Freelance"]
    WORK_MODES = ["Office", "Remote", "Hybrid"]
    EMPLOYMENT_STATUSES = [
        "Probation",
        "Active",
        "Resigned",
        "Terminated",
        "Absconded",
        "Exited",
        "On-Notice",
    ]
    BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    GENDERS = ["Male", "Female", "Other"]
    MARITAL_STATUSES = ["Single", "Married", "Divorced", "Widowed"]

   

    def get_employee_id(self, manager_value):
        if not manager_value:
            return None
        value = str(manager_value).strip()
        if " - " in value:
            return value.split(" - ", 1)[0].strip()
        return value


    async def bulk_direct_upload(self, db, file, current_user_id):
        data = parse_excel(file)

        success_count = 0
        failed_records = []

        for index, row in enumerate(data):
            try:
                # Convert date fields from DD/MM/YYYY to YYYY-MM-DD
                for field in ["joining_date", "date_of_birth"]:
                    if row.get(field):
                        value = row.get(field)

                        # If Excel parser returns string like 13/05/2026
                        if isinstance(value, str):
                            try:
                                row[field] = datetime.strptime(
                                    value.strip(),
                                    "%d/%m/%Y"
                                ).date()
                            except ValueError:
                                # If already in another valid format, leave as-is
                                pass

                user_uuid = str(generate_uuid7())
                employee_uuid = str(generate_uuid7())

                employee_id = row.get("employee_id")
                work_email = row.get("work_email")
                department_uuid = await self.dao.get_department_uuid(
                    db,
                    row.get("department")
                )

                designation_uuid = await self.dao.get_designation_uuid(
                    db,
                    row.get("designation")
                )

                reporting_manager_employee_id = self.get_employee_id(
                    row.get("reporting_manager_uuid")
                )

                await self.dao.insert_offer_letter(
                    db,
                    row,
                    user_uuid,
                    current_user_id,
                    reporting_manager_employee_id
                )

                await self.dao.insert_employee(
                    db,
                    row,
                    user_uuid,
                    employee_uuid,
                    employee_id,
                    work_email,
                    department_uuid,
                    designation_uuid,
                    reporting_manager_employee_id,
                    current_user_id,
                )

                success_count += 1

            except Exception as e:
                failed_records.append(
                    {
                        "row": index + 2,
                        "reason": str(e),
                    }
                )

        return {
            "message": "Bulk upload completed",
            "success_count": success_count,
            "failed_count": len(failed_records),
            "failed_records": failed_records,
        }
    async def download_bulk_template(self, db):
        departments = await self.dao.get_departments(db)
        designations = await self.dao.get_designations(db)
        country_codes = await self.dao.get_country_codes(db)
        employees = await self.dao.get_employees_for_dropdown(db)

        manager_values = []
        for emp in employees:
            employee_id, first_name, middle_name, last_name = emp
            name = " ".join(
                part for part in [first_name, middle_name, last_name] if part
            ).strip()
            manager_values.append(f"{employee_id} - {name}")

        headers = [
            "first_name",
            "middle_name",
            "last_name",
            "mail",
            "country_code",
            "contact_number",
            "employee_type",
            "currency",
            "joining_date",
            "cc_emails",
            "total_ctc",
            "job_id",
            "date_of_birth",
            "work_email",
            "employee_id",
            "department",
            "designation",
            "reporting_manager_uuid",
            "employment_type",
            "location",
            "work_mode",
            "employment_status",
            "blood_group",
            "gender",
            "marital_status",
            "total_experience",
        ]

        wb = Workbook()
        ws = wb.active
        ws.title = "Employee Upload"
        ws.append(headers)

        master = wb.create_sheet("Master")

        master_data = {
            "CountryCodes": country_codes,
            "EmployeeTypes": self.EMPLOYEE_TYPES,
            "Currencies": self.CURRENCIES,
            "Managers": manager_values,
            "EmploymentTypes": self.EMPLOYEE_TYPES,
            "WorkModes": self.WORK_MODES,
            "EmploymentStatuses": self.EMPLOYMENT_STATUSES,
            "BloodGroups": self.BLOOD_GROUPS,
            "Genders": self.GENDERS,
            "MaritalStatuses": self.MARITAL_STATUSES,
        }

        col = 1
        for range_name, values in master_data.items():
            master.cell(row=1, column=col, value=range_name)
            for i, value in enumerate(values, start=2):
                master.cell(row=i, column=col, value=value)

            if values:
                col_letter = get_column_letter(col)
                wb.defined_names.add(
                    DefinedName(
                        range_name,
                        attr_text=f"Master!${col_letter}$2:${col_letter}${len(values)+1}",
                    )
                )
            col += 1

        dept_map = {}
        for designation_uuid, designation_name, department_uuid in designations:
            dept_map.setdefault(department_uuid, []).append(designation_name)

        for department_uuid, department_name in departments:
            safe_name = department_name.replace(" ", "_")
            master.cell(row=1, column=col, value=safe_name)

            des_list = dept_map.get(department_uuid, [])
            for i, des in enumerate(des_list, start=2):
                master.cell(row=i, column=col, value=des)

            if des_list:
                col_letter = get_column_letter(col)
                wb.defined_names.add(
                    DefinedName(
                        safe_name,
                        attr_text=f"Master!${col_letter}$2:${col_letter}${len(des_list)+1}",
                    )
                )
            col += 1

        dept_names = [dept[1] for dept in departments]
        master.cell(row=1, column=col, value="Departments")
        for i, dept_name in enumerate(dept_names, start=2):
            master.cell(row=i, column=col, value=dept_name)

        if dept_names:
            col_letter = get_column_letter(col)
            wb.defined_names.add(
                DefinedName(
                    "Departments",
                    attr_text=f"Master!${col_letter}$2:${col_letter}${len(dept_names)+1}",
                )
            )

        header_to_col = {header: i + 1 for i, header in enumerate(headers)}

        def add_dropdown(header, range_name):
            col_idx = header_to_col[header]
            col_letter = get_column_letter(col_idx)
            dv = DataValidation(type="list", formula1=f"={range_name}", allow_blank=True)
            ws.add_data_validation(dv)
            dv.add(f"{col_letter}2:{col_letter}500")

        add_dropdown("country_code", "CountryCodes")
        add_dropdown("employee_type", "EmployeeTypes")
        add_dropdown("currency", "Currencies")
        add_dropdown("reporting_manager_uuid", "Managers")
        add_dropdown("employment_type", "EmploymentTypes")
        add_dropdown("work_mode", "WorkModes")
        add_dropdown("employment_status", "EmploymentStatuses")
        add_dropdown("blood_group", "BloodGroups")
        add_dropdown("gender", "Genders")
        add_dropdown("marital_status", "MaritalStatuses")
        add_dropdown("department", "Departments")

        dept_col = get_column_letter(header_to_col["department"])
        des_col = get_column_letter(header_to_col["designation"])

        for row in range(2, 501):
            dv = DataValidation(
                type="list",
                formula1=f'=INDIRECT(SUBSTITUTE(${dept_col}{row}," ","_"))',
                allow_blank=True,
            )
            ws.add_data_validation(dv)
            dv.add(f"{des_col}{row}")

        master.sheet_state = "hidden"

        stream = BytesIO()
        wb.save(stream)
        stream.seek(0)

        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=employee_template.xlsx"
            },
        )
