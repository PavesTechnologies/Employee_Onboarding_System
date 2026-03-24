from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.dao.hr_onboarding_dao import HrOnboardingDAO
# from ...Business_Layer.utils import send_hr_onboarding_submitted_email,send_candidate_onboarding_submitted_email
from ...DAL.dao.hr_onboarding_dao import HrOnboardingDAO
from fastapi import HTTPException
from Backend.DAL.utils.storage_utils import S3StorageService
from Backend.DAL.dao.offerletter_dao import OfferLetterDAO
import re
import asyncio
import time
from datetime import datetime
from Backend.Business_Layer.utils.email_utils import send_hr_onboarding_submitted_email,send_candidate_onboarding_submitted_email

# from fastapi_cache.decorator import cache


class HrOnboardingService:

    HR_EMAIL = "lokeswaribusam216@gmail.com"
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = HrOnboardingDAO(db)
        self.offer_dao = OfferLetterDAO(db)

    async def get_full_onboarding_details(self, user_uuid: str, current_user_id: int):
        return await self.dao.get_full_onboarding_details(
            user_uuid, current_user_id
        )

    # =================================================
    # FINAL SUBMIT – STORE ALL DETAILS (CANDIDATE)
    # =================================================


    async def final_submit_onboarding(self, user_uuid):
        try:
            if await self.offer_dao.get_offer_by_uuid(user_uuid) is None:
                raise HTTPException(status_code=404, detail="Offer Letter Not Found")
            
            personal_details = await self.dao.get_personal_details_by_uuid(user_uuid)
            if personal_details is None:
                raise HTTPException(status_code=404, detail="Personal Details Not Found for this user")
            address_details = await self.dao.get_address_details_by_uuid(user_uuid)
            if address_details is None:
                raise HTTPException(status_code=404, detail="Address Details Not Found for this user")
            identity_details = await self.dao.get_identity_details_by_uuid(user_uuid)
            if identity_details is None:
                raise HTTPException(status_code=404, detail="Identity Details Not Found for this user")
            education_details = await self.dao.get_education_details_by_uuid(user_uuid)
            if education_details is None:
                raise HTTPException(status_code=404, detail="Education Details Not Found for this user")
            experience_details = await self.dao.get_experience_details_by_uuid(user_uuid)
            if experience_details is None:
                raise HTTPException(status_code=404, detail="Experience Details Not Found for this user") 
            
            await self.dao.final_submit_onboarding(user_uuid)

                    # ✅ EMAIL TRIGGER (ONLY ADDITION)
            offer = await self.offer_dao.get_offer_by_uuid(user_uuid)
            candidate_name = f"{offer.first_name} {offer.last_name}"

                # Candidate email
            send_candidate_onboarding_submitted_email(
                to_email=offer.mail,
                candidate_name=candidate_name
            ) 

                # HR email
            send_hr_onboarding_submitted_email(
                    hr_email=self.HR_EMAIL,
                    candidate_name=candidate_name,
                    candidate_email=offer.mail,
                    submitted_at=datetime.utcnow()
            )

            return {"message": "Onboarding submitted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        

    async def view_onboarding_documents(self, file_path: str):
        try:
            print("File path in service:", file_path)
            pattern = r"^s3://[^/]+/(.+?/[0-9a-fA-F-]{36})"
            match = re.search(pattern, file_path)

            if not match:
                raise ValueError("Invalid S3 file path format")
            match = re.search(pattern, file_path).group(1)
            names = match.split('/')
            print("Names:", names)
            if len(names) == 2:
                print("Entering identity and education document check")
                table_name = names[0]
                existing  = await self.dao.identity_and_education_document_exists(table_name, file_path)
                if not existing:
                    print("Document not found in identity and education check")
                    raise HTTPException(status_code=404, detail="Document Not Found")
            elif len(names) == 3:
                print(names)
                table_name = names[0]
                col_name = names[1]
                existing = await self.dao.experience_document_exists(table_name, col_name, file_path)
                if not existing:    
                    raise HTTPException(status_code=404, detail="Document Not Found")
            else:
                raise ValueError("Invalid file path format")
            print("hello")
            blob_service = S3StorageService()
            document_url = await blob_service.get_presigned_url(file_path)
            return document_url
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # =================================================
    # HR VERIFY / REJECT PROFILE
    # =================================================

    async def update_verification_status(
        self,
        user_uuid: str,
        status: str,
        current_user_id: int
    ):
        """
        status: VERIFIED | REJECTED
        """

        if status.upper() not in ["VERIFIED", "REJECTED"]:
            raise HTTPException(status_code=400, detail="Invalid verification status")

        updated = await self.offer_dao.update_offerletter_status(
            user_uuid=user_uuid,new_status=status,current_user_id=current_user_id
            )
        if not updated:
            raise HTTPException(status_code=404, detail="Offer letter not found for the given user UUID")

    async def verify_document(self, payload, current_user_id):

        await self.dao.update_document_status(
        user_uuid=payload.user_uuid,
        document_uuid=payload.document_uuid,
        doc_type=payload.doc_type,
        status=payload.status,
        remarks=payload.remarks,
        verified_by=current_user_id
    )
