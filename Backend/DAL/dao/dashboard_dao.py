import calendar

from sqlalchemy import select, func, case, and_, or_, tuple_
from datetime import date, datetime, timedelta

from Backend.DAL.models.models import (
    OfferLetterDetails,
    PersonalDetails,
    Addresses,
    EmployeeEducationDocument,
    EmployeeIdentityDocument,
    EmployeeExperience,
    EmployeeBankDetails,
    EmployeePfDetails,
    EmployeeDetails
)


class DashboardDAO:

    def __init__(self, db):
        self.db = db

    async def get_dashboard_summary(self, start_date=None, end_date=None):

        # =========================
        # 1. OFFER COUNTS (SINGLE QUERY)
        # =========================
        counts_query = await self.db.execute(
            select(
                func.count().label("total"),

                func.sum(case((OfferLetterDetails.status == "Created", 1), else_=0)).label("created"),
                func.sum(case((OfferLetterDetails.status == "Offered", 1), else_=0)).label("offered"),
                func.sum(case((OfferLetterDetails.status == "Accepted", 1), else_=0)).label("accepted"),
                func.sum(case((OfferLetterDetails.status == "Submitted", 1), else_=0)).label("submitted"),
                func.sum(case((OfferLetterDetails.status == "Verified", 1), else_=0)).label("verified"),
                func.sum(case((OfferLetterDetails.status == "Rejected", 1), else_=0)).label("rejected"),
            )
        )

        result = counts_query.one()

        total = result.total or 0
        created = result.created or 0
        offered = result.offered or 0
        accepted = result.accepted or 0
        submitted = result.submitted or 0
        verified = result.verified or 0
        rejected = result.rejected or 0

        # =========================
        # 2. COMPLETED
        # =========================
        completed_result = await self.db.execute(
            select(func.count(EmployeeDetails.employee_id))
        )
        completed = completed_result.scalar() or 0

        # =========================
        # 3. SAFE PIPELINE
        # =========================
        offered = min(offered, total)
        accepted = min(accepted, offered)

        # =========================
        # 4. PENDING ACTIONS
        # =========================
        pending_verification = submitted
        pending_documents = max(accepted - submitted, 0)
        pending_joining = max(verified - completed, 0)

        # =========================
        # 5. METRICS
        # =========================
        acceptance_rate = (accepted / offered * 100) if offered else 0
        completion_rate = (completed / total * 100) if total else 0
        drop_off_rate = (rejected / total * 100) if total else 0

        # =========================
        # 6. DOCUMENT COUNTS (OPTIMIZED)
        # =========================

        personal_result = await self.db.execute(
            select(func.count(func.distinct(PersonalDetails.user_uuid)))
            .where(PersonalDetails.status == "verified")
        )
        personal_count = personal_result.scalar() or 0

        address_result = await self.db.execute(
            select(func.count(func.distinct(Addresses.user_uuid)))
            .where(Addresses.status == "verified")
        )
        address_count = address_result.scalar() or 0

        education_result = await self.db.execute(
            select(func.count(func.distinct(EmployeeEducationDocument.user_uuid)))
            .where(EmployeeEducationDocument.status == "verified")
        )
        education_count = education_result.scalar() or 0

        identity_result = await self.db.execute(
            select(func.count(func.distinct(EmployeeIdentityDocument.user_uuid)))
            .where(EmployeeIdentityDocument.status == "verified")
        )
        identity_count = identity_result.scalar() or 0

        experience_result = await self.db.execute(
            select(func.count(func.distinct(EmployeeExperience.employee_uuid)))
            .where(EmployeeExperience.status == "verified")
        )
        experience_count = experience_result.scalar() or 0

        bank_result = await self.db.execute(
            select(func.count(func.distinct(EmployeeBankDetails.user_uuid)))
            .where(EmployeeBankDetails.status == "verified")
        )
        bank_count = bank_result.scalar() or 0

        pf_result = await self.db.execute(
            select(func.count(func.distinct(EmployeePfDetails.user_uuid)))
            .where(EmployeePfDetails.status == "verified")
        )
        pf_count = pf_result.scalar() or 0

        total_candidates = total

        def percent(val):
            return round((val / total_candidates) * 100, 2) if total_candidates else 0

        documents = {
            "personal": {"completed": personal_count, "total": total_candidates, "percentage": percent(personal_count)},
            "address": {"completed": address_count, "total": total_candidates, "percentage": percent(address_count)},
            "education": {"completed": education_count, "total": total_candidates, "percentage": percent(education_count)},
            "identity": {"completed": identity_count, "total": total_candidates, "percentage": percent(identity_count)},
            "experience": {"completed": experience_count, "total": total_candidates, "percentage": percent(experience_count)},
            "bank": {"completed": bank_count, "total": total_candidates, "percentage": percent(bank_count)},
            "pf": {"completed": pf_count, "total": total_candidates, "percentage": percent(pf_count)}
        }

        # =========================
        # 7. AGING
        # =========================
        now = datetime.utcnow()

        aging3_result = await self.db.execute(
            select(func.count()).where(
                OfferLetterDetails.created_at < now - timedelta(days=3)
            )
        )
        aging3 = aging3_result.scalar() or 0

        aging7_result = await self.db.execute(
            select(func.count()).where(
                OfferLetterDetails.created_at < now - timedelta(days=7)
            )
        )
        aging7 = aging7_result.scalar() or 0

        # =========================
        # 8. RECENT ACTIVITY
        # =========================
        recent_result = await self.db.execute(
            select(OfferLetterDetails)
            .order_by(OfferLetterDetails.updated_at.desc())
            .limit(5)
        )

        action_map = {
            "Created": "Offer Created",
            "Offered": "Offer Sent",
            "Accepted": "Offer Accepted",
            "Submitted": "Documents Submitted",
            "Verified": "Profile Verified"
        }

        recent_activity = [
            {
                "user_uuid": r.user_uuid,
                "name": f"{r.first_name} {r.last_name}",
                "action": action_map.get(r.status, r.status),
                "timestamp": str(r.updated_at or r.created_at)
            }
            for r in recent_result.scalars().all()
        ]

        # =========================
        # FINAL RESPONSE
        # =========================
        return {
            "overview": {
                "total_candidates": total,
                "offers_created": created,
                "offers_offered": offered,
                "offers_accepted": accepted,
                "offers_submitted": submitted,
                "offers_verified": verified,
                "offers_rejected": rejected
            },
            "pipeline": {
                "created": created,
                "offered": offered,
                "accepted": accepted,
                "submitted": submitted,
                "verified": verified
                
            },
            "pending_actions": {
                "pending_verification": pending_verification,
                "pending_documents": pending_documents,
                "pending_joining": pending_joining
            },
            "metrics": {
                "acceptance_rate": f"{round(acceptance_rate, 2)}%",
                "completion_rate": f"{round(completion_rate, 2)}%",
                "drop_off_rate": f"{round(drop_off_rate, 2)}%"
            },
            "documents": documents,
            "aging": {
                "pending_3_days": aging3,
                "pending_7_days": aging7
            },
            "recent_activity": recent_activity
        }

    async def get_celebrations(self, start_date: date, end_date: date):
        active_statuses = ("Probation", "Active", "On-Notice")

        birthdays_result = await self.db.execute(
            select(EmployeeDetails)
            .where(
                EmployeeDetails.date_of_birth.is_not(None),
                EmployeeDetails.employment_status.in_(active_statuses),
                self._date_month_day_filter(
                    EmployeeDetails.date_of_birth,
                    start_date,
                    end_date
                )
            )
            .order_by(
                func.month(EmployeeDetails.date_of_birth),
                func.day(EmployeeDetails.date_of_birth),
                EmployeeDetails.first_name
            )
        )

        anniversaries_result = await self.db.execute(
            select(EmployeeDetails)
            .where(
                EmployeeDetails.joining_date.is_not(None),
                EmployeeDetails.employment_status.in_(active_statuses),
                EmployeeDetails.joining_date < start_date,
                self._date_month_day_filter(
                    EmployeeDetails.joining_date,
                    start_date,
                    end_date
                )
            )
            .order_by(
                func.month(EmployeeDetails.joining_date),
                func.day(EmployeeDetails.joining_date),
                EmployeeDetails.first_name
            )
        )

        new_joinees_result = await self.db.execute(
            select(EmployeeDetails)
            .where(
                EmployeeDetails.joining_date.is_not(None),
                EmployeeDetails.employment_status.in_(active_statuses),
                EmployeeDetails.joining_date.between(start_date, end_date)
            )
            .order_by(EmployeeDetails.joining_date, EmployeeDetails.first_name)
        )

        return {
            "birthdays": [
                self._format_celebration_item(
                    employee,
                    self._get_celebration_date(
                        employee.date_of_birth,
                        start_date,
                        end_date
                    )
                )
                for employee in birthdays_result.scalars().all()
            ],
            "workAnniversaries": [
                self._format_work_anniversary_item(
                    employee,
                    start_date,
                    end_date
                )
                for employee in anniversaries_result.scalars().all()
            ],
            "newJoinees": [
                self._format_celebration_item(employee, employee.joining_date)
                for employee in new_joinees_result.scalars().all()
            ]
        }

    def _date_month_day_filter(self, column, start_date: date, end_date: date):
        start_month_day = (start_date.month, start_date.day)
        end_month_day = (end_date.month, end_date.day)
        column_month_day = tuple_(func.month(column), func.day(column))

        if start_month_day <= end_month_day:
            return and_(
                column_month_day >= start_month_day,
                column_month_day <= end_month_day
            )

        return or_(
            column_month_day >= start_month_day,
            column_month_day <= end_month_day
        )

    def _format_celebration_item(self, employee, event_date):
        return {
            "name": " ".join(
                part for part in [
                    employee.first_name,
                    employee.middle_name,
                    employee.last_name
                ]
                if part
            ),
            "date": event_date.strftime("%d/%m/%y")
        }

    def _format_work_anniversary_item(self, employee, start_date: date, end_date: date):
        anniversary_date = self._get_celebration_date(
            employee.joining_date,
            start_date,
            end_date
        )

        return {
            **self._format_celebration_item(employee, anniversary_date),
            "anniversaryYear": anniversary_date.year - employee.joining_date.year
        }

    def _get_celebration_date(self, original_date: date, start_date: date, end_date: date):
        occurrence_year = start_date.year
        if (original_date.month, original_date.day) < (start_date.month, start_date.day):
            occurrence_year = end_date.year

        last_day = calendar.monthrange(occurrence_year, original_date.month)[1]
        occurrence_day = min(original_date.day, last_day)

        return date(occurrence_year, original_date.month, occurrence_day)
