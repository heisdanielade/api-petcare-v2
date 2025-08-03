# app/services/email_service.py

from fastapi_mail import FastMail, MessageSchema, MessageType
from jinja2 import Template

from app.core.config import TEMPLATES_DIR, mail_config, settings


fm = FastMail(mail_config)


class EmailService:

    @staticmethod
    async def send_verification_email(email_to: str, code: str):
        template_path = TEMPLATES_DIR / "auth" / "email-verification.html"
        template_str = template_path.read_text()
        rendered = Template(template_str).render(verification_code=code)

        message = MessageSchema(
            subject=f"{code} is your verification code",
            recipients=[email_to],
            body=rendered,
            subtype=MessageType.html)

        try:
            await fm.send_message(message=message)
        except Exception as e:
            # TODO: add logging
            print(f"Failed to send verification email to {email_to}: {e}")

    @staticmethod
    async def send_welcome_email(email_to: str):
        template_path = TEMPLATES_DIR / "account" / "user-registration.html"
        template_str = template_path.read_text()
        rendered = Template(template_str).render()

        message = MessageSchema(
            subject="Welcome to PamietamPsa",
            recipients=[email_to],
            body=rendered,
            subtype=MessageType.html)

        try:
            await fm.send_message(message=message)
        except Exception as e:
            # TODO: add logging
            print(f"Failed to send welcome email to {email_to}: {e}")

    @staticmethod
    async def send_password_reset_email(email_to: str, reset_token: str):
        reset_link = f"{settings.FRONTEND_PROD_URL}/u/reset-password?token={reset_token}"
        template_path = TEMPLATES_DIR / "auth" / "password-reset.html"
        template_str = template_path.read_text()
        rendered = Template(template_str).render(reset_link=reset_link)

        message = MessageSchema(
            subject="You requested a Password Reset",
            recipients=[email_to],
            body=rendered,
            subtype=MessageType.html)

        try:
            await fm.send_message(message=message)
        except Exception as e:
            # TODO: add logging
            print(f"Failed to send password reset email to {email_to}: {e}")

    @staticmethod
    async def send_password_reset_notification_email(email_to: str, reset_time: str):
        template_path = TEMPLATES_DIR / "auth" / "notify-password-reset.html"
        template_str = template_path.read_text()
        rendered = Template(template_str).render(reset_time=reset_time)

        message = MessageSchema(
            subject="You changed your Password",
            recipients=[email_to],
            body=rendered,
            subtype=MessageType.html)

        try:
            await fm.send_message(message=message)
        except Exception as e:
            # TODO: add logging
            print(
                f"Failed to password reset notification email to {email_to}: {e}")
