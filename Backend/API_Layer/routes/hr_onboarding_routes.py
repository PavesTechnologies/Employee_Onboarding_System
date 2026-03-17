

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import unquote

from ...Business_Layer.services.hr_onboarding_service import (HrOnboardingService)
from ...API_Layer.interfaces.candidate_submit_forms_interfaces import HrOnboardingSubmitRequest
from ...API_Layer.interfaces.hr_onboarding_interfaces import HRVerificationRequest
from ..utils.role_based import require_roles
from sqlalchemy.future import select
from Backend.DAL.utils.dependencies import get_db
from Backend.DAL.models.models import OfferLetterDetails, EmployeeDetails

router = APIRouter()

def extract_experience_documents(experience_data):
    experience_docs = []

    for exp in experience_data:
        for doc in exp.get("documents", []):
            experience_docs.append({
                "company_name": exp.get("company_name"),
                "doc_type": doc.get("doc_type"),
                "file_path": doc.get("file_path")
            })

    return experience_docs


@router.get("/hr/{user_uuid}")
async def get_full_onboarding_details(user_uuid: str, request: Request, db: AsyncSession = Depends(get_db)):
    current_user_id = int(request.state.user.get("user_id"))
    service = HrOnboardingService(db)
    data = await service.get_full_onboarding_details(user_uuid, current_user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User onboarding data not found")
    return data


@router.post("/candidate/submit")
async def submit_onboarding(
    payload: HrOnboardingSubmitRequest,
    db: AsyncSession = Depends(get_db)
):
    service = HrOnboardingService(db)

    await service.final_submit_onboarding(payload.user_uuid)
    return {"message": "Onboarding submitted successfully"}


@router.get("/view_documents", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def view_onboarding_documents(file_path: str, db: AsyncSession = Depends(get_db)):
    try:
        file_path = unquote(file_path)
        print("route file path:", file_path)
        service = HrOnboardingService(db)
        document_url = await service.view_onboarding_documents(file_path)
        return  document_url
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
          
@router.post("/verify-profile", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def verify_employee_profile(
    payload: HRVerificationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    HR verifies or rejects an employee profile
    """
    current_user_id = int(request.state.user.get("user_id"))

    service = HrOnboardingService(db)

    await service.update_verification_status(
        user_uuid=payload.user_uuid,
        status=payload.status,
        current_user_id=current_user_id
    )

    return {
        "message": "Verification status updated successfully"
    }

# @router.get("/employees/documents")
# async def get_all_employee_documents(
#     request: Request,
#     db: AsyncSession = Depends(get_db)
# ):

#     current_user_id = int(request.state.user.get("user_id"))

#     employees_result = await db.execute(select(OfferLetterDetails))
#     employees = employees_result.scalars().all()

#     service = HrOnboardingService(db)

#     results = []

#     for emp in employees:

#         onboarding_data = await service.get_full_onboarding_details(
#             emp.user_uuid,
#             current_user_id
#         )

#         if not onboarding_data:
#             continue

#         identity_docs = onboarding_data.get("identity_documents", [])
#         education_docs = onboarding_data.get("education_documents", [])
#         experience_data = onboarding_data.get("experience", [])

#         experience_docs = []

#         for exp in experience_data:
#             for doc in exp.get("documents", []):
#                 experience_docs.append({
#                     "company_name": exp.get("company_name"),
#                     "doc_type": doc.get("doc_type"),
#                     "file_path": doc.get("file_path")
#                 })

#         results.append({
#             "user_uuid": emp.user_uuid,
#             "name": f"{emp.first_name} {emp.last_name}",
#             "identity_documents": identity_docs,
#             "education_documents": education_docs,
#             "experience_documents": experience_docs
#         })

#     return results


@router.get("/employees/documents")
async def get_all_employee_documents(
    request: Request,
    db: AsyncSession = Depends(get_db)
):

    current_user_id = int(request.state.user.get("user_id"))

    # JOIN OfferLetterDetails + CoreEmployee
    employees_query = await db.execute(
        select(OfferLetterDetails, EmployeeDetails.employee_id)
        .outerjoin(EmployeeDetails, EmployeeDetails.user_uuid == OfferLetterDetails.user_uuid)
    )

    employees = employees_query.all()

    service = HrOnboardingService(db)

    results = []

    for emp, employee_id in employees:

        onboarding_data = await service.get_full_onboarding_details(
            emp.user_uuid,
            current_user_id
        )

        if not onboarding_data:
            continue

        documents = []

        # Identity Documents
        for doc in onboarding_data.get("identity_documents", []):
            documents.append({
                "document_name": doc.get("identity_type"),
                "file_path": doc.get("file_path")
            })

        # Education Documents
        for doc in onboarding_data.get("education_documents", []):
            documents.append({
                "document_name": doc.get("document_name") or "Education Document",
                "file_path": doc.get("file_path")
            })

        # Experience Documents
        for exp in onboarding_data.get("experience", []):
            for doc in exp.get("documents", []):
                documents.append({
                    "document_name": doc.get("doc_type"),
                    "file_path": doc.get("file_path")
                })

        results.append({
            "user_uuid": emp.user_uuid,
            "emp_id": employee_id,  # ✅ fetched from CoreEmployee
            "name": f"{emp.first_name} {emp.last_name}",
            "department": emp.designation,
            "documents": documents
        })

    return results

@router.get("/employee/{user_uuid}/documents")
async def get_employee_documents(
    user_uuid: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):

    current_user_id = int(request.state.user.get("user_id"))

    service = HrOnboardingService(db)

    onboarding_data = await service.get_full_onboarding_details(
        user_uuid,
        current_user_id
    )

    if not onboarding_data:
        raise HTTPException(status_code=404, detail="Onboarding data not found")

    documents = []

    # Identity Documents
    for doc in onboarding_data.get("identity_documents", []):
        documents.append({
            "document_name": doc.get("identity_type"),
            "file_path": doc.get("file_path")
        })

    # Education Documents
    for doc in onboarding_data.get("education_documents", []):
        documents.append({
            "document_name": doc.get("document_name") or "Education Document",
            "file_path": doc.get("file_path")
        })

    # Experience Documents
    for exp in onboarding_data.get("experience", []):
        for doc in exp.get("documents", []):
            documents.append({
                "document_name": doc.get("doc_type"),
                "file_path": doc.get("file_path")
            })

    return {
        "user_uuid": user_uuid,
        "documents": documents
    }
# @router.get("/employee/{user_uuid}/documents")
# async def get_employee_documents(
#     user_uuid: str,
#     request: Request,
#     db: AsyncSession = Depends(get_db)
# ):

#     current_user_id = int(request.state.user.get("user_id"))

#     service = HrOnboardingService(db)

#     onboarding_data = await service.get_full_onboarding_details(
#         user_uuid,
#         current_user_id
#     )

#     if not onboarding_data:
#         raise HTTPException(status_code=404, detail="Onboarding data not found")

#     identity_docs = onboarding_data.get("identity_documents", [])
#     education_docs = onboarding_data.get("education_documents", [])
#     experience_data = onboarding_data.get("experience", [])

#     experience_docs = []

#     for exp in experience_data:
#         for doc in exp.get("documents", []):
#             experience_docs.append({
#                 "company_name": exp.get("company_name"),
#                 "doc_type": doc.get("doc_type"),
#                 "file_path": doc.get("file_path")
#             })

#     return {
#         "user_uuid": user_uuid,
#         "identity_documents": identity_docs,
#         "education_documents": education_docs,
#         "experience_documents": experience_docs
#     }