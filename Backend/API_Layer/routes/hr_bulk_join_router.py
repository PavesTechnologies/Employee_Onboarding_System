from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.dao.hr_bulk_join_dao import HrBulkJoinDAO
from ...DAL.utils.dependencies import get_db
from  ...API_Layer.interfaces.bulk_join_request_interfaces import BulkJoinRequest,ReassignJoiningRequest
from ...Business_Layer.services.hr_bulk_join_service import HrBulkJoinService
from ...Business_Layer.services.document_service import DocumentService
from ..utils.role_based import require_roles

router = APIRouter()

@router.post("/offerletters/bulk-join", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def bulk_join(
    payload: BulkJoinRequest,
    request: Request,
    preview: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = HrBulkJoinService(db)

        if preview:
            pdf_path = await service.generate_bulk_join_preview(payload)

            return FileResponse(
                pdf_path,
                media_type="application/pdf",
                filename="joining_letter_preview.pdf"
            )

        current_user_id = int(request.state.user.get("user_id"))
          
        result = await service.process_bulk_join(payload, current_user_id)

        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.put("/offerletters/reassign-joining", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def reassign_joining(
    payload: ReassignJoiningRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        current_user_id = int(request.state.user.get("user_id"))

        service = HrBulkJoinService(db)

        result = await service.reassign_joining(payload, current_user_id)

        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/offerletters/{user_uuid}")
async def get_offer_details(user_uuid: str, db: AsyncSession = Depends(get_db)):

    dao = HrBulkJoinDAO(db)
    user = await dao.get_user_by_uuid(user_uuid)

    if not user:
        raise HTTPException(404, "User not found")

    return {
        "user_uuid": user.user_uuid,
        "joining_date": user.joining_date,
        "reporting_manager": user.reporting_manager,
        "joining_comments": user.joining_comments,
        "status": user.status
    }


@router.get("/offerletters/{user_uuid}/joining-generate-preview", dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def generate_joining_preview(
    user_uuid: str,
    joining_date: date | None = Query(default=None),
    location: str = Query(...),
    reporting_time: str = Query(...),
    department: str = Query(...),
    reporting_manager: str = Query(...),
    custom_message: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    dao = HrBulkJoinDAO(db)
    user = await dao.get_user_by_uuid(user_uuid)

    if not user:
        raise HTTPException(404, "User not found")

    selected_joining_date = joining_date or user.joining_date
    if not selected_joining_date:
        raise HTTPException(400, "Joining date is required")

    service = HrBulkJoinService(db)
    manager = await service.resolve_reporting_manager(reporting_manager)

    joining_pdf_data = service.build_joining_pdf_data(
        user=user,
        joining_date=selected_joining_date,
        location=location,
        reporting_time=reporting_time,
        department=department,
        reporting_manager_name=manager["name"],
        custom_message=custom_message
    )

    pdf_path = DocumentService().generate_joining_pdf(joining_pdf_data)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"joining_letter_{user_uuid}.pdf"
    )
@router.get("/reporting-manager/{employee_id}/employees")
async def get_employees_under_manager(
    employee_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = HrBulkJoinService(db)

        employees = await service.get_employees_under_manager(employee_id)

        return {
            "employees": employees
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
