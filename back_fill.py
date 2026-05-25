# =========================================================
# BACKFILL SCRIPT
# Creates Missing Records For Old Employees
# =========================================================

from sqlalchemy import text
from Backend.Business_Layer.utils.uuid_generator import generate_uuid7
async def backfill_old_employee_records(db):

    try:

        # =====================================================
        # GET ALL EMPLOYEES
        # =====================================================

        employees_query = text("""
            SELECT
                ed.user_uuid,
                old.country_code
            FROM employee_details ed

            LEFT JOIN offer_letter_details old
                ON old.user_uuid = ed.user_uuid

            WHERE ed.user_uuid IS NOT NULL
        """)

        employees_result = await db.execute(
            employees_query
        )

        employees = employees_result.fetchall()

        success_count = 0

        failed_records = []

        # =====================================================
        # LOOP EMPLOYEES
        # =====================================================

        for emp in employees:

            try:

                user_uuid = emp[0]

                country_code = emp[1]

                # =============================================
                # GET COUNTRY UUID
                # =============================================

                country_uuid = None

                if country_code:

                    cleaned_code = str(country_code)\
                        .replace("+", "")\
                        .strip()

                    country_query = text("""
                        SELECT country_uuid
                        FROM countries
                        WHERE REPLACE(calling_code, '+', '')
                        = :calling_code
                        LIMIT 1
                    """)

                    country_result = await db.execute(
                        country_query,
                        {
                            "calling_code":
                                cleaned_code
                        }
                    )

                    country_uuid = (
                        country_result.scalar()
                    )

                async with db.begin_nested():

                    # =================================================
                    # PERSONAL DETAILS
                    # =================================================

                    personal_exists_query = text("""
                        SELECT personal_uuid
                        FROM personal_details
                        WHERE user_uuid = :user_uuid
                        LIMIT 1
                    """)

                    personal_exists = await db.execute(
                        personal_exists_query,
                        {
                            "user_uuid":
                                user_uuid
                        }
                    )

                    personal_record = (
                        personal_exists.scalar()
                    )

                    if not personal_record:

                        insert_personal_query = text("""
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
                                NULL,
                                NULL,
                                NULL,
                                NULL,
                                :nationality_country_uuid,
                                :residence_country_uuid,
                                NULL,
                                NULL,
                                NULL,
                                'uploaded',
                                NOW(),
                                NOW()
                            )
                        """)

                        await db.execute(
                            insert_personal_query,
                            {
                                "personal_uuid":
                                    str(generate_uuid7()),

                                "user_uuid":
                                    user_uuid,

                                "nationality_country_uuid":
                                    country_uuid,

                                "residence_country_uuid":
                                    country_uuid,
                            }
                        )

                    else:

                        update_personal_query = text("""
                            UPDATE personal_details
                            SET
                                nationality_country_uuid =
                                    COALESCE(
                                        nationality_country_uuid,
                                        :country_uuid
                                    ),

                                residence_country_uuid =
                                    COALESCE(
                                        residence_country_uuid,
                                        :country_uuid
                                    ),

                                updated_at = NOW()

                            WHERE user_uuid = :user_uuid
                        """)

                        await db.execute(
                            update_personal_query,
                            {
                                "country_uuid":
                                    country_uuid,

                                "user_uuid":
                                    user_uuid,
                            }
                        )

                    # =================================================
                    # BANK DETAILS
                    # =================================================

                    bank_exists_query = text("""
                        SELECT bank_uuid
                        FROM employee_bank_details
                        WHERE user_uuid = :user_uuid
                        LIMIT 1
                    """)

                    bank_exists = await db.execute(
                        bank_exists_query,
                        {
                            "user_uuid":
                                user_uuid
                        }
                    )

                    if not bank_exists.scalar():

                        insert_bank_query = text("""
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

                        await db.execute(
                            insert_bank_query,
                            {
                                "bank_uuid":
                                    str(generate_uuid7()),

                                "user_uuid":
                                    user_uuid,
                            }
                        )

                    # =================================================
                    # PF DETAILS
                    # =================================================

                    pf_exists_query = text("""
                        SELECT pf_uuid
                        FROM employee_pf_details
                        WHERE user_uuid = :user_uuid
                        LIMIT 1
                    """)

                    pf_exists = await db.execute(
                        pf_exists_query,
                        {
                            "user_uuid":
                                user_uuid
                        }
                    )

                    if not pf_exists.scalar():

                        insert_pf_query = text("""
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

                        await db.execute(
                            insert_pf_query,
                            {
                                "pf_uuid":
                                    str(generate_uuid7()),

                                "user_uuid":
                                    user_uuid,
                            }
                        )

                    # =================================================
                    # CURRENT ADDRESS
                    # =================================================

                    current_address_query = text("""
                        SELECT address_uuid
                        FROM addresses
                        WHERE user_uuid = :user_uuid
                        AND address_type = 'current'
                        LIMIT 1
                    """)

                    current_address_exists = await db.execute(
                        current_address_query,
                        {
                            "user_uuid":
                                user_uuid
                        }
                    )

                    if not current_address_exists.scalar():

                        insert_current_query = text("""
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
                                'current',
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

                        await db.execute(
                            insert_current_query,
                            {
                                "address_uuid":
                                    str(generate_uuid7()),

                                "user_uuid":
                                    user_uuid,

                                "country_uuid":
                                    country_uuid,
                            }
                        )

                    # =================================================
                    # PERMANENT ADDRESS
                    # =================================================

                    permanent_address_query = text("""
                        SELECT address_uuid
                        FROM addresses
                        WHERE user_uuid = :user_uuid
                        AND address_type = 'permanent'
                        LIMIT 1
                    """)

                    permanent_address_exists = await db.execute(
                        permanent_address_query,
                        {
                            "user_uuid":
                                user_uuid
                        }
                    )

                    if not permanent_address_exists.scalar():

                        insert_permanent_query = text("""
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
                                'permanent',
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

                        await db.execute(
                            insert_permanent_query,
                            {
                                "address_uuid":
                                    str(generate_uuid7()),

                                "user_uuid":
                                    user_uuid,

                                "country_uuid":
                                    country_uuid,
                            }
                        )

                success_count += 1

            except Exception as e:

                failed_records.append({
                    "user_uuid": user_uuid,
                    "reason": str(e)
                })

        # =====================================================
        # FINAL COMMIT
        # =====================================================

        await db.commit()

        return {

            "message":
                "Old employee records backfilled successfully",

            "success_count":
                success_count,

            "failed_count":
                len(failed_records),

            "failed_records":
                failed_records,
        }

    except Exception as e:

        await db.rollback()

        raise Exception(
            f"Backfill failed: {str(e)}"
        )