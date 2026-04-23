from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.DAL.utils.dependencies import get_db
from Backend.Business_Layer.services.exit_documents_service import ExitDocumentsService
from Backend.API_Layer.interfaces.exit_documents_interface import ExitDocumentResponse


router = APIRouter(
    prefix="/exit-documents",
    tags=["Exit Documents"]
)
# Generate Relieving
@router.post("/generate/relieving/{exit_uuid}", response_model=ExitDocumentResponse)
async def generate_relieving(exit_uuid: str, request: Request, db: AsyncSession = Depends(get_db)):

    service = ExitDocumentsService()

    user = request.state.user

    return await service.generate_single_document(
        db,
        exit_uuid,
        user.get("user_id"),
        "Relieving Letter",
        "relieving_letter.html"
    )


# Generate Experience
@router.post("/generate/experience/{exit_uuid}", response_model=ExitDocumentResponse)
async def generate_experience(exit_uuid: str, request: Request, db: AsyncSession = Depends(get_db)):

    service = ExitDocumentsService()

    user = request.state.user

    return await service.generate_single_document(
        db,
        exit_uuid,
        user.get("user_id"),
        "Experience Letter",
        "experience_letter.html"
    )


# Generate FNF
@router.post("/generate/fnf/{exit_uuid}", response_model=ExitDocumentResponse)
async def generate_fnf(exit_uuid: str, request: Request, db: AsyncSession = Depends(get_db)):

    service = ExitDocumentsService()

    user = request.state.user

    return await service.generate_single_document(
        db,
        exit_uuid,
        user.get("user_id"),
        "Full & Final",
        "fnf_letter.html"
    )


# Generate NOC
@router.post("/generate/noc/{exit_uuid}", response_model=ExitDocumentResponse)
async def generate_noc(exit_uuid: str, request: Request, db: AsyncSession = Depends(get_db)):

    service = ExitDocumentsService()

    user = request.state.user

    return await service.generate_single_document(
        db,
        exit_uuid,
        user.get("user_id"),
        "NOC",
        "noc_letter.html"
    )


# Generate Resignation
@router.post("/generate/resignation/{exit_uuid}", response_model=ExitDocumentResponse)
async def generate_resignation(exit_uuid: str, request: Request, db: AsyncSession = Depends(get_db)):

    service = ExitDocumentsService()

    user = request.state.user

    return await service.generate_single_document(
        db,
        exit_uuid,
        user.get("user_id"),
        "Resignation Letter",
        "resignation_letter.html"
    )


# Generate Termination
@router.post("/generate/termination/{exit_uuid}", response_model=ExitDocumentResponse)
async def generate_termination(exit_uuid: str, request: Request, db: AsyncSession = Depends(get_db)):

    service = ExitDocumentsService()

    user = request.state.user

    return await service.generate_single_document(
        db,
        exit_uuid,
        user.get("user_id"),
        "Termination Letter",
        "termination_letter.html"
    )


# Get All Documents
@router.get("/{exit_uuid}", response_model=list[ExitDocumentResponse])
async def get_documents(exit_uuid: str, db: AsyncSession = Depends(get_db)):

    service = ExitDocumentsService()

    return await service.get_documents(
        db,
        exit_uuid
    )


# Download
@router.get("/download/{document_uuid}")
async def download_document(document_uuid: str, db: AsyncSession = Depends(get_db)):

    service = ExitDocumentsService()

    return await service.download_document(
        db,
        document_uuid
    )


# View
@router.get("/view/{document_uuid}")
async def view_document(document_uuid: str, db: AsyncSession = Depends(get_db)):

    service = ExitDocumentsService()

    return await service.view_document(
        db,
        document_uuid
    )