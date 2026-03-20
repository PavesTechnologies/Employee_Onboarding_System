from email.mime import text
from sqlalchemy import text
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.utils.dependencies import get_db
from Backend.API_Layer.interfaces.token_verification_interfaces import TokenVerificationRequest, TokenVerificationResponse
from Backend.Business_Layer.services.token_verification_service import OnboardingVerifyLinkService

router = APIRouter()
@router.post("/verify_token")
async def verify_token(
    requestdata: TokenVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verifies the onboarding token sent to the user's email."""

    service = OnboardingVerifyLinkService(db)
    print(f"🔐 API: Verifying token...")

    result = await service.verify_token(requestdata)

    return result

@router.get("/{raw_token}")
async def get_user_uuid_by_token(
    raw_token: str,
    db: AsyncSession = Depends(get_db)
):
    service = OnboardingVerifyLinkService(db)

    try:
        print("🔐 Verifying token:", raw_token)

        # ✅ Step 1: Validate token properly
        valid_link = await service.dao.get_valid_link_by_token(raw_token)

        if not valid_link:
            print("❌ Invalid or expired token")
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        user_uuid = valid_link.user_uuid

        if not user_uuid:
            print("❌ user_uuid is None")
            raise HTTPException(status_code=400, detail="Invalid user")

        print("✅ user_uuid:", user_uuid)

        # ✅ Step 2: Safe DB check
        result = await db.execute(
            text("SELECT 1 FROM offer_letter_details WHERE user_uuid = :user_uuid"),
            {"user_uuid": user_uuid}
        )

        exists = result.first()

        # ✅ Step 3: Insert if not exists
        if not exists:
            await db.execute(
                text("INSERT INTO offer_letter_details (user_uuid) VALUES (:user_uuid)"),
                {"user_uuid": user_uuid}
            )
            await db.commit()
            print("✅ Inserted new record")

        return user_uuid

    except HTTPException as http_err:
        raise http_err

    except Exception as e:
        print("🔥 FULL ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))  # 👈 show actual error