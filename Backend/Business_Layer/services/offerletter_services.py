# Backend/Business_Layer/services/offerletter_service.py
import asyncio
from unittest import result
from fastapi import HTTPException
import base64
import os
from fastapi.responses import StreamingResponse
import requests
from httpx import AsyncClient
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from ...API_Layer.interfaces.offerletter_interfaces import(
    BulkSendOfferLettersRequest,
    OfferCreateRequest,
    BulkSendOfferLettersResult,
    BulkSendOfferLettersResponse
)
from Backend.API_Layer.utils.docusign_token_genearation_utils import generate_docusign_access_token
from ...DAL.dao.offerletter_dao import OfferLetterDAO
from ..utils.uuid_generator import generate_uuid7
from ...config.env_loader import get_env_var
from ..utils.validation_utils import (
    validate_name,
    validate_email,
    validate_country,
    validate_phone_number,
    validate_designation,
    validate_package,
    validate_currency
)
DOCUSIGN_BASE_URL = get_env_var("DOCUSIGN_BASE_URL")
DOCUSIGN_ACCOUNT_ID = get_env_var("DOCUSIGN_ACCOUNT_ID")
DOCUSIGN_TEMPLATE_ID = get_env_var("DOCUSIGN_TEMPLATE_ID")
class OfferLetterService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = OfferLetterDAO(self.db)

 
    async def create_offer(self, request_data: OfferCreateRequest, current_user_id: int):
        """
        Business logic for creating a new offer letter.
        Includes validation of all user input fields.
        """
        try:
            # --- VALIDATION SECTION ---
            first_name = validate_name(request_data.first_name)
            middle_name = validate_name(request_data.middle_name) if request_data.middle_name else None
            last_name = validate_name(request_data.last_name)
            mail = validate_email(request_data.mail)
            country_code = validate_country(request_data.country_code)
            contact_number = validate_phone_number(request_data.country_code, request_data.contact_number, type = 'contact_number')
            designation = validate_designation(request_data.designation)
            # package = validate_package(request_data.package)
            # currency = validate_currency(request_data.currency)
            # --- DUPLICATE CHECK ---
            existing_offer = await self.dao.get_offer_by_email(mail)
            if existing_offer:
                raise HTTPException(status_code=400, detail="Offer already exists for this email")

            # --- CREATE OFFER ---
            uuid = generate_uuid7()
            new_offer = await self.dao.create_offer(uuid, request_data, current_user_id)
            await self.db.commit()
            # await self.create_docusign_draft(uuid)

            return uuid
        
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    
    async def create_bulk_offers(self, df, current_user_id: int):
        """
        Bulk create offers with proper transaction handling and duplicate detection.
        Returns data without committing - caller (route) handles commit.
        """
        successful_offers = []
        failed_offers = []

        # --- 1️⃣ Basic Checks ---
        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded Excel file is empty.")

        required_columns = {
            'first_name', 'last_name', 'mail', 'country_code',
            'contact_number', 'designation','employee_type', 'package', 'currency'
        }
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns in Excel file: {', '.join(missing)}"
            )

        total_rows = len(df)
        df = df.dropna(subset=required_columns)
        skipped_rows = total_rows - len(df)

        # --- 2️⃣ Validate All Rows First ---
        valid_offers = []
        seen_emails = set()
        
        for index, row in df.iterrows():
            try:
                # Validate each field
                first_name = validate_name(str(row['first_name']).strip())
                last_name = validate_name(str(row['last_name']).strip())
                mail = validate_email(str(row['mail']).strip())
                country_code = validate_country(str(row['country_code']).strip())
                contact_number = validate_phone_number(str(row['country_code']).strip(), str(row['contact_number']).strip(), type = 'contact_number')
                designation = validate_designation(str(row['designation']).strip())
                package = validate_package(str(row['package']).strip())
                currency = validate_currency(str(row['currency']).strip())

                print(first_name, last_name, mail, country_code, str(row['contact_number']), designation, package, currency)
                # Check for duplicates within the batch
                if mail in seen_emails:
                    failed_offers.append({
                        "row": index + 2,
                        "email": mail,
                        "error": "Duplicate email within this batch"
                    })
                    continue

                seen_emails.add(mail)
                
                request_data = OfferCreateRequest(
                    first_name=first_name,
                    last_name=last_name,
                    mail=mail,
                    country_code=country_code,
                    contact_number=contact_number,
                    designation=designation,
                    employee_type = str(row['employee_type']).strip(),
                    package=package,
                    currency=currency
                    
                )
                valid_offers.append((index, request_data))

            except ValueError as ve:
                failed_offers.append({
                    "row": index + 2,
                    "error": str(ve)
                })
            except Exception as e:
                failed_offers.append({
                    "row": index + 2,
                    "error": f"Unexpected error: {str(e)}"
                })

        # --- 3️⃣ Check for existing emails in DB ---
        if valid_offers:
            emails_to_check = [offer[1].mail for offer in valid_offers]
            existing_emails = await self.dao.get_offers_by_emails(emails_to_check)
            
            if existing_emails:
                existing_email_set = set(existing_emails)
                # Add failed entries for existing emails
                for offer_index, offer_data in valid_offers:
                    if offer_data.mail in existing_email_set:
                        failed_offers.append({
                            "row": offer_index + 2,
                            "email": offer_data.mail,
                            "error": "Offer already exists for this email"
                        })
                
                # Filter out offers with existing emails
                valid_offers = [
                    offer for offer in valid_offers 
                    if offer[1].mail not in existing_email_set
                ]

        # --- 4️⃣ Add All Valid Offers to Session (No Commit) ---
        if valid_offers:
            try:
                for idx, request_data in valid_offers:
                    uuid = generate_uuid7()
                    new_offer = await self.dao.create_offer_no_commit(
                        uuid, request_data, current_user_id
                    )
                    successful_offers.append({
                        "email": request_data.mail,
                        "offer_id": new_offer.user_uuid
                    })
                
                # IMPORTANT: Do NOT commit here - let the route handle it
                # This allows the route to handle transaction boundaries
                
            except IntegrityError as ie:
                # This shouldn't happen if we validated properly
                raise HTTPException(
                    status_code=409, 
                    detail=f"Database constraint violation: {str(ie.orig)}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error preparing bulk offers: {str(e)}"
                )

        # --- 5️⃣ Return Summary (Route will commit) ---
        return {
            "total_rows": total_rows,
            "processed_rows": len(df),
            "successful_count": len(successful_offers),
            "failed_count": len(failed_offers),
            "successful_offers": successful_offers,
            "failed_offers": failed_offers,
            "skipped_rows": skipped_rows
        }

         
    async def get_all_offers(self):
        return await self.dao.get_all_offers()
    
    async def get_offer_by_uuid(self, user_uuid: str):
        offers = await self.dao.get_offer_by_uuid(user_uuid)
        if not offers:
            return None
        return offers
   
    async def update_offer_by_uuid(self, user_uuid: str, request_data: OfferCreateRequest, current_user_id: int):
        try:
            # Check if offer exists first
            offer = await self.dao.get_offer_by_uuid(user_uuid)
            if not offer:
                raise HTTPException(status_code=404, detail="Offer not found")

            # --- VALIDATIONS (Keep consistent with POST) ---
            validate_name(request_data.first_name)
            validate_email(request_data.mail)
            validate_phone_number(request_data.country_code, request_data.contact_number, type='contact_number')
            # Add total_ctc or compensation validation if needed

            # Email uniqueness check
            if request_data.mail != offer['mail']:
                existing = await self.dao.get_offer_by_email(request_data.mail)
                if existing:
                    raise HTTPException(status_code=409, detail="Email already belongs to another offer")

            # --- UPDATE EXECUTION ---
            success = await self.dao.update_offer_by_uuid(user_uuid, request_data, current_user_id)
            
            if success:
                await self.db.commit() # Commit both Detail and Compensation changes
                return True
            
            return False

        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")    
    async def get_offer_by_user_id(self, user_id: int):
        return await self.dao.get_offer_by_user_id(user_id)

    async def get_created_offerletters(self, current_user_id: int):
        """
        Fetch all offer letters where:
        - status = 'created'
        - created_by = current_user_id
        """
        print("Fetching pending offer letters for user:", current_user_id)

        records = await self.dao.fetch_created_offerletters(current_user_id)

        return records
    

    async def create_offerletter_draft_with_pandadoc(self, payload: dict, user_uuid: str):
        """
        Create a PandaDoc draft, extract its ID, store it in DB.
        """
        print("create_offerletter_draft_with_pandadoc service started")
        
        # -------------------- Load ENV Variables --------------------
        try:
            api_key = get_env_var("PANDADOC_API_KEY")
            template_id = get_env_var("PANDADOC_TEMPLATE_ID")
            api_url = get_env_var("PANDADOC_DRAFT_API_URL")

            print("API key loaded:", api_key)
            print("Template ID loaded:", template_id)
            print("API URL loaded:", api_url)

        except Exception as e:
            print("Error loading env variables:", e)
            raise


        # -------------------- Prepare PandaDoc Body --------------------
        print("Preparing PandaDoc document body")

        doc_body = {
            "name": f"Offer Letter {payload['user_uuid']}",
            "template_uuid": template_id,
            "recipients": [
                {
                    "email": payload["email"],
                    "first_name": payload["first_name"],
                    "last_name": payload["last_name"],
                    "role": "Candidate"
                }
            ],
            "tokens": [
                {"name": "first_name", "value": payload["first_name"]},
                {"name": "last_name", "value": payload["last_name"]},
                {"name": "designation", "value": payload["designation"]},
                # {"name": "employee_type", "value": payload["employee_type"]},
                {"name": "package", "value": payload["package"]},
                {"name": "currency", "value": payload["currency"]},
                {"name": "user_uuid", "value": payload["user_uuid"]},
                {"name": "company_name", "value": payload["company_name"]}
            ],
            "send_document": False
        }

        # -------------------- Prepare Headers --------------------
        headers = {
            "Authorization": f"API-Key {api_key}",
            "Content-Type": "application/json"
        }

        print("Headers prepared, sending request to PandaDoc")

        # -------------------- API Call --------------------
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(api_url, json=doc_body, headers=headers)

            if response.status_code not in (200, 201):
                raise Exception(f"PandaDoc Error: {response.status_code} - {response.text}")

            print("PandaDoc request successful:", response.text)
            response_json = response.json()

            # -------------------- Extract Draft ID --------------------
            draft_id = response_json.get("id")
            print("PandaDoc Draft ID extracted:", draft_id)

            if not draft_id:
                raise Exception("PandaDoc did not return a valid document id")

            # -------------------- Save Draft ID in DB --------------------
            print("Updating PandaDoc draft ID in database...")
            await self.dao.update_pandadoc_draft_id(
                user_uuid=user_uuid,
                draft_id=draft_id
            )
            print("Draft ID stored in DB successfully")

            return response_json

        except Exception as e:
            print("Unexpected error during PandaDoc request:", str(e))
            raise

    
    async def poll_pandadoc_draft_status(self, user_uuid: str) -> dict:
        """
        Poll PandaDoc until document status becomes `document.draft`.
        Steps:
        1) Get draft ID from DB using DAO
        2) Poll PandaDoc every 2s
        3) Stop when status = document.draft
        """
        # 1️⃣ Fetch draft_id from DB
        draft_id = await self.dao.get_pandadoc_draft_id(user_uuid)

        if not draft_id:
            raise HTTPException(status_code=400, detail="Draft ID not found for this offer letter")

        print(f"[PandaDoc Poll] Starting poll for draft_id: {draft_id}")

        # 2️⃣ PandaDoc Poll URL
        poll_url = get_env_var("PANDADOC_POLL_API_URL").format(draft_id=draft_id)
        api_key = get_env_var("PANDADOC_API_KEY")

        headers = {
            "Authorization": f"API-Key {api_key}",  # your PandaDoc key
            "Content-Type": "application/json"
        }

        max_attempts = 25    # total ~50 seconds (25 × 2s)
        attempt = 0

        async with httpx.AsyncClient() as client:
            while attempt < max_attempts:
                attempt += 1
                print(f"[PandaDoc Poll] Attempt {attempt}/{max_attempts}")

                try:
                    response = await client.get(poll_url, headers=headers)
                    response.raise_for_status()
                    data = response.json()

                    status = data.get("status")
                    print(f"[PandaDoc Poll] Current status = {status}")

                    # 3️⃣ If draft is ready → return success
                    if status == "document.draft":
                        print(f"[PandaDoc Poll] Draft ready for {draft_id}")
                        return data

                except Exception as e:
                    print(f"[PandaDoc Poll] Error polling: {str(e)}")

                # Wait before next poll
                await asyncio.sleep(2)

        # 4️⃣ Fail after timeout
        raise HTTPException(
            status_code=504,
            detail=f"PandaDoc draft not ready after polling for {draft_id}"
        )
    

    async def send_pandadoc_offerletter(self, user_uuid: str) -> dict:
        """
        Sends the PandaDoc document (email to candidate) after draft status is 'document.draft'.
        - Fetch draft_id from DB
        - Call PandaDoc document send endpoint
        """

        # 1️⃣ Fetch draft_id from DB
        draft_id = await self.dao.get_pandadoc_draft_id(user_uuid)

        if not draft_id:
            raise HTTPException(status_code=400, detail="Draft ID not found for this offer letter")

        print(f"[PandaDoc Send] Sending document for draft_id: {draft_id}")

        # 2️⃣ PandaDoc Send URL
        send_url = get_env_var('PANDADOC_SEND_API_URL').format(draft_id=draft_id)

        # 3️⃣ Build request
        payload = {
            "silent": False,   # Candidate receives email
            "subject": "Your Offer Letter",
            "message": "Please review and sign your offer letter.",
        }

        api_key = get_env_var("PANDADOC_API_KEY")
        headers = {
            "Authorization": f"API-Key {api_key}",
            "Content-Type": "application/json"
        }

        # 4️⃣ Make API call
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(send_url, json=payload, headers=headers)

            if response.status_code not in (200, 202):
                print("PandaDoc send error response:", response.text)
                raise HTTPException(
                    status_code=500,
                    detail=f"PandaDoc send error: {response.text}"
                )

            print(f"[PandaDoc Send] Document sent for draft {draft_id}")
            return response.json()

        except httpx.RequestError as req_err:
            print("[PandaDoc Send] RequestError:", str(req_err))
            raise HTTPException(status_code=500, detail=f"HTTP RequestError: {str(req_err)}")

        except Exception as e:
            print("[PandaDoc Send] Unexpected error:", str(e))
            raise HTTPException(status_code=500, detail=f"Unexpected Error: {str(e)}")
        

    async def send_bulk_offerletters(self, request_data: BulkSendOfferLettersRequest, current_user_id: int):
        """
        Business logic for sending multiple offer letters using PandaDoc.
        Fetches offer details, sends each offer letter, updates status, and
        returns a detailed summary for each UUID.
        """
        print('bulk send service started')
        uuids = request_data.user_uuid_list

        try:
            successful = []
            failed = []

            # --- 1️⃣ Basic Checks ---
            if not request_data:
                raise HTTPException(status_code=400, detail="No offerletter UUIDs provided.")

            total_requests = len(uuids)
            print(f'Total offer letters to send: {total_requests}')
            print('the uuids: ', *uuids)

            # --- 2️⃣ Process Each Offer Letter ---
            for user_uuid in uuids:

                # Fetch DB record using DAO function EXACTLY as written
                record = await self.dao.get_offer_by_uuid(user_uuid)
                print('record fetched for uuid', user_uuid, ':', record)
                if not record:
                    failed.append({
                        "offerletter_uuid": user_uuid,
                        "error": "Offer letter not found in database"
                    })
                    continue

                # Build payload for PandaDoc
                payload = {
                    "first_name": record.first_name,
                    "last_name": record.last_name,
                    "email": record.mail,
                    "designation": record.designation,
                    # "employee_type": record.employee_type,
                    "package": record.package,
                    "currency": record.currency,
                    "user_uuid": user_uuid,
                    "company_name" : "Paves Global Infotech"
                }
                print('payload for uuid', user_uuid, ':', payload)

                # --- 3️⃣ Call PandaDoc ---
                print('Sending offer letter via PandaDoc for uuid', user_uuid)
                # create draft endpoint calling 
                try:
                    print('About to call create_offerletter_draft_with_pandadoc for uuid', user_uuid)
                    await self.create_offerletter_draft_with_pandadoc(payload, user_uuid)
                    print('PandaDoc draft call completed successfully')

                    # poll draft status endpoint calling
                    try:
                        print('About to call poll_pandadoc_draft_status for uuid', user_uuid)
                        await self.poll_pandadoc_draft_status(user_uuid)
                        print('PandaDoc poll call completed successfully')

                        # send document endpoint calling
                        try:
                            print('About to call send_pandadoc_offerletter for uuid', user_uuid)
                            await self.send_pandadoc_offerletter(user_uuid)
                            print('PandaDoc send call completed successfully')

                            # --- 4️⃣ Update Offer Letter Status ---
                            print('About to update offer letter status in DB for uuid', user_uuid)
                            try:
                                await self.dao.update_offerletter_status(
                                    user_uuid = user_uuid,
                                    new_status = "Offered",
                                    current_user_id = current_user_id
                                )
                                print('Offer letter status updated successfully for uuid', user_uuid)

                                # --- 5️⃣ Append to successful ---
                                successful.append({
                                    "offerletter_uuid": user_uuid,
                                    "email": record.mail,
                                    "status": "success",
                                    "message": "Offer letter sent successfully"
                                })
                                print('Offer letter sent and recorded as successful for uuid', user_uuid)

                            except Exception as dao_e:
                                print('Error updating offer letter status for uuid', user_uuid, '-', str(dao_e))
                                failed.append({
                                    "offerletter_uuid": user_uuid,
                                    "email": record.mail,
                                    "error": f"DB update error: {dao_e}"
                                })
                                continue  # skip adding to successful if update failed
                        except Exception as e:
                            print('Error sending offer letter for uuid', user_uuid, '-', str(e))
                            failed.append({
                                "offerletter_uuid": user_uuid,
                                "email": record.mail,
                                "error": str(e)
                            })

                    except Exception as e:
                        print('Error polling offer letter for uuid', user_uuid, '-', str(e))
                        failed.append({
                            "offerletter_uuid": user_uuid,
                            "email": record.mail,
                            "error": str(e)
                        })

                except Exception as e:
                    print('Error drafting offer letter for uuid', user_uuid, '-', str(e))
                    failed.append({
                        "offerletter_uuid": user_uuid,
                        "email": record.mail,
                        "error": str(e)
                    })

            # --- 6️⃣ Build Final Summary ---
            print('Building final summary')

            # Convert successful + failed into `BulkSendOfferLettersResult` list
            results = []

            for s in successful:
                results.append(BulkSendOfferLettersResult(
                    user_uuid=s["offerletter_uuid"],
                    status=s["status"],
                    mail_sent_to=s["email"],
                    pandadoc_status="document_created_and_sent",
                    message=s["message"],
                    error=None
                ))

            for f in failed:
                results.append(BulkSendOfferLettersResult(
                    user_uuid=f["offerletter_uuid"],
                    status="failed",
                    mail_sent_to=f.get("email"),
                    pandadoc_status=None,
                    message=None,
                    error=f.get("error")
                ))

            summary = BulkSendOfferLettersResponse(
                total_requests=total_requests,
                successful=len(successful),
                failed=len(failed),
                results=results
            )

            print('Final summary prepared:', summary.dict())
            return summary


        except HTTPException as he:
            raise he
        except Exception as e:
            print('Unexpected error in send_bulk_offerletters:', str(e))
            raise HTTPException(status_code=500, detail=str(e))
        
    # async def send_bulk_offerletters_via_docusign(
    #     self,
    #     request_data,
    #     current_user_id: int
    # ):
    #     print("🚀 Bulk DocuSign offer letter service started")

    #     uuids = request_data.user_uuid_list
    #     successful = []
    #     failed = []

    #     if not uuids:
    #         raise HTTPException(status_code=400, detail="No UUIDs provided")
    #     try:
    #         for user_uuid in uuids:
    #             print(f"\n🔁 Processing user_uuid: {user_uuid}")

    #             try:
    #                 # 1️⃣ Fetch offer letter record
    #                 record = await self.dao.get_offer_by_uuid(user_uuid)
    #                 if not record:
    #                     failed.append({
    #                         "offerletter_uuid": user_uuid,
    #                         "error": "Offer letter not found"
    #                     })
    #                     continue

    #                 # 2️⃣ Build DocuSign payload
    #                 full_name = f"{record.first_name} {record.last_name}"

    #                 # Get CC emails from DB
    #                 cc_emails = []

    #                 if record.cc_emails:
    #                     cc_emails = [e.strip() for e in record.cc_emails.split(",") if e.strip()]


    #                 # Build template roles
    #                 template_roles = [

    #                     # ✅ Employee (Signer)
    #                     {
    #                         "roleName": "Employee",
    #                         "name": full_name,
    #                         "email": record.mail,

    #                         "tabs": {
    #                             "textTabs": [
    #                                 {"tabLabel": "EF", "value": full_name},
    #                                 {"tabLabel": "EE", "value": record.mail},
    #                                 {"tabLabel": "ET", "value": record.designation},
    #                                 {"tabLabel": "EP", "value": record.package},
    #                                 {"tabLabel": "EC", "value": record.country_code},
    #                                 {"tabLabel": "EN", "value": record.contact_number}
    #                             ]
    #                         }
    #                     }
    #                 ]


    #                 # ✅ Manager (CC) — First CC email
    #                 if cc_emails:
    #                     template_roles.append({
    #                         "roleName": "Manager",   # MUST MATCH TEMPLATE
    #                         "name": "Manager",
    #                         "email": cc_emails[0]
    #                     })


    #                 # Final payload
    #                 payload = {
    #                     "templateId": DOCUSIGN_TEMPLATE_ID,

    #                     "templateRoles": template_roles,
    #                     "status": "sent"
    #                 }

    #                     # "emailSubject": "Your Offer Letter from Paves Global Infotech",
    #                     # "emailBlurb": "Please review and sign your offer letter.",

    #                 # payload = {
    #                 #     "templateId": DOCUSIGN_TEMPLATE_ID,
    #                 #     "templateRoles": [
    #                 #         {
    #                 #             "roleName": "Employee",
    #                 #             "name": full_name,
    #                 #             "email": record.mail,
    #                 #             "tabs": {
    #                 #                 "textTabs": [
    #                 #                     {"tabLabel": "EF", "value": full_name},
    #                 #                     {"tabLabel": "EE", "value": record.mail},
    #                 #                     {"tabLabel": "ET", "value": record.designation},
    #                 #                     {"tabLabel": "EP", "value": record.package},
    #                 #                     # {"tabLabel": "EET", "value": record.employee_type},
    #                 #                     {"tabLabel": "EC", "value": record.country_code},
    #                 #                     {"tabLabel": "EN", "value": record.contact_number}
    #                 #                 ]
    #                 #             }
    #                 #         },
    #                 #         {
    #                 #             "roleName": "Manager",
    #                 #             "name": "Ajay Kumar",
    #                 #             "email": "ajaykumar1438742@gmail.com"
    #                 #         }
    #                 #     ],
    #                 #     "status": "sent"
    #                 # }

    #                 print("📄 DocuSign payload prepared")
    #                 print(payload)
    #                 # 3️⃣ Get DocuSign access token
    #                 token_data = generate_docusign_access_token()
    #                 access_token = token_data["access_token"]
    #                 print("🔑 DocuSign access token obtained")

    #                 # 4️⃣ Call DocuSign Create Envelope API
    #                 url = f"{DOCUSIGN_BASE_URL}/v2.1/accounts/{DOCUSIGN_ACCOUNT_ID}/envelopes"

    #                 headers = {
    #                     "Authorization": f"Bearer {access_token}",
    #                     "Content-Type": "application/json"
    #                 }

    #                 response = requests.post(url, json=payload, headers=headers)
    #                 response.raise_for_status()

    #                 response_data = response.json()
    #                 envelope_id = response_data.get("envelopeId")

    #                 if not envelope_id:
    #                     raise Exception("Envelope ID not returned by DocuSign")

    #                 print(f"✅ Envelope sent successfully: {envelope_id}")

    #                 # 5️⃣ Store envelopeId (replace PandaDoc ID)
    #                 await self.dao.update_pandadoc_draft_id(
    #                     user_uuid=user_uuid,
    #                     draft_id=envelope_id
    #                 )

    #                 # 6️⃣ Update offer letter status
    #                 await self.dao.update_offerletter_status(
    #                     user_uuid=user_uuid,
    #                     new_status="Offered",
    #                     current_user_id=current_user_id
    #                 )

    #                 successful.append({
    #                     "offerletter_uuid": user_uuid,
    #                     "email": record.mail,
    #                     "status": "success",
    #                     "message": "Offer letter sent via DocuSign"
    #                 })

    #             except Exception as e:
    #                 print(f"❌ Error processing {user_uuid}: {str(e)}")
    #                 failed.append({
    #                     "offerletter_uuid": user_uuid,
    #                     "email": getattr(record, "mail", None),
    #                     "error": str(e)
    #                 })

    #         print("📊 Bulk DocuSign sending completed")

    #         return "Offer letters sent via DocuSign successfully"
    #     except Exception as e:
    #         print("❗ Unexpected error in bulk DocuSign service:", str(e))
    #         raise HTTPException(status_code=500, detail=str(e))


    # async def send_bulk_offerletters_via_docusign(
    #     self,
    #     request_data,
    #     current_user_id: int
    # ):

    #     print("🚀 Bulk DocuSign SEND started")

    #     uuids = request_data.user_uuid_list
    #     successful = []
    #     failed = []

    #     if not uuids:
    #         raise HTTPException(status_code=400, detail="No UUIDs provided")

    #     try:
    #         # 🔑 Generate DocuSign token once
    #         token_data = generate_docusign_access_token()
    #         access_token = token_data["access_token"]

    #         headers = {
    #             "Authorization": f"Bearer {access_token}",
    #             "Content-Type": "application/json"
    #         }

    #         for user_uuid in uuids:
    #             print(f"\n🔁 Processing user_uuid: {user_uuid}")

    #             try:
    #                 # 1️⃣ Get envelope_id from DB
    #                 envelope_id = await self.dao.get_pandadoc_draft_id(user_uuid)

    #                 if not envelope_id:
    #                     failed.append({
    #                         "offerletter_uuid": user_uuid,
    #                         "error": "DocuSign envelope not created"
    #                     })
    #                     continue

    #                 # 2️⃣ Call DocuSign update envelope status API
    #                 url = f"{DOCUSIGN_BASE_URL}/v2.1/accounts/{DOCUSIGN_ACCOUNT_ID}/envelopes/{envelope_id}"

    #                 payload = {
    #                     "status": "sent"
    #                 }

    #                 response = requests.put(url, json=payload, headers=headers)
    #                 response.raise_for_status()

    #                 print(f"✅ Envelope sent: {envelope_id}")

    #                 # 3️⃣ Update DB status
    #                 await self.dao.update_offerletter_status(
    #                     user_uuid=user_uuid,
    #                     new_status="Offered",
    #                     current_user_id=current_user_id
    #                 )

    #                 successful.append({
    #                     "offerletter_uuid": user_uuid,
    #                     "status": "success",
    #                     "message": "Offer letter sent via DocuSign"
    #                 })

    #             except Exception as e:
    #                 print(f"❌ Error sending {user_uuid}: {str(e)}")

    #                 failed.append({
    #                     "offerletter_uuid": user_uuid,
    #                     "error": str(e)
    #                 })

    #         print("📊 Bulk send completed")

    #         return {
    #             "successful": successful,
    #             "failed": failed
    #         }

    #     except Exception as e:
    #         print("❗ Unexpected error in bulk send:", str(e))
    #         raise HTTPException(status_code=500, detail=str(e))
        

    # async def send_bulk_offerletters_via_docusign_pdf(
    #         self,
    #         request_data,
    #         current_user_id: int
    #     ):

    #         print("🚀 Sending generated PDF via DocuSign")

    #         uuids = request_data.user_uuid_list
    #         print("📦 UUIDs received:", uuids)


    #         token_data = generate_docusign_access_token()
    #         access_token = token_data["access_token"]

    #         print("🔑 Token generated (first 50 chars):", access_token[:50])

    #         headers = {
    #             "Authorization": f"Bearer {access_token}",
    #             "Content-Type": "application/json"
    #         }


    #         for user_uuid in uuids:
    #             print("\n🔁 Processing UUID:", user_uuid)

    #             record = await self.dao.get_offer_by_uuid(user_uuid)

    #             if not record:
    #                 print("Offer not found:", user_uuid)
    #                 continue

    #             # 1️⃣ PDF path
    #             pdf_path = os.path.join(os.getcwd(), "generated_pdfs", f"offer_{user_uuid}.pdf")

    #                     # ✅ DEBUG LOGS (PDF)
    #             print("📂 Checking PDF path:", pdf_path)
    #             print("📁 File exists:", os.path.exists(pdf_path))
    #             try:
    #                    print("📁 Available files:", os.listdir("generated_pdfs"))
    #             except Exception as e:
    #                     print("⚠️ Could not list directory:", str(e))

    #             if not os.path.exists(pdf_path):
    #                 raise Exception(f"PDF not found for {user_uuid}")

    #             # 2️⃣ Convert PDF → base64
    #             with open(pdf_path, "rb") as f:
    #                 pdf_base64 = base64.b64encode(f.read()).decode()

    #             print("📄 PDF converted to base64 (length):", len(pdf_base64))
    #             # 🔥 Handle different record types
    #             if isinstance(record, dict):
    #                 email = record.get("mail")
    #                 first_name = record.get("first_name")
    #                 last_name = record.get("last_name")

    #             elif hasattr(record, "__dict__"):
    #                 email = getattr(record, "mail", None)
    #                 first_name = getattr(record, "first_name", None)
    #                 last_name = getattr(record, "last_name", None)

    #             else:
    #                 # tuple or Row
    #                 print("⚠️ Record is tuple/Row, accessing by index")
    #                 email = record[2]        # ⚠️ adjust if needed
    #                 first_name = record[0]
    #                 last_name = record[1]

                

    #             if not email:
    #                 raise Exception("Email missing in record")
                
                
    #             # 3️⃣ Document
    #             document = {
    #                 "documentBase64": pdf_base64,
    #                 "name": "Offer Letter",
    #                 "fileExtension": "pdf",
    #                 "documentId": "1"
    #             }

    #             # 4️⃣ Signer
    #             signer = {
    #                 "email": email,
    #                 "name": f"{first_name} {last_name}",
    #                 "recipientId": "1",
    #                 "routingOrder": "1",
    #                 "tabs": {
    #                     "signHereTabs": [
    #                         {
    #                             "documentId": "1",
    #                             "pageNumber": "1",
    #                             "xPosition": "450",
    #                             "yPosition": "650"
    #                         }
    #                     ]
    #                 }
    #             }

    #             envelope_definition = {
    #                 "emailSubject": "Please sign your offer letter",
    #                 "documents": [document],
    #                 "recipients": {
    #                     "signers": [signer]
    #                 },
    #                 "status": "sent"
    #             }
    #             print("🌐 DOCUSIGN_BASE_URL:", DOCUSIGN_BASE_URL)
    #             print("🏢 DOCUSIGN_ACCOUNT_ID:", DOCUSIGN_ACCOUNT_ID)

    #             url = f"{DOCUSIGN_BASE_URL}/v2.1/accounts/{DOCUSIGN_ACCOUNT_ID}/envelopes"
    #             # ✅ DEBUG LOGS (Before API call)
    #             print("📤 Sending request to DocuSign...")
    #             print("👤 Email:", email)
    #             print("🌐 URL:", url)

    #             response = requests.post(
    #                 url,
    #                 json=envelope_definition,
    #                 headers=headers
    #             )
    #             # ✅ DEBUG LOGS (After API call)
    #             print("📥 DocuSign Status Code:", response.status_code)
    #             print("📥 DocuSign Response:", response.text)


             

             


    #             if response.status_code not in[200,201]:
    #                 print("❌ DocuSign Error:", response.text)
    #                 raise Exception(f"DocuSign failed: {response.text}")

    #             envelope_id = response.json()["envelopeId"]

    #             print("Envelope created:", envelope_id)

    #             await self.dao.update_pandadoc_draft_id(user_uuid, envelope_id)

    #             await self.dao.update_offerletter_status(
    #                 user_uuid=user_uuid,
    #                 new_status="Offered",
    #                 current_user_id=current_user_id
    #             )

    #         return {"message": "Offer letters sent via DocuSign"}


    async def send_bulk_offerletters_via_docusign_pdf(
        self,
        request_data,
        current_user_id: int
    ):

        print("🚀 Sending generated PDF via DocuSign")

        uuids = request_data.user_uuid_list
        print("📦 UUIDs received:", uuids)

        # 🔑 Generate token once
        token_data = generate_docusign_access_token()
        access_token = token_data["access_token"]

        print("🔑 Token generated (first 50 chars):", access_token[:50])

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        for user_uuid in uuids:
            print("\n🔁 Processing UUID:", user_uuid)

            # 1️⃣ Fetch record
            record = await self.dao.get_offer_by_uuid(user_uuid)

            if not record:
                print("❌ Offer not found:", user_uuid)
                continue

            # 2️⃣ Extract data safely (DICT)
            email = record.get("mail")
            first_name = record.get("first_name")
            last_name = record.get("last_name")
            cc_raw = record.get("cc_mails")
            

            


            print("👤 Employee:", email)

            if not email:
                raise Exception("Email missing in record")

            # 3️⃣ Extract managers from cc_mails
            cc_emails = []
            if cc_raw:
                cc_emails = cc_raw
            else:
                print("⚠️ No cc_mails found in DB")

            print("👥 Managers:", cc_emails)

            # 4️⃣ PDF path
            pdf_path = os.path.join(
                os.getcwd(),
                "generated_pdfs",
                f"offer_{user_uuid}.pdf"
            )

            print("📂 Checking PDF path:", pdf_path)
            print("📁 File exists:", os.path.exists(pdf_path))

            if not os.path.exists(pdf_path):
                raise Exception(f"PDF not found for {user_uuid}")

            # 5️⃣ Convert PDF → base64
            with open(pdf_path, "rb") as f:
                pdf_base64 = base64.b64encode(f.read()).decode()

            print("📄 PDF converted to base64 (length):", len(pdf_base64))

            # 6️⃣ Document
            document = {
                "documentBase64": pdf_base64,
                "name": "Offer Letter",
                "fileExtension": "pdf",
                "documentId": "1"
            }

            # 7️⃣ Build signers dynamically
            signers = []
            routing_order = 1

            # 🔹 Managers (FIRST)
            for idx, manager_email in enumerate(cc_emails):
                signers.append({
                    "email": manager_email,
                    "name": f"Manager {idx+1}",
                    "recipientId": str(routing_order),
                    "routingOrder": str(routing_order),
                    "tabs": {
                        "signHereTabs": [
                            {
                                "documentId": "1",
                                "pageNumber": "5",
                                "xPosition": "120",
                                "yPosition": "300"
                            }
                        ]
                    }
                })
                routing_order += 1

            # 🔹 Employee (LAST)
            signers.append({
                "email": email,
                "name": f"{first_name} {last_name}",
                "recipientId": str(routing_order),
                "routingOrder": str(routing_order),
                "tabs": {
                    "signHereTabs": [
                        {
                            "documentId": "1",
                            "pageNumber": "5",
                            "xPosition": "360",
                            "yPosition": "620"
                        }
                    ]
                }
            })

            print("🧾 Total Signers:", len(signers))

            # 8️⃣ Envelope
            envelope_definition = {
                "emailSubject": "Please sign the offer letter",
                "documents": [document],
                "recipients": {
                    "signers": signers
                },
                "status": "sent"
            }

            # 9️⃣ API call
            url = f"{DOCUSIGN_BASE_URL}/v2.1/accounts/{DOCUSIGN_ACCOUNT_ID}/envelopes"

            print("📤 Sending request to DocuSign...")
            print("🌐 URL:", url)

            response = requests.post(
                url,
                json=envelope_definition,
                headers=headers
            )

            print("📥 DocuSign Status Code:", response.status_code)
            print("📥 DocuSign Response:", response.text)

            # 🔟 Handle response
            if response.status_code not in [200, 201]:
                raise Exception(f"DocuSign failed: {response.text}")

            envelope_id = response.json()["envelopeId"]

            print("✅ Envelope created:", envelope_id)

            # 1️⃣1️⃣ Save envelope ID
            await self.dao.update_pandadoc_draft_id(user_uuid, envelope_id)

            # 1️⃣2️⃣ Update status
            await self.dao.update_offerletter_status(
                user_uuid=user_uuid,
                new_status="Offered",
                current_user_id=current_user_id
            )

        return {"message": "Offer letters sent via DocuSign"}
    async def delete_offer_letter(self, user_uuid: str) -> str:
            """
            Delete offer only when:
            1. status = Rejected
            2. status = Created AND approval action = REJECTED
            3. status = Created AND approval not started

            Block when approval exists.
            """

            try:
                # 🔎 Fetch offer
                offer = await self.dao.get_offer_by_uuid(user_uuid)
                if not offer:
                    raise HTTPException(status_code=404, detail="Offer letter not found")

                # 🚨 Check approval request existence
                approval_request = await self.dao.get_approval_request_by_user_uuid(user_uuid)

                if approval_request:
                    raise HTTPException(
                        status_code=400,
                        detail="Approval already initiated for this offer. Delete approval request first.",
                    )

                # ✅ Apply status-based delete rules
                if offer.status not in ["Rejected", "Created"]:
                    raise HTTPException(
                        status_code=400,
                        detail="Offer letter cannot be deleted due to its current status",
                    )

                # 🗑 Delete offer
                await self.dao.delete_offer_letter(user_uuid)

                # 💾 Commit once in service
                await self.db.commit()

                return "Offer letter deleted successfully"

            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    async def create_docusign_draft(self, user_uuid: str):

                record = await self.dao.get_offer_by_uuid(user_uuid)

                if not record:
                    raise HTTPException(status_code=404, detail="Offer not found")

                full_name = f"{record['first_name']} {record['last_name']}"

                cc_emails = []
                if record.get("cc_emails"):
                    
                    cc_emails = [e.strip() for e in record["cc_emails"].split(",") if e.strip()]

                template_roles = [
                    {
                        "roleName": "Employee",
                        "name": full_name,
                        "email": record["mail"],
                        "tabs": {
                            "textTabs": [
                                {"tabLabel": "EF", "value": full_name},
                                {"tabLabel": "EE", "value": record["mail"]},
                                {"tabLabel": "ET", "value": record["designation"]},
                                {"tabLabel": "EC", "value": record["country_code"]},
                                {"tabLabel": "EN", "value": record["contact_number"]}
                            ]
                        }
                    }
                ]

                if cc_emails:
                    template_roles.append({
                        "roleName": "Manager",
                        "name": "Manager",
                        "email": cc_emails[0]
                    })

                payload = {
                    "templateId": DOCUSIGN_TEMPLATE_ID,
                    "templateRoles": template_roles,
                    "status": "created"  
                }

                token_data = generate_docusign_access_token()
                access_token = token_data["access_token"]

                url = f"{DOCUSIGN_BASE_URL}/v2.1/accounts/{DOCUSIGN_ACCOUNT_ID}/envelopes"

                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }

                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()

                envelope_id = response.json().get("envelopeId")

                if not envelope_id:
                    raise Exception("Envelope ID not returned")

                # 🔥 Store envelope id
                await self.dao.update_pandadoc_draft_id(
                    user_uuid=user_uuid,
                    draft_id=envelope_id
                )

    async def get_docusign_preview(self, user_uuid: str):
        """
        Generate and return the DocuSign preview URL for the offer letter.
        Steps:
        1) Fetch envelope_id from DB using DAO
        2) Call DocuSign API to get recipient view (preview) URL
        """

        try:
            # 1️⃣ Fetch envelope_id from DB
            envelope_id = await self.dao.get_pandadoc_draft_id(user_uuid)

            if not envelope_id:
                raise HTTPException(status_code=404, detail="DocuSign envelope not found for this offer letter")

            print(f"[DocuSign Preview] Fetching preview for envelope_id: {envelope_id}")

            # 2️⃣ Call DocuSign API to get recipient view URL
            token_data = generate_docusign_access_token()
            access_token = token_data["access_token"]

            url = f"{DOCUSIGN_BASE_URL}/v2.1/accounts/{DOCUSIGN_ACCOUNT_ID}/envelopes/{envelope_id}/views/sender"

            payload = {
                "returnUrl": "https://localhost:5173/offer-preview-return"  # Change to your actual return URL
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            preview_url = response.json().get("url")

            if not preview_url:
                raise Exception("Preview URL not returned by DocuSign")

            print(f"[DocuSign Preview] Preview URL obtained: {preview_url}")
            return {"preview_url": preview_url}

        except HTTPException:
            raise
        except Exception as e:
            print(f"[DocuSign Preview] Error obtaining preview: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    async def get_final_offer_preview(self, user_uuid: str):

        try:
            envelope_id = await self.dao.get_pandadoc_draft_id(user_uuid)
 
            if not envelope_id:
                raise HTTPException(
                    status_code=404,
                    detail="Envelope not found"
                )

            token_data = generate_docusign_access_token()
            access_token = token_data["access_token"]

            url = f"{DOCUSIGN_BASE_URL}/v2.1/accounts/{DOCUSIGN_ACCOUNT_ID}/envelopes/{envelope_id}/documents/1"

            headers = {
                "Authorization": f"Bearer {access_token}"
            }

            response = requests.get(url, headers=headers, stream=True)

            response.raise_for_status()

            return StreamingResponse(
                response.raw,
                media_type="application/pdf"
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    

    

    # async def generate_offer_pdf_preview(self, user_uuid: str):

    #   offer = await self.dao.get_offer_by_uuid(user_uuid)

    # if not offer:
    #     raise HTTPException(status_code=404, detail="Offer not found")

    # buffer = BytesIO()

    # pdf = canvas.Canvas(buffer)

    # pdf.drawString(100, 750, f"Offer Letter")

    # pdf.drawString(100, 720, f"Name: {offer['first_name']} {offer['last_name']}")
    # pdf.drawString(100, 700, f"Email: {offer['mail']}")
    # pdf.drawString(100, 680, f"Designation: {offer['designation']}")
    # pdf.drawString(100, 660, f"Employee Type: {offer['employee_type']}")
    # pdf.drawString(100, 640, f"Contact: +{offer['country_code']} {offer['contact_number']}")

    # pdf.drawString(100, 610, f"Total CTC: {offer['total_ctc']}")

    # pdf.showPage()
    # pdf.save()

    # buffer.seek(0)

    # return StreamingResponse(
    #     buffer,
    #     media_type="application/pdf",
    #     headers={
    #         "Content-Disposition": f"inline; filename=offer_{user_uuid}.pdf"
    #     }
    # )