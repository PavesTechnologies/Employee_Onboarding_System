from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.API_Layer.interfaces.background_check_interfaces import (
    BackgroundCheckCreateRequest,
    BackgroundCheckDocumentMessageResponse,
    BackgroundCheckDocumentResponse,
    BackgroundCheckMessageResponse,
    BackgroundCheckResponse,
    BackgroundCheckStatusUpdateRequest,
    BackgroundCheckUpdateRequest,
)
from Backend.Business_Layer.services.background_check_service import (
    BackgroundCheckService,
)
from Backend.DAL.utils.dependencies import get_db

router = APIRouter()


@router.post("", response_model=BackgroundCheckResponse)
async def create_background_check(
    request_data: BackgroundCheckCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = BackgroundCheckService(db)
        return await service.create_check(request_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_uuid}", response_model=list[BackgroundCheckResponse])
async def get_background_checks_by_user(
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


@router.get("/{check_uuid}", response_model=BackgroundCheckResponse)
async def get_background_check(
    check_uuid: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = BackgroundCheckService(db)
        return await service.get_check_by_uuid(check_uuid)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{check_uuid}", response_model=BackgroundCheckResponse)
async def update_background_check(
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


@router.patch("/{check_uuid}/status", response_model=BackgroundCheckResponse)
async def update_background_check_status(
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


@router.delete("/{check_uuid}", response_model=BackgroundCheckMessageResponse)
async def delete_background_check(
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


@router.post("/documents", response_model=BackgroundCheckDocumentResponse)
async def upload_background_check_document(
    user_uuid: str = Form(...),
    category: str = Form(...),
    document_name: Optional[str] = Form(None),
    doc_type: Optional[str] = Form(None),
    uploaded_by: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        service = BackgroundCheckService(db)
        return await service.upload_document(
            user_uuid=user_uuid,
            category=category,
            document_name=document_name,
            doc_type=doc_type,
            uploaded_by=uploaded_by,
            file=file,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/user/{user_uuid}", response_model=list[BackgroundCheckDocumentResponse])
async def get_background_check_documents_by_user(
    user_uuid: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = BackgroundCheckService(db)
        return await service.get_documents_by_user_uuid(user_uuid)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}", response_model=BackgroundCheckDocumentResponse)
async def get_background_check_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = BackgroundCheckService(db)
        return await service.get_document_by_id(document_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/documents/{document_id}", response_model=BackgroundCheckDocumentMessageResponse
)
async def delete_background_check_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = BackgroundCheckService(db)
        return await service.delete_document(document_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
