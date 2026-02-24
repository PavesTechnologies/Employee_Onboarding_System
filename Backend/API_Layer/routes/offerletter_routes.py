# Backend/API_Layer/routes/offerletter_routes.py

from Backend.DAL.utils.database import get_read_db
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from ...API_Layer.interfaces.offerletter_interfaces import(
    DeleteOfferResponse,
    OfferCreateRequest, 
    OfferCreateResponse, 
    BulkOfferCreateResponse,
    OfferLetterDetailsResponse, 
    OfferUpdateResponse,
    BulkSendOfferLettersResponse, 
    BulkSendOfferLettersRequest,
    BulkSendOfferLettersResult,
)
from ...Business_Layer.services.offerletter_services import OfferLetterService
from ...DAL.utils.dependencies import get_db
import pandas as pd
from io import BytesIO
from ...config import env_loader
import requests
from ..utils.role_based import require_roles

router = APIRouter()

# ✅ Create single offer letter
@router.post("/create", response_model=OfferCreateResponse, dependencies=[Depends(require_roles("HR", "Admin"))])
async def create_offer_letter(
    request_data: OfferCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a single offer letter.
    Uses FastAPI dependency injection to manage DB session.
    """
    try:
        print("In create_offer_letter route", request_data)
        print("current user", request.state.user.get("user_id"))  # Example of accessing user info from JWT
        current_user_id = int(request.state.user.get("user_id"))  # ✅ Access user info from request state

        offer_service = OfferLetterService(db)           # ✅ pass injected session
        offer_id = await offer_service.create_offer(request_data, current_user_id)

        return OfferCreateResponse(
            message="Offer letter created successfully",
            offer_id=offer_id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Bulk create offer letters
@router.post("/bulk_create", response_model=BulkOfferCreateResponse, dependencies=[Depends(require_roles("HR", "ADMIN"))])

async def create_bulk_offer_letters(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Creates multiple offer letters from an uploaded Excel file.
    Handles transaction commit/rollback at route level.
    """
    current_user_id = None
    try:
        # Validate file first
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file format. Only .xlsx, .xls, .csv are allowed"
            )

        current_user_id = int(request.state.user.get("user_id"))
        
        # Read file into DataFrame
        content = await file.read()
        
        try:
            df = pd.read_excel(BytesIO(content), engine="openpyxl")
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to read Excel file: {str(e)}"
            )

        # Service handles validation and data preparation
        offer_service = OfferLetterService(db)
        result = await offer_service.create_bulk_offers(df, current_user_id)
        
        # Route handles transaction commit
        await db.commit()
        
        return result

    except HTTPException:
        # HTTPException is already formatted properly
        if current_user_id:  # Only rollback if we had a valid session
            await db.rollback()
        raise
        
    except Exception as e:
        # Catch any unexpected errors
        if current_user_id:
            await db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )


# ✅ Get all offers
@router.get("/", response_model=list[OfferLetterDetailsResponse], dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def get_all_offers(
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves all offer letters.
    """
    try:
        offer_service = OfferLetterService(db)
        offers = await offer_service.get_all_offers()
        return offers

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import time

@router.get("/user_id/details", response_model=list[OfferLetterDetailsResponse], dependencies=[Depends(require_roles("HR", "ADMIN"))])

async def get_offer_by_user_id(
    request: Request,
    db: AsyncSession = Depends(get_read_db)
):
    start = time.perf_counter()

    current_user_id = int(request.state.user.get("user_id"))
    offer_service = OfferLetterService(db)
    result = await offer_service.get_offer_by_user_id(current_user_id)

    print("⏱ FULL endpoint:", time.perf_counter() - start)
    return result
    
# get offer by offer uuid
@router.get("/offer/{user_uuid}", response_model=OfferLetterDetailsResponse)

async def get_offer_by_uuid(
    user_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves an offer letter by its UUID.
    """
    try:
        offer_service = OfferLetterService(db)
        offer = await offer_service.get_offer_by_uuid(user_uuid)
        if not offer:
            raise HTTPException(status_code=404, detail="Offer letter not found")
        cc_raw = getattr(offer, "cc_emails", "")
        if cc_raw:
            cc_list = [e.strip() for e in cc_raw.split(",") if e.strip()]
        else:
            cc_list = []
        return {
            "user_uuid": offer.user_uuid,
            "first_name": offer.first_name,
            "last_name": offer.last_name,
            "mail": offer.mail,
            "country_code": offer.country_code,
            "contact_number": offer.contact_number,
            "designation": offer.designation,
            "employee_type": offer.employee_type,
            "package": offer.package,
            "currency": offer.currency,
            "created_by": offer.created_by,
            "status": offer.status,
            "cc_emails": cc_list
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.put("/{user_uuid}", response_model=OfferUpdateResponse)

async def update_offer_by_uuid(
    user_uuid: str,
    request_data: OfferCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        offer_service = OfferLetterService(db)
        current_user_id = int(request.state.user.get("user_id"))

        offer = await offer_service.update_offer_by_uuid(
            user_uuid, request_data, current_user_id
        )

        return OfferUpdateResponse(
            message="Offer Details Updated Successfully",
            offer_id=user_uuid
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/created", response_model=list[OfferLetterDetailsResponse], dependencies=[Depends(require_roles("HR", "ADMIN"))])

async def get_created_offerletters(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    print("Fetching created offer letters endpoint called")
    # Extract user_id from JWT middleware
    current_user_id = request.state.user.get("user_id")

    offer_service = OfferLetterService(db)
    result =  await offer_service.get_created_offerletters(current_user_id)
    for i in result:
        print("uuid", i.user_uuid)
    return result


@router.post("/bulk-send", dependencies=[Depends(require_roles("HR", "ADMIN"))])

async def bulk_send_offer_letters(
    request_data: BulkSendOfferLettersRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    print("Bulk send offer letters endpoint called")
    offer_service = OfferLetterService(db)
    print('offer_service created in route')
    return await offer_service.send_bulk_offerletters_via_docusign(request_data, int(request.state.user.get("user_id")))

## delete offer letter by user_uuid only when it satisfies the following conditions:
# 1. The offer letter status is 'rejected'
# 2. The offer letter status was in 'created' and approval status is 'Rejected'
# 3. the offer letter status is in  'created'(no action taken from approver
@router.delete("/delete/{user_uuid}", response_model=DeleteOfferResponse, dependencies=[Depends(require_roles("HR", "ADMIN"))])
async def delete_offer_letter(

    user_uuid: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        print("Delete offer letter endpoint called")
        offer_service = OfferLetterService(db)
        result = await offer_service.delete_offer_letter(user_uuid)
        if result:
            return DeleteOfferResponse(message="Offer letter deleted successfully")
        else:
            raise HTTPException(status_code=400, detail="Offer letter cannot be deleted due to its current status or it does not exist")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

