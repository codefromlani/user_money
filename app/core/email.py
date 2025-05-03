import os
import aiosmtplib
from email.message import EmailMessage
from pydantic import EmailStr


EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "465"))
EMAIL_USERNAME= os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD= os.getenv("EMAIL_PASSWORD")


async def send_verification_email(email: EmailStr, token: str):
    message = EmailMessage()
    message["FROM"] = EMAIL_USERNAME
    message["TO"] = email
    message["Subject"] = "Verify your email address"
    verification_url = f"http://localhost:8000/auth/verify?token={token}"
    message.add_alternative(
    f"""
<html>
  <body>
    <p>Hi there,</p>
    <p>Thanks for registering! Please click the link below to verify your email:</p>
    <p><a href="{verification_url}">Verify Email</a></p>
    <p>If you didn’t request this, you can ignore this email.</p>
    <br>
    <p>Best regards,<br>Your App Team</p>
  </body>
</html>
""",
    subtype="html",
)
    
    try:
        await aiosmtplib.send(
            message,
            hostname=EMAIL_HOST,
            port=EMAIL_PORT,
            username=EMAIL_USERNAME,
            password=EMAIL_PASSWORD,
            use_tls=True
        )
    except Exception as e:
        print(f"Error sending email: {e}")
        raise

async def send_reset_email(email: EmailStr, reset_token: str):
    message = EmailMessage()
    message["FROM"] = EMAIL_USERNAME
    message["TO"] = email
    message["Subject"] = "Password Reset Request"
    reset_link = f"http://localhost:8000/auth/password-reset/verify?reset_token={reset_token}"
    message.add_alternative(
    f"""
<html>
  <body>
    <p>Hello,</p>
    <p>We received a request to reset the password for your account.</p>
    <p>Please click the link below to reset your password:</p>
    <p><a href="{reset_link}">Reset Password</a></p>
    <p>If you didn’t request this, you can ignore this email.</p>
    <br>
    <p>Best regards,<br>Your App Team</p>
  </body>
</html>
""",
    subtype="html",
)
    
    try:
        await aiosmtplib.send(
            message,
            hostname=EMAIL_HOST,
            port=EMAIL_PORT,
            username=EMAIL_USERNAME,
            password=EMAIL_PASSWORD,
            use_tls=True
        )
    except Exception as e:
        print(f"Error sending email: {e}")
        raise
