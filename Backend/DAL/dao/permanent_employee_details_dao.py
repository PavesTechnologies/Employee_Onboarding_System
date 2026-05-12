from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.models.models import EmployeeDetails


class PermanentEmployeeDetailsDAO:

    async def get_last_employee(self, db: AsyncSession):

        result = await db.execute(
            select(EmployeeDetails)
            .order_by(EmployeeDetails.id.desc())
            .limit(1)
        )

        return result.scalars().first()


    async def get_employee_by_user_uuid(self, db: AsyncSession, user_uuid: str):

        result = await db.execute(
            select(EmployeeDetails).where(
                EmployeeDetails.user_uuid == user_uuid
            )
        )

        return result.scalars().first()
    
    async def get_employee_by_email(self, db: AsyncSession, email: str):

        result = await db.execute(
            select(EmployeeDetails).where(
                EmployeeDetails.work_email == email
            )
        )

        return result.scalars().first()

    async def get_employee_by_manager_value(self, db: AsyncSession, reporting_manager):
        if reporting_manager is None:
            return None

        manager_value = str(reporting_manager).strip()
        if not manager_value:
            return None

        filters = [
            EmployeeDetails.employee_id == manager_value,
            EmployeeDetails.employee_uuid == manager_value,
            EmployeeDetails.user_uuid == manager_value,
            func.trim(
                func.concat(
                    EmployeeDetails.first_name,
                    " ",
                    EmployeeDetails.last_name
                )
            ) == manager_value,
            func.trim(
                func.concat(
                    EmployeeDetails.first_name,
                    " ",
                    func.coalesce(EmployeeDetails.middle_name, ""),
                    " ",
                    EmployeeDetails.last_name
                )
            ) == manager_value
        ]

        if manager_value.isdigit():
            filters.insert(0, EmployeeDetails.id == int(manager_value))

        for filter_condition in filters:
            result = await db.execute(
                select(EmployeeDetails).where(filter_condition)
            )
            employee = result.scalars().first()
            if employee:
                return employee

        return None


    async def create_employee(self, db: AsyncSession, employee: EmployeeDetails):

        db.add(employee)
        await db.commit()
        await db.refresh(employee)
        return employee
    
    async def get_employee_by_uuid(self, db: AsyncSession, employee_uuid: str):

        result = await db.execute(
            select(EmployeeDetails).where(
                EmployeeDetails.employee_uuid == employee_uuid
            )
        )

        return result.scalars().first()
    
    async def update_employee(self, db: AsyncSession, employee: EmployeeDetails):

        await db.commit()
        await db.refresh(employee)

        return employee
    
    async def get_all_employees(self, db: AsyncSession):

        result = await db.execute(
            select(EmployeeDetails)
        )

        return result.scalars().all()
    
    async def delete_employee(self, db: AsyncSession, employee_uuid: str):
        employee = await self.get_employee_by_uuid(db, employee_uuid)
        if not employee:
            raise ValueError("Employee not found")

        await db.delete(employee)
        await db.commit()


    async def get_departments(self, db):
        query = text("""
            SELECT department_uuid, department_name
            FROM departments
            ORDER BY department_name
        """)
        result = await db.execute(query)
        return result.fetchall()

    async def get_designations(self, db):
        query = text("""
            SELECT designation_uuid,
                   designation_name,
                   department_uuid
            FROM designations
            ORDER BY designation_name
        """)
        result = await db.execute(query)
        return result.fetchall()

    async def get_department_uuid(self, db, department_name):
        query = text("""
            SELECT department_uuid
            FROM departments
            WHERE department_name = :name
        """)
        result = await db.execute(query, {"name": department_name})
        return result.scalar()

    async def get_designation_uuid(self, db, designation_name):
        query = text("""
            SELECT designation_uuid
            FROM designations
            WHERE designation_name = :name
        """)
        result = await db.execute(query, {"name": designation_name})
        return result.scalar()

    async def get_country_codes(self, db):
        query = text("""
            SELECT DISTINCT calling_code
            FROM countries
            WHERE calling_code IS NOT NULL
              AND calling_code <> ''
            ORDER BY calling_code
        """)
        result = await db.execute(query)
        return [row[0] for row in result.fetchall()]

    async def get_all_employees(self, db):
        query = text("""
            SELECT employee_id,
                   first_name,
                   middle_name,
                   last_name
            FROM employee_details
            WHERE employee_id IS NOT NULL
            ORDER BY employee_id
        """)
        result = await db.execute(query)
        return result.fetchall()

    async def get_next_employee_id(self, db):
        query = text("""
            SELECT MAX(CAST(employee_id AS UNSIGNED))
            FROM employee_details
            WHERE employee_id REGEXP '^[0-9]+$'
        """)
        result = await db.execute(query)
        max_id = result.scalar()

        if not max_id:
            return "5100001"

        return str(int(max_id) + 1)

    async def insert_offer_letter(self, db, row, user_uuid, uploaded_by, reporting_manager_employee_id):
        query = text("""
            INSERT INTO offer_letter_details (
                user_uuid,
                first_name,
                middle_name,
                last_name,
                mail,
                country_code,
                contact_number,
                designation,
                cc_emails,
                employee_type,
                joining_date,
                hire_type,
                status,
                job_id,
                total_ctc,
                currency,
                reporting_manager,
                created_by,
                created_at
            )
            VALUES (
                :user_uuid,
                :first_name,
                :middle_name,
                :last_name,
                :mail,
                :country_code,
                :contact_number,
                :designation,
                :cc_emails,
                :employee_type,
                :joining_date,
                'Direct',
                'Completed',
                :job_id,
                :total_ctc,
                :currency,
                :reporting_manager,
                :created_by,
                NOW()
            )
        """)

        values = {
            "user_uuid": user_uuid,
            "first_name": row.get("first_name"),
            "middle_name": row.get("middle_name"),
            "last_name": row.get("last_name"),
            "mail": row.get("mail"),
            "country_code": row.get("country_code"),
            "contact_number": row.get("contact_number"),
            "designation": row.get("designation"),
            "cc_emails": row.get("cc_emails"),
            "employee_type": row.get("employee_type"),
            "joining_date": row.get("joining_date"),
            "job_id": row.get("job_id"),
            "total_ctc": row.get("total_ctc"),
            "currency": row.get("currency"),
            "reporting_manager": reporting_manager_employee_id,
            "created_by": uploaded_by,
        }

        await db.execute(query, values)

    async def insert_employee(
        self,
        db,
        row,
        user_uuid,
        employee_uuid,
        employee_id,
        work_email,
        department_uuid,
        designation_uuid,
        reporting_manager_employee_id,
        uploaded_by
    ):
        query = text("""
            INSERT INTO employee_details (
                employee_uuid,
                user_uuid,
                employee_id,
                first_name,
                middle_name,
                last_name,
                date_of_birth,
                work_email,
                contact_number,
                department_uuid,
                designation_uuid,
                reporting_manager_uuid,
                employment_type,
                joining_date,
                location,
                work_mode,
                employment_status,
                blood_group,
                gender,
                marital_status,
                total_experience,
                created_by
                
            )
            VALUES (
                :employee_uuid,
                :user_uuid,
                :employee_id,
                :first_name,
                :middle_name,
                :last_name,
                :date_of_birth,
                :work_email,
                :contact_number,
                :department_uuid,
                :designation_uuid,
                :reporting_manager_uuid,
                :employment_type,
                :joining_date,
                :location,
                :work_mode,
                :employment_status,
                :blood_group,
                :gender,
                :marital_status,
                :total_experience,
                :created_by
                
            )
        """)

        values = {
            "employee_uuid": employee_uuid,
            "user_uuid": user_uuid,
            "employee_id": employee_id,
            "first_name": row.get("first_name"),
            "middle_name": row.get("middle_name"),
            "last_name": row.get("last_name"),
            "date_of_birth": row.get("date_of_birth"),
            "work_email": work_email,
            "contact_number": row.get("contact_number"),
            "department_uuid": department_uuid,
            "designation_uuid": designation_uuid,
            "reporting_manager_uuid": reporting_manager_employee_id,
            "employment_type": row.get("employment_type"),
            "joining_date": row.get("joining_date"),
            "location": row.get("location"),
            "work_mode": row.get("work_mode"),
            "employment_status": row.get("employment_status"),
            "blood_group": row.get("blood_group"),
            "gender": row.get("gender"),
            "marital_status": row.get("marital_status"),
            "total_experience": row.get("total_experience"),
            "created_by": uploaded_by,
        }

        await db.execute(query, values)
        await db.commit()



