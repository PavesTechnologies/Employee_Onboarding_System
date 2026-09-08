 
 
# test_email.py

"""

Standalone script to test all email functions in Backend/Business_Layer/utils/email_utils.py

Make sure your .env file has EMAIL_USER, EMAIL_PASSWORD, EMAIL_HOST, EMAIL_PORT set.

"""
 
from Backend.Business_Layer.utils.email_utils import (

    send_email,

    send_offer_accepted_email,

    send_otp_email,

    send_candidate_onboarding_submitted_email,

    send_hr_onboarding_submitted_email,

    send_joining_email,

)

from datetime import datetime
 
# Test recipient (candidate)

TEST_RECIPIENT = "chinnuabhishek123@gmail.com"

# Test HR recipient (hard-coded HR mailbox in service layer, but we can simulate here)

HR_RECIPIENT = "chinnuabhishek123@gmail.com"
 
def main():

    # 1. Generic send_email (Background Verification Request)

    print("\n--- Testing send_email (generic background verification) ---")

    # send_email(

    #     to_email="chinnuabhishek123@gmail.com",

    #     subject="Background Verification Request – Abhi",

    #     content="<p>Please find attached candidate documents for verification.</p>",

    #     cc_emails=[HR_RECIPIENT],

    #     attachment_bytes=b"FakeZipBytes",

    #     attachment_filename="supporting_docs.zip",

    #     attachment_maintype="application",

    #     attachment_subtype="zip",

    # )
 
    # 2. Offer Accepted Email (PandaDoc webhook)

    print("\n--- Testing send_offer_accepted_email (PandaDoc) ---")

    send_offer_accepted_email(

        to_email=TEST_RECIPIENT,

        name="Abhi",

        onboarding_url="https://secure-upload-link.example.com"

    )
 
    # 3. Offer Accepted Email (DocuSign webhook)

    print("\n--- Testing send_offer_accepted_email (DocuSign) ---")

    send_offer_accepted_email(

        to_email=TEST_RECIPIENT,

        name="Abhi",

        onboarding_url="https://secure-upload-link.example.com"

    )
 
    # 4. Candidate Onboarding Submitted Email

    print("\n--- Testing send_candidate_onboarding_submitted_email ---")

    send_candidate_onboarding_submitted_email(

        to_email=TEST_RECIPIENT,

        candidate_name="Abhi"

    )
 
    # 5. HR Onboarding Submitted Email

    print("\n--- Testing send_hr_onboarding_submitted_email ---")

    send_hr_onboarding_submitted_email(

        hr_email=HR_RECIPIENT,

        candidate_name="Abhi",

        candidate_email=TEST_RECIPIENT,

        submitted_at=datetime.now()

    )
 
    # 6. Joining Email (Bulk Join)

    print("\n--- Testing send_joining_email (Bulk Join) ---")

    send_joining_email(

        to_email=TEST_RECIPIENT,

        name="Abhi",

        joining_date_str="15-09-2026",

        location="Hyderabad Office",

        reporting_time="9:00 AM",

        department="Engineering",

        reporting_manager="Jane Smith",

        custom_message="Please bring your original certificates for verification.",

        attachment_bytes=b"FakePDFBytes",

        attachment_filename="joining_letter.pdf"

    )
 
    # 7. Joining Email (Reassign Joining)

    print("\n--- Testing send_joining_email (Reassign Joining) ---")

    send_joining_email(

        to_email=TEST_RECIPIENT,

        name="Abhi",

        joining_date_str="20-09-2026",

        location="Hyderabad Office",

        reporting_time="10:00 AM",

        department="Engineering",

        reporting_manager="Jane Smith",

        custom_message="Your joining date has been rescheduled.",

        attachment_bytes=b"FakePDFBytes",

        attachment_filename="joining_letter.pdf"

    )
 
    # 8. OTP Email

    print("\n--- Testing send_otp_email ---")

    send_otp_email(

        to_email=TEST_RECIPIENT,

        otp="123456"

    )
 
if __name__ == "__main__":

    main()
 