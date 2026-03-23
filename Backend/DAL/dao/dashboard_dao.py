from sqlalchemy import select, func, case
from datetime import datetime, timedelta

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
        completion_rate = (completed / verified * 100) if verified else 0
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
                "verified": verified,
                "completed": completed
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