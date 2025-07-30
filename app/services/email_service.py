# app/services/email_service.py

from fastapi_mail import FastMail, MessageSchema, MessageType
from jinja2 import Template

from app.core.config import TEMPLATES_DIR, mail_config


fm = FastMail(mail_config)


async def send_verification_email(email_to: str, code: str):
    template_path = TEMPLATES_DIR / "auth" / "email-verification.html"
    template_str = template_path.read_text()
    rendered = Template(template_str).render(verification_code=code)

    message = MessageSchema(
        subject=f"{code} is your verification code",
        recipients=[email_to],
        body=rendered,
        subtype=MessageType.html
    )

    try:
        await fm.send_message(message=message)
    except Exception as e:
        # TODO: add logging
        print(f"Failed to send verification email to {email_to}: {e}")


async def send_welcome_email(email_to: str):
    template_path = TEMPLATES_DIR / "account" / "user-registration.html"
    template_str = template_path.read_text()
    rendered = Template(template_str).render()

    message = MessageSchema(
        subject="Welcome to PamietamPsa",
        recipients=[email_to],
        body=rendered,
        subtype=MessageType.html
    )

    try:
        await fm.send_message(message=message)
    except Exception as e:
        # TODO: add logging
        print(f"Failed to send welcome email to {email_to}: {e}")
