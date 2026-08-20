import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.core import environmentVariables

logger = logging.getLogger("copchat.email")
config = environmentVariables()


def send_registration_email(
    to_email: str,
    full_name: str,
    service_id: str,
    temp_password: str,
) -> bool:
    """
    Background worker function to send welcome email with temporary credentials.
    Supports TLS and SSL configurations from environment variables.
    """
    smtp_host = config.smtp_host
    smtp_port = config.smtp_port
    smtp_user = config.smtp_user
    smtp_password = config.smtp_password
    from_email = config.smtp_from_email
    from_name = config.smtp_from_name

    subject = "Welcome to CopChat Portal - Login Credentials"

    plain_text_content = f"""Hello {full_name},

Welcome to CopChat - The Secure Police Communication Portal.

Your account registration has been completed successfully. Please use the temporary credentials below for your initial login:

----------------------------------------
Service ID  : {service_id}
Email       : {to_email}
Temporary Password : {temp_password}
----------------------------------------

IMPORTANT:
This is a one-time temporary password. Upon your first login, you will be required to set up a new permanent password to secure your account.

Stay Safe & Connected,
CopChat Administration Team
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Welcome to CopChat</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f6f9;
            margin: 0;
            padding: 20px;
            color: #333333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
            border: 1px solid #e1e8ed;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #ffffff;
            padding: 25px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        .content {{
            padding: 30px;
        }}
        .greeting {{
            font-size: 18px;
            font-weight: 600;
            color: #1e3c72;
            margin-top: 0;
        }}
        .credentials-box {{
            background-color: #f8fafc;
            border-left: 4px solid #2a5298;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .field {{
            margin-bottom: 10px;
            font-size: 14px;
        }}
        .field-name {{
            font-weight: bold;
            color: #555555;
            display: inline-block;
            width: 160px;
        }}
        .field-value {{
            font-family: monospace;
            font-size: 15px;
            color: #111827;
            background: #e2e8f0;
            padding: 3px 8px;
            border-radius: 4px;
        }}
        .notice {{
            background-color: #fffbeb;
            border: 1px solid #fef3c7;
            color: #b45309;
            padding: 15px;
            border-radius: 6px;
            font-size: 13px;
            line-height: 1.5;
            margin-top: 20px;
        }}
        .footer {{
            background-color: #f8fafc;
            padding: 15px 30px;
            text-align: center;
            font-size: 12px;
            color: #718096;
            border-top: 1px solid #edf2f7;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CopChat Security Portal 🛡️</h1>
        </div>
        <div class="content">
            <p class="greeting">Hello {full_name},</p>
            <p>Welcome to <strong>CopChat</strong>, the secure communication portal for law enforcement personnel.</p>
            <p>Your account has been successfully created. Please use the following one-time credentials to perform your initial login:</p>
            
            <div class="credentials-box">
                <div class="field">
                    <span class="field-name">Service ID:</span>
                    <span class="field-value">{service_id}</span>
                </div>
                <div class="field">
                    <span class="field-name">Registered Email:</span>
                    <span class="field-value">{to_email}</span>
                </div>
                <div class="field">
                    <span class="field-name">Temporary Password:</span>
                    <span class="field-value">{temp_password}</span>
                </div>
            </div>

            <div class="notice">
                <strong>⚠️ Action Required:</strong><br>
                This temporary password is provided for one-time setup. Upon logging into the portal, you will be prompted to set a new permanent password.
            </div>
        </div>
        <div class="footer">
            &copy; CopChat Police Communication System. Confidential & Secure.
        </div>
    </div>
</body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email

    msg.attach(MIMEText(plain_text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    if not smtp_user or not smtp_password:
        logger.warning(
            f"SMTP credentials not configured. Email to {to_email} skipped. "
            f"Temporary Password generated: {temp_password}"
        )
        return False

    try:
        if config.smtp_use_ssl:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15) as server:
                server.login(smtp_user, smtp_password)
                server.sendmail(from_email, [to_email], msg.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                if config.smtp_use_tls:
                    server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(from_email, [to_email], msg.as_string())
        
        logger.info(f"Registration welcome email successfully sent to {to_email}")
    except Exception:
        logger.exception(f"Failed to send registration email to {to_email}")
        return False
