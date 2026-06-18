from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.API_Layer.interfaces.background_check_interfaces import (
    BackgroundCheckCreateRequest,
    BackgroundCheckMessageResponse,
    BackgroundCheckResponse,
    BackgroundCheckStatusUpdateRequest,
    BackgroundCheckUpdateRequest,
    EmployeeBgvStatusUpdateRequest,
    EmployeeBgvStatusUpdateResponse,
    FinalBGVDecisionRequest,
    FinalBGVDecisionResponse,
    SendToConsultancyRequest,
    SendToConsultancyResponse,
)
from Backend.Business_Layer.services.background_check_service import (
    BackgroundCheckService,
)
from Backend.Business_Layer.services.permanent_employee_details_service import (
    PermanentEmployeeDetailsService,
)
from Backend.DAL.utils.dependencies import get_db

router = APIRouter()


@router.get("/employee/{user_uuid}/profile")
async def get_employee_bgv_profile(
    user_uuid: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = BackgroundCheckService(db)
        return await service.get_bgv_profile(user_uuid)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/view")
async def view_bgv_document(
    file_path: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = BackgroundCheckService(db)
        return await service.view_document(file_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_uuid}", response_model=list[BackgroundCheckResponse])
async def get_hr_background_checks(
    user_uuid: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = BackgroundCheckService(db)
        return await service.get_checks_by_user_uuid(user_uuid)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{check_uuid}", response_model=BackgroundCheckResponse)
async def update_hr_background_check_status(
    check_uuid: str,
    request_data: BackgroundCheckStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = BackgroundCheckService(db)
        return await service.update_status(check_uuid, request_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=BackgroundCheckResponse)
async def create_hr_background_check(
    request_data: BackgroundCheckCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    try:
        raw_id = request.state.user.get("employee_id") or request.state.user.get("user_id")
        created_by = str(raw_id) if raw_id is not None else None
        print(f"[BGV] create_check created_by={created_by} | JWT keys={list(request.state.user.keys())}")
        service = BackgroundCheckService(db)
        return await service.create_check(request_data, created_by=created_by)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{check_uuid}", response_model=BackgroundCheckResponse)
async def update_hr_background_check(
    check_uuid: str,
    request_data: BackgroundCheckUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = BackgroundCheckService(db)
        return await service.update_check(check_uuid, request_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{check_uuid}", response_model=BackgroundCheckMessageResponse)
async def delete_hr_background_check(
    check_uuid: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = BackgroundCheckService(db)
        return await service.delete_check(check_uuid)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-to-consultancy", response_model=SendToConsultancyResponse)
async def send_hr_background_checks_to_consultancy(
    request_data: SendToConsultancyRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = BackgroundCheckService(db)
        return await service.send_to_consultancy(request_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/employee/{user_uuid}/bgv-status", response_model=EmployeeBgvStatusUpdateResponse)
async def update_employee_bgv_status(
    user_uuid: str,
    request_data: EmployeeBgvStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = PermanentEmployeeDetailsService()
        return await service.update_bgv_status(db, user_uuid, request_data.bgv_status.value)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/employee/{user_uuid}/final-decision", response_model=FinalBGVDecisionResponse)
async def submit_final_bgv_decision(
    user_uuid: str,
    request_data: FinalBGVDecisionRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    try:
        raw_id = request.state.user.get("employee_id") or request.state.user.get("user_id")
        decided_by = str(raw_id) if raw_id is not None else None
        service = BackgroundCheckService(db)
        return await service.final_decision(user_uuid, request_data, decided_by=decided_by)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
