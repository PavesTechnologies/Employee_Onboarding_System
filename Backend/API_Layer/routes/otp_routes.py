from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from Backend.API_Layer.interfaces.otp_interfaces import OtpRequestBody, OtpResponseStatus
from Backend.Business_Layer.services.otp_service import OtpResponseService
from ...DAL.utils.dependencies import get_db
from ..utils.role_based import require_roles

router = APIRouter()

@router.post("/send", response_model=OtpResponseStatus)
async def send_otp(
    email: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    service = OtpResponseService(db)
    print(f"📧 API: Sending OTP to {email}...")

    result = await service.send_otp_if_allowed(email)

    if result.status != "success":
        raise HTTPException(
            status_code=400,
            detail=result.message
        )

    return result

@router.post("/verifyOtp", response_model=OtpResponseStatus)
async def verify_otp(
    requestdata: OtpRequestBody,
    db: AsyncSession = Depends(get_db)
):
    """Verifies the OTP sent to the user's email."""
    service = OtpResponseService(db)
    result = await service.verify_otp(requestdata.email, requestdata.otp)

    if result.status.upper() != "SUCCESS":
        raise HTTPException(
            status_code=400,
            detail=result.message
        )

    return result