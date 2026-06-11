import calendar

from sqlalchemy import select, func, case, and_, or_, tuple_
from sqlalchemy.orm import aliased
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
    EmployeeDetails,
    Departments,
)

# Alias for self-join to resolve reporting manager name
ManagerEmployee = aliased(EmployeeDetails, name="manager_emp")


class DashboardDAO:

    def __init__(self, db):
        self.db = db

    async def get_dashboard_summary(self, start_date=None, end_date=None):

        # =========================
        # 1. OFFER COUNTS (single query)
        # =========================
        counts_query = await self.db.execute(
            select(
                func.count().label("total"),
                func.sum(
                    case((OfferLetterDetails.status == "Created", 1), else_=0)
                ).label("created"),
                func.sum(
                    case((OfferLetterDetails.status == "Offered", 1), else_=0)
                ).label("offered"),
                func.sum(
                    case((OfferLetterDetails.status == "Accepted", 1), else_=0)
                ).label("accepted"),
                func.sum(
                    case((OfferLetterDetails.status == "Submitted", 1), else_=0)
                ).label("submitted"),
                func.sum(
                    case((OfferLetterDetails.status == "Verified", 1), else_=0)
                ).label("verified"),
                func.sum(
                    case((OfferLetterDetails.status == "Rejected", 1), else_=0)
                ).label("rejected"),
                func.sum(
                    case((OfferLetterDetails.status == "Completed", 1), else_=0)
                ).label("completed"),
                func.sum(
                    case((OfferLetterDetails.status == "Rescheduled", 1), else_=0)
                ).label("rescheduled"),
                func.sum(
                    case((OfferLetterDetails.status == "Joining Pending", 1), else_=0)
                ).label("joining_pending"),
                func.sum(
                    case((OfferLetterDetails.status == "Joining", 1), else_=0)
                ).label("joining"),
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
        completed_offers = result.completed or 0
        rescheduled = result.rescheduled or 0
        joining_pending = result.joining_pending or 0
        joining = result.joining or 0

        # =========================
        # 2. COMPLETED EMPLOYEES (EmployeeDetails record = fully onboarded)
        # =========================
        completed_result = await self.db.execute(
            select(func.count(EmployeeDetails.employee_id))
        )
        completed = completed_result.scalar() or 0

        # =========================
        # 3. PENDING ACTIONS
        # =========================
        pending_verification = submitted
        pending_documents = max(accepted - submitted, 0)
        pending_joining = max(verified - completed, 0)

        # =========================
        # 5. METRICS
        # =========================
        # Cumulative acceptance: count every candidate who reached Accepted or beyond
        # (not just those currently sitting in "Accepted" status).
        candidates_ever_accepted = (
            accepted
            + submitted
            + verified
            + joining_pending
            + joining
            + rescheduled
            + completed_offers
        )
        # Candidates who were actually sent an offer (exclude "Created" — offer not sent yet)
        candidates_ever_offered = total - created

        acceptance_rate = (
            (candidates_ever_accepted / candidates_ever_offered * 100)
            if candidates_ever_offered
            else 0
        )
        completion_rate = (completed / total * 100) if total else 0
        drop_off_rate = (rejected / total * 100) if total else 0

        # =========================
        # 6. DOCUMENT VERIFICATION SUMMARY
        #    Distinct-user counts per type + row-level counts for aggregate summary
        # =========================
        doc_configs = [
            ("personal", PersonalDetails.user_uuid, PersonalDetails.status),
            ("address", Addresses.user_uuid, Addresses.status),
            (
                "education",
                EmployeeEducationDocument.user_uuid,
                EmployeeEducationDocument.status,
            ),
            (
                "identity",
                EmployeeIdentityDocument.user_uuid,
                EmployeeIdentityDocument.status,
            ),
            ("experience", EmployeeExperience.employee_uuid, EmployeeExperience.status),
            ("bank", EmployeeBankDetails.user_uuid, EmployeeBankDetails.status),
            ("pf", EmployeePfDetails.user_uuid, EmployeePfDetails.status),
        ]

        documents = {}
        total_distinct_verified = 0  # for overall_document_completion_percentage
        agg_verified_rows = 0  # for document_summary (row-level)
        agg_pending_rows = 0
        agg_rejected_rows = 0

        for doc_name, uuid_col, status_col in doc_configs:
            doc_result = await self.db.execute(
                select(
                    status_col.label("status"),
                    func.count(func.distinct(uuid_col)).label("distinct_cnt"),
                    func.count().label("row_cnt"),
                ).group_by(status_col)
            )
            distinct_stats: dict = {}
            row_stats: dict = {}
            for row in doc_result.all():
                key = row.status or "uploaded"
                distinct_stats[key] = row.distinct_cnt
                row_stats[key] = row.row_cnt

            v = distinct_stats.get("verified", 0)
            p = distinct_stats.get("uploaded", 0)
            r = distinct_stats.get("rejected", 0)

            documents[doc_name] = {
                "verified_count": v,
                "pending_count": p,
                "rejected_count": r,
                "total": total,
                "completion_percentage": round((v / total) * 100, 2) if total else 0,
            }

            total_distinct_verified += v
            agg_verified_rows += row_stats.get("verified", 0)
            agg_pending_rows += row_stats.get("uploaded", 0)
            agg_rejected_rows += row_stats.get("rejected", 0)

        # Overall % based on distinct users having every doc type verified
        overall_doc_pct = (
            round((total_distinct_verified / (total * len(doc_configs))) * 100, 2)
            if total
            else 0
        )

        # Aggregated document_summary (row-level totals across all types)
        doc_summary_total = agg_verified_rows + agg_pending_rows + agg_rejected_rows
        doc_summary_pct = (
            round((agg_verified_rows / doc_summary_total) * 100, 2)
            if doc_summary_total
            else 0
        )

        # =========================
        # 7. PROCESS DELAYS
        #    Only count candidates still in active stages (not Completed / Rejected).
        #    Use updated_at so a recently-touched candidate isn't flagged as delayed.
        # =========================
        now = datetime.utcnow()
        _active_statuses = (
            "Created",
            "Offered",
            "Accepted",
            "Submitted",
            "Verified",
            "Joining Pending",
            "Joining",
            "Rescheduled",
        )

        delayed_3_result = await self.db.execute(
            select(func.count()).where(
                OfferLetterDetails.status.in_(_active_statuses),
                OfferLetterDetails.updated_at < now - timedelta(days=3),
            )
        )
        delayed_3_days = delayed_3_result.scalar() or 0

        delayed_7_result = await self.db.execute(
            select(func.count()).where(
                OfferLetterDetails.status.in_(_active_statuses),
                OfferLetterDetails.updated_at < now - timedelta(days=7),
            )
        )
        delayed_7_days = delayed_7_result.scalar() or 0

        # =========================
        # 8. RECENT ACTIVITY
        #    Joins: EmployeeDetails → Departments, ManagerEmployee for manager name
        # =========================
        recent_result = await self.db.execute(
            select(
                OfferLetterDetails.user_uuid,
                OfferLetterDetails.first_name,
                OfferLetterDetails.last_name,
                OfferLetterDetails.status,
                OfferLetterDetails.designation,
                OfferLetterDetails.reporting_manager,
                OfferLetterDetails.joining_date,
                OfferLetterDetails.updated_at,
                OfferLetterDetails.created_at,
                Departments.department_name,
                ManagerEmployee.first_name.label("manager_first_name"),
                ManagerEmployee.last_name.label("manager_last_name"),
            )
            .select_from(OfferLetterDetails)
            .outerjoin(
                EmployeeDetails,
                EmployeeDetails.user_uuid == OfferLetterDetails.user_uuid,
            )
            .outerjoin(
                Departments,
                Departments.department_uuid == EmployeeDetails.department_uuid,
            )
            .outerjoin(
                ManagerEmployee,
                ManagerEmployee.employee_id == OfferLetterDetails.reporting_manager,
            )
            .order_by(OfferLetterDetails.updated_at.desc())
            .limit(10)
        )

        action_map = {
            "Created": "Offer Created",
            "Offered": "Offer Sent",
            "Accepted": "Offer Accepted",
            "Submitted": "Documents Submitted",
            "Verified": "Profile Verified",
            "Completed": "Onboarding Completed",
            "Joining Pending": "Awaiting Joining",
            "Joining": "Joining Initiated",
            "Rescheduled": "Joining Rescheduled",
            "Rejected": "Offer Rejected",
        }

        recent_activity = []
        for r in recent_result.all():
            mgr_name = (
                " ".join(
                    part for part in [r.manager_first_name, r.manager_last_name] if part
                ).strip()
                or "Not Assigned"
            )

            recent_activity.append(
                {
                    "user_uuid": r.user_uuid,
                    "candidate_name": f"{r.first_name or ''} {r.last_name or ''}".strip(),
                    "department": r.department_name or "Not Assigned",
                    "designation": r.designation or "Not Assigned",
                    # backward-compatible raw value
                    "reporting_manager": r.reporting_manager or "Not Assigned",
                    # new HR-friendly fields
                    "reporting_manager_id": r.reporting_manager or None,
                    "reporting_manager_name": mgr_name,
                    "joining_date": str(r.joining_date) if r.joining_date else None,
                    "current_status": r.status,
                    "activity_action": action_map.get(r.status, r.status),
                    "activity_timestamp": str(r.updated_at or r.created_at),
                }
            )

        # =========================
        # 9. DEPARTMENT SUMMARY (with percentage)
        # =========================
        dept_result = await self.db.execute(
            select(
                Departments.department_name,
                func.count(OfferLetterDetails.user_uuid).label("count"),
            )
            .select_from(OfferLetterDetails)
            .outerjoin(
                EmployeeDetails,
                EmployeeDetails.user_uuid == OfferLetterDetails.user_uuid,
            )
            .outerjoin(
                Departments,
                Departments.department_uuid == EmployeeDetails.department_uuid,
            )
            .group_by(Departments.department_name)
            .order_by(func.count(OfferLetterDetails.user_uuid).desc())
        )

        department_summary = [
            {
                "department": row.department_name or "Not Assigned",
                "count": row.count,
                "percentage": round((row.count / total) * 100, 2) if total else 0,
            }
            for row in dept_result.all()
        ]

        # =========================
        # 10. DERIVED SECTIONS (computed from already-fetched data)
        # =========================

        # Dashboard summary — mutually exclusive candidate buckets
        active_candidates = (
            created
            + offered
            + accepted
            + submitted
            + verified
            + joining_pending
            + joining
            + rescheduled
        )
        completed_candidates = completed_offers
        pending_candidates = rejected

        # Priority classification of each action item
        def _priority(
            count: int, high_threshold: int, medium_threshold: int = 1
        ) -> str:
            if count >= high_threshold:
                return "High"
            if count >= medium_threshold:
                return "Medium"
            return "Low"

        actions = [
            {
                "count": pending_verification,
                "priority": _priority(pending_verification, 6),
            },
            {
                "count": pending_joining,
                "priority": _priority(pending_joining, 4),
            },
            {
                "count": pending_documents,
                "priority": _priority(pending_documents, 1),
            },
        ]

        total_pending_actions = sum(a["count"] for a in actions)
        high_priority = sum(a["count"] for a in actions if a["priority"] == "High")
        medium_priority = sum(a["count"] for a in actions if a["priority"] == "Medium")
        low_priority = sum(a["count"] for a in actions if a["priority"] == "Low")

        # =========================
        # FINAL RESPONSE
        # =========================
        return {
            "dashboard_summary": {
                "total_candidates": total,
                "active_candidates": active_candidates,
                "completed_candidates": completed_candidates,
                "pending_candidates": pending_candidates,
            },
            "overview": {
                "total_candidates": total,
                "offer_management": {
                    "created": created,
                    "offered": offered,
                    "accepted": accepted,
                    "rejected": rejected,
                },
                "employee_onboarding": {
                    "submitted": submitted,
                    "verified": verified,
                    "completed": completed_offers,
                },
                "joining_process": {
                    "joining_pending": joining_pending,
                    "joining": joining,
                    "rescheduled": rescheduled,
                },
            },
            "pipeline": {
                "created": {
                    "count": created,
                    "label": "Created",
                    "description": "Candidates for whom offer letters have been generated",
                },
                "offered": {
                    "count": offered,
                    "label": "Offered",
                    "description": "Candidates to whom the offer letter has been sent",
                },
                "accepted": {
                    "count": accepted,
                    "label": "Accepted",
                    "description": "Candidates who have accepted the offer",
                },
                "submitted": {
                    "count": submitted,
                    "label": "Submitted",
                    "description": "Candidates who have submitted their onboarding documents",
                },
                "verified": {
                    "count": verified,
                    "label": "Verified",
                    "description": "Candidates whose documents have been verified by HR",
                },
                "completed": {
                    "count": completed_offers,
                    "label": "Completed",
                    "description": "Candidates who have completed the full onboarding process",
                },
            },
            "pending_actions": {
                "documents_pending_verification": {
                    "count": pending_verification,
                    "description": "Candidates who submitted documents awaiting HR verification",
                    "priority": actions[0]["priority"],
                },
                "candidates_awaiting_joining": {
                    "count": pending_joining,
                    "description": "Verified candidates yet to complete the joining process",
                    "priority": actions[1]["priority"],
                },
                "candidates_yet_to_submit": {
                    "count": pending_documents,
                    "description": "Accepted candidates who have not submitted their documents yet",
                    "priority": actions[2]["priority"],
                },
            },
            "action_required_summary": {
                "total_pending_actions": total_pending_actions,
                "high_priority": high_priority,
                "medium_priority": medium_priority,
                "low_priority": low_priority,
            },
            "metrics": {
                "offer_acceptance_success_rate": {
                    "value": f"{round(acceptance_rate, 2)}%",
                    "description": "Percentage of candidates who accepted the offer out of all offers sent (cumulative)",
                },
                "employee_onboarding_completion_rate": {
                    "value": f"{round(completion_rate, 2)}%",
                    "description": "Percentage of candidates who completed the full onboarding process",
                },
                "candidate_attrition_rate": {
                    "value": f"{round(drop_off_rate, 2)}%",
                    "description": "Percentage of candidates who rejected or dropped off during the process",
                },
            },
            "documents": documents,
            "document_summary": {
                "total_documents": doc_summary_total,
                "verified_documents": agg_verified_rows,
                "pending_documents": agg_pending_rows,
                "rejected_documents": agg_rejected_rows,
                "overall_completion_percentage": doc_summary_pct,
            },
            "overall_document_completion_percentage": overall_doc_pct,
            "process_delays": {
                "delayed_more_than_3_days": {
                    "count": delayed_3_days,
                    "description": "Candidates awaiting action for more than 3 days",
                },
                "delayed_more_than_7_days": {
                    "count": delayed_7_days,
                    "description": "Candidates awaiting action for more than 7 days",
                },
            },
            "department_summary": department_summary,
            "recent_activity": recent_activity,
        }

    async def get_celebrations(self, start_date: date, end_date: date):
        active_statuses = ("Probation", "Active", "On-Notice")

        birthdays_result = await self.db.execute(
            select(EmployeeDetails)
            .where(
                EmployeeDetails.date_of_birth.is_not(None),
                EmployeeDetails.employment_status.in_(active_statuses),
                self._date_month_day_filter(
                    EmployeeDetails.date_of_birth, start_date, end_date
                ),
            )
            .order_by(
                func.month(EmployeeDetails.date_of_birth),
                func.day(EmployeeDetails.date_of_birth),
                EmployeeDetails.first_name,
            )
        )

        anniversaries_result = await self.db.execute(
            select(EmployeeDetails)
            .where(
                EmployeeDetails.joining_date.is_not(None),
                EmployeeDetails.employment_status.in_(active_statuses),
                EmployeeDetails.joining_date < start_date,
                self._date_month_day_filter(
                    EmployeeDetails.joining_date, start_date, end_date
                ),
            )
            .order_by(
                func.month(EmployeeDetails.joining_date),
                func.day(EmployeeDetails.joining_date),
                EmployeeDetails.first_name,
            )
        )

        new_joinees_result = await self.db.execute(
            select(EmployeeDetails)
            .where(
                EmployeeDetails.joining_date.is_not(None),
                EmployeeDetails.employment_status.in_(active_statuses),
                EmployeeDetails.joining_date.between(start_date, end_date),
            )
            .order_by(EmployeeDetails.joining_date, EmployeeDetails.first_name)
        )

        return {
            "birthdays": [
                self._format_celebration_item(
                    employee,
                    self._get_celebration_date(
                        employee.date_of_birth, start_date, end_date
                    ),
                )
                for employee in birthdays_result.scalars().all()
            ],
            "workAnniversaries": [
                self._format_work_anniversary_item(employee, start_date, end_date)
                for employee in anniversaries_result.scalars().all()
            ],
            "newJoinees": [
                self._format_celebration_item(employee, employee.joining_date)
                for employee in new_joinees_result.scalars().all()
            ],
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _date_month_day_filter(self, column, start_date: date, end_date: date):
        start_month_day = (start_date.month, start_date.day)
        end_month_day = (end_date.month, end_date.day)
        column_month_day = tuple_(func.month(column), func.day(column))

        if start_month_day <= end_month_day:
            return and_(
                column_month_day >= start_month_day, column_month_day <= end_month_day
            )

        return or_(
            column_month_day >= start_month_day, column_month_day <= end_month_day
        )

    def _format_celebration_item(self, employee, event_date):
        return {
            "name": " ".join(
                part
                for part in [
                    employee.first_name,
                    employee.middle_name,
                    employee.last_name,
                ]
                if part
            ),
            "date": event_date.strftime("%d/%m/%y"),
        }

    def _format_work_anniversary_item(self, employee, start_date: date, end_date: date):
        anniversary_date = self._get_celebration_date(
            employee.joining_date, start_date, end_date
        )
        return {
            **self._format_celebration_item(employee, anniversary_date),
            "anniversaryYear": anniversary_date.year - employee.joining_date.year,
        }

    def _get_celebration_date(
        self, original_date: date, start_date: date, end_date: date
    ):
        occurrence_year = start_date.year
        if (original_date.month, original_date.day) < (
            start_date.month,
            start_date.day,
        ):
            occurrence_year = end_date.year

        last_day = calendar.monthrange(occurrence_year, original_date.month)[1]
        occurrence_day = min(original_date.day, last_day)

        return date(occurrence_year, original_date.month, occurrence_day)
