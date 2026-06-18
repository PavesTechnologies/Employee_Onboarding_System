# =========================================================
# permanent_employee_details_dao.py
# =========================================================

from sqlalchemy import func, select, text, cast, Integer
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.models.models import EmployeeDetails


class PermanentEmployeeDetailsDAO:

    # =====================================================
    # EMPLOYEE HELPERS
    # =====================================================

    async def get_last_employee(self, db: AsyncSession):

        result = await db.execute(
            select(func.max(cast(EmployeeDetails.employee_id, Integer))).where(
                EmployeeDetails.employee_id.isnot(None)
            )
        )

        return result.scalar()

    async def get_employee_by_user_uuid(self, db: AsyncSession, user_uuid: str):

        result = await db.execute(
            select(EmployeeDetails).where(EmployeeDetails.user_uuid == user_uuid)
        )

        return result.scalars().first()

    async def get_employee_by_email(self, db: AsyncSession, email: str):

        result = await db.execute(
            select(EmployeeDetails).where(EmployeeDetails.work_email == email)
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
                func.concat(EmployeeDetails.first_name, " ", EmployeeDetails.last_name)
            )
            == manager_value,
            func.trim(
                func.concat(
                    EmployeeDetails.first_name,
                    " ",
                    func.coalesce(EmployeeDetails.middle_name, ""),
                    " ",
                    EmployeeDetails.last_name,
                )
            )
            == manager_value,
        ]

        if manager_value.isdigit():
            filters.insert(0, EmployeeDetails.id == int(manager_value))

        for filter_condition in filters:

            result = await db.execute(select(EmployeeDetails).where(filter_condition))

            employee = result.scalars().first()

            if employee:
                return employee

        return None

    # =====================================================
    # CREATE EMPLOYEE
    # =====================================================

    async def create_employee(self, db: AsyncSession, employee: EmployeeDetails):

        db.add(employee)

        await db.flush()

        await db.refresh(employee)

        return employee

    # =====================================================
    # GET EMPLOYEE
    # =====================================================

    async def get_employee_by_uuid(self, db: AsyncSession, employee_uuid: str):

        result = await db.execute(
            select(EmployeeDetails).where(
                EmployeeDetails.employee_uuid == employee_uuid
            )
        )

        return result.scalars().first()

    # =====================================================
    # UPDATE EMPLOYEE
    # =====================================================

    async def update_employee(self, db: AsyncSession, employee: EmployeeDetails):

        await db.flush()

        await db.refresh(employee)

        return employee

    # =====================================================
    # GET ALL EMPLOYEES
    # =====================================================

    async def get_all_employees(self, db: AsyncSession):

        query = text("""
            SELECT
                ed.user_uuid,
                ed.employee_uuid,
                ed.employee_id,
                ed.first_name,
                ed.middle_name,
                ed.last_name,
                ed.date_of_birth,
                ed.work_email,
                ed.contact_number,
                ed.department_uuid,
                ed.designation_uuid,
                ed.reporting_manager_uuid,
                ed.employment_type,
                ed.joining_date,
                ed.location,
                ed.work_mode,
                ed.employment_status,
                ed.blood_group,
                ed.gender,
                ed.marital_status,
                ed.bgv_status,
                CASE
                    WHEN COUNT(bc.check_uuid) = 0 THEN 'PENDING'
                    WHEN SUM(CASE WHEN bc.status = 'VERIFIED'  THEN 1 ELSE 0 END) = COUNT(bc.check_uuid) THEN 'VERIFIED'
                    WHEN SUM(CASE WHEN bc.status = 'REJECTED'  THEN 1 ELSE 0 END) > 0 THEN 'REJECTED'
                    WHEN SUM(CASE WHEN bc.status IN ('IN_REVIEW', 'VERIFIED') THEN 1 ELSE 0 END) > 0 THEN 'IN_REVIEW'
                    ELSE 'PENDING'
                END AS bg_status
            FROM employee_details ed
            LEFT JOIN background_checks bc
                ON bc.user_uuid = ed.user_uuid
                AND (bc.check_type NOT LIKE '__session__%' AND bc.check_type NOT LIKE '__hidden__%')
            GROUP BY
                ed.user_uuid, ed.employee_uuid, ed.employee_id,
                ed.first_name, ed.middle_name, ed.last_name,
                ed.date_of_birth, ed.work_email, ed.contact_number,
                ed.department_uuid, ed.designation_uuid, ed.reporting_manager_uuid,
                ed.employment_type, ed.joining_date, ed.location, ed.work_mode,
                ed.employment_status, ed.blood_group, ed.gender, ed.marital_status,
                ed.bgv_status
        """)

        result = await db.execute(query)

        return result.mappings().all()

    # =====================================================
    # DELETE EMPLOYEE
    # =====================================================

    async def delete_employee(self, db: AsyncSession, employee_uuid: str):

        employee = await self.get_employee_by_uuid(db, employee_uuid)

        if not employee:
            raise ValueError("Employee not found")

        await db.delete(employee)

        await db.flush()

    # =====================================================
    # DUPLICATE VALIDATIONS
    # =====================================================

    async def check_employee_id_exists(self, db, employee_id):

        query = text("""
            SELECT employee_id
            FROM employee_details
            WHERE employee_id = employee_id
            LIMIT 1
        """)

        result = await db.execute(query, {"employee_id": employee_id})

        return result.scalar() is not None

    async def check_work_email_exists(self, db, work_email):

        query = text("""
            SELECT work_email
            FROM employee_details
            WHERE work_email = :work_email

            UNION

            SELECT mail
            FROM offer_letter_details
            WHERE mail = :work_email

            LIMIT 1
        """)

        result = await db.execute(query, {"work_email": work_email})

        return result.scalar() is not None

    # =====================================================
    # DEPARTMENTS
    # =====================================================

    async def get_departments(self, db):

        query = text("""
            SELECT department_uuid, department_name
            FROM departments
            ORDER BY department_name
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

    # =====================================================
    # DESIGNATIONS
    # =====================================================

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

    async def get_designation_uuid(self, db, designation_name):

        query = text("""
            SELECT designation_uuid
            FROM designations
            WHERE designation_name = :name
        """)

        result = await db.execute(query, {"name": designation_name})

        return result.scalar()

    # =====================================================
    # COUNTRY CODES
    # =====================================================

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

    async def get_country_uuid_by_calling_code(self, db, calling_code):

        if not calling_code:
            return None

        cleaned_code = str(calling_code).replace("+", "").strip()

        query = text("""
            SELECT country_uuid
            FROM countries
            WHERE REPLACE(calling_code, '+', '')
            = :calling_code
            LIMIT 1
        """)

        result = await db.execute(query, {"calling_code": cleaned_code})

        return result.scalar()

    # =====================================================
    # EMPLOYEE DROPDOWN
    # =====================================================

    async def get_employees_for_dropdown(self, db):

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

    # =====================================================
    # OFFER LETTER
    # =====================================================

    async def insert_offer_letter(
        self, db, row, user_uuid, uploaded_by, reporting_manager_employee_id
    ):

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

    # =====================================================
    # EMPLOYEE
    # =====================================================

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
        uploaded_by,
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

    # =====================================================
    # PERSONAL DETAILS
    # =====================================================

    async def insert_personal_details(self, db, personal_uuid, user_uuid, row):

        query = text("""
            INSERT INTO personal_details (
                personal_uuid,
                user_uuid,
                date_of_birth,
                gender,
                marital_status,
                blood_group,
                nationality_country_uuid,
                residence_country_uuid,
                emergency_contact_name,
                emergency_contact_phone,
                emergency_contact_relation_uuid,
                status,
                created_at,
                updated_at
            )
            VALUES (
                :personal_uuid,
                :user_uuid,
                :date_of_birth,
                :gender,
                :marital_status,
                :blood_group,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                'uploaded',
                NOW(),
                NOW()
            )
        """)

        values = {
            "personal_uuid": personal_uuid,
            "user_uuid": user_uuid,
            "date_of_birth": row.get("date_of_birth"),
            "gender": row.get("gender"),
            "marital_status": row.get("marital_status"),
            "blood_group": row.get("blood_group"),
        }

        await db.execute(query, values)

    # =====================================================
    # BANK DETAILS
    # =====================================================

    async def insert_bank_details(self, db, bank_uuid, user_uuid):

        query = text("""
            INSERT INTO employee_bank_details (
                bank_uuid,
                user_uuid,
                account_holder_name,
                bank_name,
                branch_name,
                account_number,
                ifsc_code,
                account_type,
                status,
                created_at
            )
            VALUES (
                :bank_uuid,
                :user_uuid,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                'uploaded',
                NOW()
            )
        """)

        values = {
            "bank_uuid": bank_uuid,
            "user_uuid": user_uuid,
        }

        await db.execute(query, values)

    # =====================================================
    # PF DETAILS
    # =====================================================

    async def insert_pf_details(self, db, pf_uuid, user_uuid):

        query = text("""
            INSERT INTO employee_pf_details (
                pf_uuid,
                user_uuid,
                pf_member,
                uan_number,
                status,
                created_at
            )
            VALUES (
                :pf_uuid,
                :user_uuid,
                NULL,
                NULL,
                'uploaded',
                NOW()
            )
        """)

        values = {
            "pf_uuid": pf_uuid,
            "user_uuid": user_uuid,
        }

        await db.execute(query, values)

    # =====================================================
    # ADDRESS
    # =====================================================

    async def insert_address(
        self, db, address_uuid, user_uuid, address_type, country_uuid
    ):

        query = text("""
            INSERT INTO addresses (
                address_uuid,
                user_uuid,
                address_type,
                address_line1,
                country_uuid,
                address_line2,
                city,
                district_or_ward,
                state_or_region,
                postal_code,
                status,
                created_at,
                updated_at
            )
            VALUES (
                :address_uuid,
                :user_uuid,
                :address_type,
                NULL,
                :country_uuid,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                'uploaded',
                NOW(),
                NOW()
            )
        """)

        values = {
            "address_uuid": address_uuid,
            "user_uuid": user_uuid,
            "address_type": address_type,
            "country_uuid": country_uuid,
        }

        await db.execute(query, values)
