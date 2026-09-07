import smtplib
from email.message import EmailMessage

# from ...config.env_loader import get_env_var
from datetime import datetime

import os
from dotenv import load_dotenv

load_dotenv()


def get_env_var(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{var_name}' not found.")
    return value


EMAIL_USER = get_env_var("EMAIL_USER")
EMAIL_PASSWORD = get_env_var("EMAIL_PASSWORD")
EMAIL_HOST = get_env_var("EMAIL_HOST")
EMAIL_PORT = int(get_env_var("EMAIL_PORT"))
# FRONTEND_URL = get_env_var("FRONTEND_URL")


def send_email(
    to_email: str,
    subject: str,
    content: str,
    cc_emails: list[str] | None = None,
    attachment_bytes: bytes | None = None,
    attachment_filename: str | None = None,
    attachment_maintype: str = "application",
    attachment_subtype: str = "zip",
):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    recipients = [to_email]
    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)
        recipients += cc_emails
    msg.set_content("This email requires an HTML-supported client.")
    msg.add_alternative(content, subtype="html")


    if attachment_bytes and attachment_filename:
        msg.add_attachment(
            attachment_bytes,
            maintype=attachment_maintype,
            subtype=attachment_subtype,
            filename=attachment_filename,
        )

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg, to_addrs=recipients)
        print(f"✅ Email sent to {recipients}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")


def send_offer_accepted_email(
    to_email: str,
    name: str,
    subject: str = "Offer Accepted – Next Steps",
    onboarding_url: str = "",
    cc_emails: list[str] | None = None,
):
    """
    Sends a professional offer acceptance email to the candidate.
    """
    
    
    content = f"""
    <!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Offer Acceptance</title>
</head>

<body style="margin:0; padding:0; background:#f3f5f9; font-family:Arial, Helvetica, sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0; background:#f3f5f9;">
<tr>
<td align="center">

    <!-- MAIN CARD -->
    <table width="640" cellpadding="0" cellspacing="0"
           style="background:#ffffff; border-radius:10px; border:1px solid #e0e4ec;">

        <!-- GRADIENT BAR -->
        <tr>
            <td style="height:8px; padding:0; margin:0; line-height:8px;">
                <!--[if gte mso 9]>
                <v:rect xmlns:v="urn:schemas-microsoft-com:vml"
                        fill="true" stroke="false"
                        style="width:640px;height:8px;">
                    <v:fill type="gradient" angle="90"
                            color="#0A1A44"
                            color2="#1A4DFF" />
                </v:rect>
                <![endif]-->
                <div style="background:linear-gradient(90deg, #0A1A44, #3B0E57, #1A4DFF);
                            height:8px; width:100%;"></div>
            </td>
        </tr>

        <!-- HEADER -->
        <tr>
            <td style="padding:32px 40px 20px;">
                <h2 style="margin:0; font-size:22px; color:#0A1A44; font-weight:700;">
                    Offer Acceptance
                </h2>
                <p style="margin:8px 0 0; font-size:14px; color:#666;">
                    Notification from Employee Onboarding System
                </p>
            </td>
        </tr>

        <!-- BODY -->
        <tr>
            <td style="padding:10px 40px 30px; font-size:15px;
                       color:#444; line-height:1.7;">

                <!-- Greeting -->
                <p style="margin:0 0 18px;">
                    Hello {name},
                </p>

                <!-- Main message -->
                <p style="margin:0 0 18px;">
                    Congratulations and thank you for accepting the offer!
                </p>
                <p style="margin:0 0 18px;">
                    We are delighted to welcome you to the team. Your acceptance marks the beginning of an exciting journey with us, and we are thrilled to have you onboard.
                </p>
                <p style="margin:0 0 18px;">
                    To proceed with the onboarding process, we kindly request you to upload the required documents using the secure link below:
                </p>

                <!-- Upload Link -->
                <div style="text-align:center; margin:20px 0;">
                    <a href="{onboarding_url}"
                       style="
                           background:#0A1A44;
                           padding:12px 32px;
                           color:#ffffff !important;
                           font-weight:600;
                           font-size:15px;
                           border-radius:6px;
                           text-decoration:none;
                           display:inline-block;
                           border:1px solid #1A4DFF;
                           font-family:Arial, Helvetica, sans-serif;
                       ">
                        🔗 Upload Documents
                    </a>
                </div>

                <p style="margin:0 0 18px;">
                    Please ensure that all documents are submitted at your earliest convenience so we can complete the remaining formalities without delay.
                </p>
                <p style="margin:0 0 25px;">
                    If you have any questions or need assistance, feel free to reach out to us.
                </p>
                <p style="margin:0 0 25px;">
                    Once again, welcome aboard — we look forward to working with you!
                </p>

                <!-- Closing message -->
                <p style="margin:25px 0 10px; color:#555;">
                    Warm regards,<br>
                    Employee Onboarding System<br>
                    Paves Technologies
                </p>

            </td>
        </tr>

        <!-- FOOTER -->
        <tr>
            <td style="background:#f6f7fb; text-align:center;
                       padding:14px; font-size:12px; color:#888;">
                © 2026 Paves Global Infotech Private Limited. All rights reserved.
            </td>
        </tr>

    </table>
</td>
</tr>
</table>

</body>
</html>
    """

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    recipients = [to_email]
    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)
        recipients += cc_emails
    msg.set_content("This email requires an HTML-supported client.")
    msg.add_alternative(content, subtype="html")


    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg, to_addrs=recipients)
        print(f"✅ Email sent to {recipients}")
        return "Email sent successfully"
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return f"Failed to send email: {e}"
    # ----------------------------


def send_otp_email(to_email: str, otp: str, subject: str = "Email Verification OTP"):
    """
    Sends a professional OTP verification email.
    """
    
    content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Email Verification</title>
</head>

<body style="margin:0; padding:0; background:#f3f5f9; font-family:Arial, Helvetica, sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0; background:#f3f5f9;">
<tr>
<td align="center">

    <!-- MAIN CARD -->
    <table width="640" cellpadding="0" cellspacing="0"
           style="background:#ffffff; border-radius:10px; border:1px solid #e0e4ec;">

        <!-- GRADIENT BAR -->
        <tr>
            <td style="height:8px; padding:0; margin:0; line-height:8px;">
                <!--[if gte mso 9]>
                <v:rect xmlns:v="urn:schemas-microsoft-com:vml"
                        fill="true" stroke="false"
                        style="width:640px;height:8px;">
                    <v:fill type="gradient" angle="90"
                            color="#0A1A44"
                            color2="#1A4DFF" />
                </v:rect>
                <![endif]-->
                <div style="background:linear-gradient(90deg, #0A1A44, #3B0E57, #1A4DFF);
                            height:8px; width:100%;"></div>
            </td>
        </tr>

        <!-- HEADER -->
        <tr>
            <td style="padding:32px 40px 20px;">
                <h2 style="margin:0; font-size:22px; color:#0A1A44; font-weight:700;">
                    Email Verification
                </h2>
                <p style="margin:8px 0 0; font-size:14px; color:#666;">
                    Part of Employee Onboarding Process
                </p>
            </td>
        </tr>

        <!-- BODY -->
        <tr>
            <td style="padding:10px 40px 30px; font-size:15px;
                       color:#444; line-height:1.7;">

                <!-- Greeting -->
                <p style="margin:0 0 18px;">
                    Hello {to_email},
                </p>

                <!-- Main message -->
                <p style="margin:0 0 18px;">
                    We received a request to verify your email address as part of the Employee Onboarding process.
                </p>

                <p style="margin:0 0 18px;">
                    Your One-Time Password (OTP) is:
                </p>

                <!-- OTP Box -->
                <div style="text-align:center; margin:20px 0;">
                    <h2 style="font-size:28px; font-weight:bold; color:#0A1A44; margin:0;">
                        🔐 OTP: {otp}
                    </h2>
                    <p style="margin:10px 0; color:#555;">
                        This OTP is valid for the next 5 minutes. Please do not share this OTP with anyone for security reasons.
                    </p>
                </div>

                <p style="margin:0 0 25px;">
                    If you did not request this verification, please ignore this email.
                </p>

                <!-- Closing message -->
                <p style="margin:25px 0 10px; color:#555;">
                    Warm regards,<br>
                    Employee Onboarding System<br>
                    Paves Technologies
                </p>

            </td>
        </tr>
 
        <!-- FOOTER -->
        <tr>
            <td style="background:#f6f7fb; text-align:center;
                       padding:14px; font-size:12px; color:#888;">
                © 2026 Paves Global Infotech Private Limited. All rights reserved.
            </td>
        </tr>

    </table>
</td>
</tr>
</table>

</body>
</html>
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content("This email requires an HTML-supported client.")
    msg.add_alternative(content, subtype="html")


    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ OTP email sent to {to_email}")
        return "OTP email sent successfully"
    except Exception as e:
        print(f"❌ Failed to send OTP email to {to_email}: {e}")
        return f"Failed to send OTP email: {e}"


def send_candidate_onboarding_submitted_email(
    to_email: str,
    candidate_name: str,
    subject: str = "Onboarding Submitted Successfully",
):
    """
    Email sent to candidate after final onboarding submit
    """
    
    content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Onboarding Notification</title>
</head>

<body style="margin:0; padding:0; background:#f3f5f9; font-family:Arial, Helvetica, sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0; background:#f3f5f9;">
<tr>
<td align="center">

    <!-- MAIN CARD -->
    <table width="640" cellpadding="0" cellspacing="0"
           style="background:#ffffff; border-radius:10px; border:1px solid #e0e4ec;">

        <!-- GRADIENT BAR -->
        <tr>
            <td style="height:8px; padding:0; margin:0; line-height:8px;">
                <!--[if gte mso 9]>
                <v:rect xmlns:v="urn:schemas-microsoft-com:vml"
                        fill="true" stroke="false"
                        style="width:640px;height:8px;">
                    <v:fill type="gradient" angle="90"
                            color="#0A1A44"
                            color2="#1A4DFF" />
                </v:rect>
                <![endif]-->
                <div style="background:linear-gradient(90deg, #0A1A44, #3B0E57, #1A4DFF);
                            height:8px; width:100%;"></div>
            </td>
        </tr>

        <!-- HEADER -->
        <tr>
            <td style="padding:32px 40px 20px;">
                <h2 style="margin:0; font-size:22px; color:#0A1A44; font-weight:700;">
                    Onboarding Notification
                </h2>
                <p style="margin:8px 0 0; font-size:14px; color:#666;">
                    Notification from Employee Onboarding System
                </p>
            </td>
        </tr>

        <!-- BODY -->
        <tr>
            <td style="padding:10px 40px 30px; font-size:15px;
                       color:#444; line-height:1.7;">

                <!-- Greeting -->
                <p style="margin:0 0 18px;">
                    Hello {candidate_name},
                </p>

                <!-- Main message -->
                <p style="margin:0 0 18px;">
                    Your onboarding details have been successfully submitted.
                </p>
                <p style="margin:0 0 18px;">
                    Our HR team will review your information and verify the submitted documents.
                </p>
                <p style="margin:0 0 18px;">
                    You will be notified if any additional action is required from your side.
                </p>
                <p style="margin:0 0 25px;">
                    Thank you for completing the onboarding process.
                </p>

                <!-- Closing message -->
                <p style="margin:25px 0 10px; color:#555;">
                    Warm regards,<br>
                    Employee Onboarding System<br>
                    Paves Technologies
                </p>

                <!-- CTA BUTTON -->
                <div style="text-align:center; margin:32px 0;">
                    <a href="https://d2id2c6d521acd.cloudfront.net"
                       style="
                           background:#0A1A44;
                           padding:12px 32px;
                           color:#ffffff !important;
                           font-weight:600;
                           font-size:15px;
                           border-radius:6px;
                           text-decoration:none;
                           display:inline-block;
                           border:1px solid #1A4DFF;
                           font-family:Arial, Helvetica, sans-serif;
                       ">
                        View Onboarding Portal
                    </a>
                </div>

            </td>
        </tr>

        <!-- FOOTER -->
        <tr>
            <td style="background:#f6f7fb; text-align:center;
                       padding:14px; font-size:12px; color:#888;">
                © 2026 Paves Global Infotech Private Limited. All rights reserved.
            </td>
        </tr>

    </table>
</td>
</tr>
</table>

</body>
</html>

"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content("This email requires an HTML-supported client.")
    msg.add_alternative(content, subtype="html")


    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Candidate onboarding email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send candidate onboarding email: {e}")


def send_hr_onboarding_submitted_email(
    hr_email: str,
    candidate_name: str,
    candidate_email: str,
    submitted_at: datetime,
    subject: str = "Candidate Onboarding Submitted",
):
    """
    Email sent to HR when candidate submits onboarding
    """

    submitted_time = submitted_at.strftime("%d-%m-%Y %H:%M:%S")

    content = f"""
Hello HR Team,

A candidate has completed the onboarding submission.

Candidate Details:
-------------------
Candidate Name : {candidate_name}
Candidate Email : {candidate_email}
Submitted At   : {submitted_time}

Regards,
Employee Onboarding System
Paves Technologies
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = hr_email
    msg.set_content("This email requires an HTML-supported client.")
    msg.add_alternative(content, subtype="html")

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ HR onboarding notification email sent to {hr_email}")
    except Exception as e:
        print(f"❌ Failed to send HR onboarding email: {e}")


def send_joining_email(
    to_email: str,
    name: str,
    joining_date_str: str,
    location: str,
    reporting_time: str,
    department: str,
    reporting_manager: str,
    custom_message: str | None = None,
    attachment_bytes: bytes | None = None,
    attachment_filename: str | None = None,
):
    subject = "Joining Letter – Welcome Aboard"

    html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">

    <p>Dear {name},</p>

    <p>
      We are delighted to welcome you to <b>Paves Technologies</b>.
      We are excited to have you join our team and look forward to
      working with you as part of our organization.
    </p>

    <p>
      This email is to confirm your joining details, which are mentioned below
      for your reference.
    </p>

    <p>
    You are scheduled to join us on <b>{joining_date_str}</b> at <b>{reporting_time}</b>.
    Your work location will be <b>{location}</b>.
    {f'You will be reporting to <b>{reporting_manager}</b>. You will be part of the <b>{department}</b> department.' if reporting_manager else ''}
    </p>



    <p>
      On your first day, we kindly request you to report our HR desk and submit the necessary documents for verification. Our HR team will assist you with the onboarding formalities and guide you through the initial processes.
    </p>

    {f'''
    <p>
      <b>Additional Information:</b><br/>
      {custom_message}
    </p>
    ''' if custom_message else ""}

    <p>
      Should you have any questions or require further clarification before your
      joining date, please feel free to contact the HR team. We will be happy to assist you.
    </p>

    <p>
      We wish you every success in your new role and look forward to a positive and
      rewarding association with you.
    </p>

    <br/>

    <p>
      Warm regards,<br/>
      <b>HR Team</b><br/>
      Paves Technologies
    </p>

  </body>
</html>
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content(html_body, subtype="html")

    if attachment_bytes:
        msg.add_attachment(
            attachment_bytes,
            maintype="application",
            subtype="pdf",
            filename=attachment_filename or "joining_letter.pdf",
        )

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"Joining email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send joining email: {e}")

    # helper function to add cc to mails


def send_smtp_email(
    msg: EmailMessage, to_emails: list[str], cc_emails: list[str] | None = None
):
    recipients = to_emails.copy()

    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)
        recipients.extend(cc_emails)

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg, to_addrs=recipients)

        print(f"✅ Email sent to {recipients}")

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
