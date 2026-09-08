import smtplib
from email.message import EmailMessage
from datetime import datetime
import os
from dotenv import load_dotenv
from html import escape
import re

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
FRONTEND_URL = get_env_var("FRONTEND_URL")


def send_email(
    to_email: str,
    subject: str,
    content: str = "",
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

    employee_name = "User"

    if "–" in subject:
        employee_name = subject.split("–", 1)[1].strip()
    elif " - " in subject:
        employee_name = subject.split(" - ", 1)[1].strip()
    elif "-" in subject:
        employee_name = subject.split("-", 1)[1].strip()

    if not content:
        content = f"""Dear Consultancy Team,

Please find the supporting documents for {employee_name} attached with this email for the background verification process.

Employee Name: {employee_name}
Employee ID: Not provided in test

Verification Checks Requested:
Not provided in test

Kindly proceed with the background verification and share the verification results with us once completed.

If you require any additional information or documents, please feel free to contact the HR team.

Regards,
HR Team
Paves Technologies"""

    employee_id = ""
    verification_checks = ""

    employee_match = re.search(
        r"Employee Name\s*:\s*(.+)",
        content,
        re.IGNORECASE
    )

    employee_id_match = re.search(
        r"Employee ID\s*:\s*(.+)",
        content,
        re.IGNORECASE
    )

    checks_match = re.search(
        r"Verification Checks Requested\s*:\s*(.*?)(?:\n\s*\n|\Z)",
        content,
        re.IGNORECASE | re.DOTALL
    )

    if employee_match:
        employee_name = employee_match.group(1).strip()

    if employee_id_match:
        employee_id = employee_id_match.group(1).strip()

    if checks_match:
        verification_checks = checks_match.group(1).strip()

    content_without_details = content

    if employee_match:
        content_without_details = re.sub(
            r"Employee Name\s*:\s*.+\n?",
            "",
            content_without_details,
            flags=re.IGNORECASE
        )

    if employee_id_match:
        content_without_details = re.sub(
            r"Employee ID\s*:\s*.+\n?",
            "",
            content_without_details,
            flags=re.IGNORECASE
        )

    if checks_match:
        content_without_details = re.sub(
            r"Verification Checks Requested\s*:\s*.*?(?:\n\s*\n|\Z)",
            "",
            content_without_details,
            flags=re.IGNORECASE | re.DOTALL
        )

    content_without_details = content_without_details.strip()

    greeting = ""
    closing = ""

    greeting_match = re.match(
        r"^\s*(Dear\s+.+?,)\s*",
        content_without_details,
        re.IGNORECASE
    )

    if greeting_match:
        greeting = greeting_match.group(1)
        content_without_details = content_without_details[
            greeting_match.end():
        ].strip()

    closing_match = re.search(
        r"\n\s*(Regards,|Warm regards,|Best regards,)\s*$",
        content_without_details,
        re.IGNORECASE
    )

    if closing_match:
        closing = content_without_details[closing_match.start():].strip()
        content_without_details = content_without_details[
            :closing_match.start()
        ].strip()

    if not greeting:
        greeting = "Dear Consultancy Team,"

    if not closing:
        closing = """Regards,
HR Team
Paves Technologies"""

    message_body = escape(content_without_details).replace("\n", "<br>")

    details_rows = ""

    if employee_name:
        details_rows += f"""
<tr>
<td style="padding:8px 0; width:150px; font-weight:bold;">
Employee Name
</td>
<td style="padding:8px 0;">
{escape(employee_name)}
</td>
</tr>
"""

    if employee_id:
        details_rows += f"""
<tr>
<td style="padding:8px 0; width:150px; font-weight:bold;">
Employee ID
</td>
<td style="padding:8px 0;">
{escape(employee_id)}
</td>
</tr>
"""

    if verification_checks:
        checks_html = escape(verification_checks).replace("\n", "<br>")

        details_rows += f"""
<tr>
<td style="padding:8px 0; width:150px; font-weight:bold; vertical-align:top;">
Verification Checks
</td>
<td style="padding:8px 0;">
{checks_html}
</td>
</tr>
"""

    details_section = ""

    if details_rows:
        details_section = f"""
<div style="margin:25px 0 15px;">
<div style="font-size:15px; font-weight:700; color:#0A1A44;
border-left:4px solid #1A4DFF; padding-left:10px;">
Verification Details
</div>
</div>

<table width="100%" cellpadding="0" cellspacing="0"
style="background:#fafbff; border:1px solid #e2e6ef; border-radius:8px;">
<tr>
<td style="padding:20px 25px;">
<table width="100%" cellpadding="0" cellspacing="0"
style="font-size:14px; color:#333;">
{details_rows}
</table>
</td>
</tr>
</table>
"""

    closing_html = escape(closing).replace("\n", "<br>")

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{escape(subject)}</title>
</head>

<body style="margin:0; padding:0; background:#f3f5f9; font-family:Arial, Helvetica, sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0"
style="padding:40px 0; background:#f3f5f9;">
<tr>
<td align="center">

<table width="640" cellpadding="0" cellspacing="0"
style="background:#ffffff; border-radius:10px; border:1px solid #e0e4ec;">

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
height:8px; width:100%;">
</div>

</td>
</tr>

<tr>
<td style="padding:32px 40px 20px;">

<h2 style="margin:0; font-size:22px; color:#0A1A44; font-weight:700;">
{escape(subject)}
</h2>

<p style="margin:8px 0 0; font-size:14px; color:#666;">
Notification from Employee Onboarding System
</p>

</td>
</tr>

<tr>
<td style="padding:10px 40px 30px; font-size:15px;
color:#444; line-height:1.7;">

<p style="margin:0 0 18px;">
{escape(greeting)}
</p>

<p style="margin:0 0 25px;">
{message_body}
</p>

{details_section}

<p style="margin:25px 0 10px; color:#555;">
{closing_html}
</p>

<div style="text-align:center; margin:32px 0;">

<a href="{escape(FRONTEND_URL)}"
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
View in Employee Onboarding System
</a>

</div>

</td>
</tr>

<tr>
<td style="background:#f6f7fb; text-align:center;
padding:14px; font-size:12px; color:#888;">
© 2024 Paves Global Infotech Private Limited. All rights reserved.
</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""

    msg.set_content(content)

    msg.add_alternative(
        html_content,
        subtype="html"
    )

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
            smtp.login(
                EMAIL_USER,
                EMAIL_PASSWORD
            )
            smtp.send_message(
                msg,
                to_addrs=recipients
            )

        print(f"✅ Email sent to {recipients}")
        return "Email sent successfully"

    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        raise


def send_offer_accepted_email(
    to_email: str,
    name: str,
    subject: str = "Offer Accepted – Next Steps",
    onboarding_url: str = "",
    cc_emails: list[str] | None = None,
):
    if not onboarding_url:
        onboarding_url = FRONTEND_URL

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
                           background:#1A4DFF;
                           padding:12px 32px;
                           color:#ffffff !important;
                           font-weight:600;
                           font-size:15px;
                           border-radius:6px;
                           text-decoration:none;
                           display:inline-block;                          
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
            smtp.login(
                EMAIL_USER,
                EMAIL_PASSWORD
            )
            smtp.send_message(
                msg,
                to_addrs=recipients
            )

        print(f"✅ Email sent to {recipients}")
        return "Email sent successfully"

    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return f"Failed to send email: {e}"


def send_otp_email(to_email: str, otp: str, subject: str = "Email Verification OTP",name: str = "User"):
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
            smtp.login(
                EMAIL_USER,
                EMAIL_PASSWORD
            )
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
                           background:#1A4DFF;
                           padding:12px 32px;
                           color:#ffffff !important;
                           font-weight:600;
                           font-size:15px;
                           border-radius:6px;
                           text-decoration:none;
                           display:inline-block;
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
            smtp.login(
                EMAIL_USER,
                EMAIL_PASSWORD
            )
            smtp.send_message(msg)

        print(f"✅ Candidate onboarding email sent to {to_email}")

    except Exception as e:
        print(f"❌ Failed to send candidate onboarding email to {to_email}: {e}")


def send_hr_onboarding_submitted_email(
    hr_email: str,
    candidate_name: str,
    candidate_email: str,
    submitted_at: datetime,
    subject: str = "Candidate Onboarding Submitted",
):
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
            smtp.login(
                EMAIL_USER,
                EMAIL_PASSWORD
            )
            smtp.send_message(msg)

        print(f"✅ HR onboarding notification email sent to {hr_email}")

    except Exception as e:
        print(f"❌ Failed to send HR onboarding email to {hr_email}: {e}")


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

    content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{subject}</title>
</head>

<body style="margin:0; padding:0; background:#f3f5f9; font-family:Arial, Helvetica, sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0"
style="padding:40px 0; background:#f3f5f9;">
<tr>
<td align="center">

<table width="640" cellpadding="0" cellspacing="0"
style="background:#ffffff; border-radius:10px; border:1px solid #e0e4ec;">

<tr>
<td style="height:8px; padding:0; margin:0; line-height:8px;">

<div style="background:linear-gradient(90deg, #0A1A44, #3B0E57, #1A4DFF);
height:8px; width:100%;">
</div>

</td>
</tr>

<tr>
<td style="padding:32px 40px 20px;">

<h2 style="margin:0; font-size:22px; color:#0A1A44; font-weight:700;">
{subject}
</h2>

<p style="margin:8px 0 0; font-size:14px; color:#666;">
Notification from Employee Onboarding System
</p>

</td>
</tr>

<tr>
<td style="padding:10px 40px 30px; font-size:15px;
color:#444; line-height:1.7;">

<p style="margin:0 0 18px;">
Dear {name},
</p>

<p style="margin:0 0 25px;">
We are delighted to welcome you to <b>Paves Technologies</b>.
We are excited to have you join our team and look forward to
working with you as part of our organization.
</p>

<p style="margin:0 0 25px;">
This email is to confirm your joining details, which are mentioned below
for your reference.
</p>

<div style="margin:0 0 15px;">
<div style="font-size:15px; font-weight:700; color:#0A1A44;
border-left:4px solid #1A4DFF; padding-left:10px;">
Joining Details
</div>
</div>

<table width="100%" cellpadding="0" cellspacing="0"
style="background:#fafbff; border:1px solid #e2e6ef; border-radius:8px;">

<tr>
<td style="padding:20px 25px;">

<table width="100%" cellpadding="0" cellspacing="0"
style="font-size:14px; color:#333;">

<tr>
<td style="padding:8px 0; width:150px; font-weight:bold;">
Joining Date
</td>
<td style="padding:8px 0;">
{joining_date_str}
</td>
</tr>

<tr>
<td style="padding:8px 0; width:150px; font-weight:bold;">
Reporting Time
</td>
<td style="padding:8px 0;">
{reporting_time}
</td>
</tr>

<tr>
<td style="padding:8px 0; width:150px; font-weight:bold;">
Location
</td>
<td style="padding:8px 0;">
{location}
</td>
</tr>

<tr>
<td style="padding:8px 0; width:150px; font-weight:bold;">
Department
</td>
<td style="padding:8px 0;">
{department}
</td>
</tr>

<tr>
<td style="padding:8px 0; width:150px; font-weight:bold;">
Reporting Manager
</td>
<td style="padding:8px 0;">
{reporting_manager}
</td>
</tr>

</table>

</td>
</tr>

</table>

<p style="margin:25px 0 10px; color:#555;">
On your first day, please report to the HR desk and submit the necessary
documents for verification. Our HR team will assist you with the onboarding
formalities and guide you through the initial processes.
</p>

{f'''
<p style="margin:25px 0 10px; color:#555;">
<b>Additional Information:</b><br/>
{custom_message}
</p>
''' if custom_message else ""}

<p style="margin:25px 0 10px; color:#555;">
Should you have any questions or require further clarification before your
joining date, please feel free to contact the HR team. We will be happy to assist you.
</p>

<p style="margin:25px 0 10px; color:#555;">
We wish you every success in your new role and look forward to a positive and
rewarding association with you.
</p>

<div style="text-align:center; margin:32px 0;">

<a href="{FRONTEND_URL}"
style="
background:#1A4DFF;
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
View in Employee Onboarding System
</a>

</div>

</td>
</tr>

<tr>
<td style="background:#f6f7fb; text-align:center;
padding:14px; font-size:12px; color:#888;">
© 2024 Paves Global Infotech Private Limited. All rights reserved.
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

    msg.set_content(
        f"Dear {name}\n\n"
        f"We are delighted to welcome you to Paves Technologies.\n\n"
        f"Joining Date: {joining_date_str}\n"
        f"Reporting Time: {reporting_time}\n"
        f"Location: {location}\n"
        f"Department: {department}\n"
        f"Reporting Manager: {reporting_manager}\n\n"
        f"Regards,\n"
        f"HR Team\n"
        f"Paves Technologies"
    )

    msg.add_alternative(
        content,
        subtype="html"
    )

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
            smtp.login(
                EMAIL_USER,
                EMAIL_PASSWORD
            )
            smtp.send_message(msg)

        print(f"Joining email sent to {to_email}")

    except Exception as e:
        print(f"❌ Failed to send joining email: {e}")
        raise
def send_smtp_email(
    msg: EmailMessage,
    to_emails: list[str],
    cc_emails: list[str] | None = None
):
    recipients = to_emails.copy()

    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)
        recipients.extend(cc_emails)

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(
                EMAIL_USER,
                EMAIL_PASSWORD
            )
            smtp.send_message(
                msg,
                to_addrs=recipients
            )

        print(f"✅ Email sent to {recipients}")

    except Exception as e:
        print(f"❌ Failed to send email: {e}")