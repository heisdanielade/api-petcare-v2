# app/services/email_service.py

from fastapi_mail import FastMail, MessageSchema, MessageType
from jinja2 import Template
from app.core.logging import logger
from app.utils.helpers import mask_email
from app.core.config import TEMPLATES_DIR, mail_config, settings


fm = FastMail(mail_config)


class EmailService:
    @staticmethod
    async def _send_email(email_to: str, subject_template: str, template_rel_path: str, context: dict = None):
        """
        Internal helper to render and send HTML emails with templated subjects.
        :param email_to: Recipient email
        :param subject_template: Subject line (can contain template variables, e.g. "{code} is your code")
        :param template_rel_path: Path relative to TEMPLATES_DIR
        :param context: Dict of template variables
        """
        context = context or {}

        try:
            # Render subject and body using same context
            subject = Template(subject_template).render(context)

            template_path = TEMPLATES_DIR / template_rel_path
            template_str = template_path.read_text()
            body = Template(template_str).render(context)

            message = MessageSchema(
                subject=subject,
                recipients=[email_to],
                body=body,
                subtype=MessageType.html,
            )

            await fm.send_message(message=message)

        except Exception:
            logger.exception(
                msg=f"Failed to send email '{subject_template}' to {mask_email(email_to)}"
            )

    @staticmethod
    async def send_verification_email(email_to: str, code: str):
        await EmailService._send_email(
            email_to=email_to,
            subject_template="{{ code }} is your verification code",
            template_rel_path="auth/email-verification.html",
            context={"code": code},
        )

    @staticmethod
    async def send_welcome_email(email_to: str):
        await EmailService._send_email(
            email_to=email_to,
            subject_template="Welcome to PamietamPsa",
            template_rel_path="account/user-registration.html",
        )

    @staticmethod
    async def send_password_reset_email(email_to: str, reset_token: str):
        reset_link = f"{settings.FRONTEND_PROD_URL}/u/reset-password?token={reset_token}"
        await EmailService._send_email(
            email_to=email_to,
            subject_template="You requested a Password Reset",
            template_rel_path="auth/password-reset.html",
            context={"reset_link": reset_link},
        )

    @staticmethod
    async def send_password_reset_notification_email(email_to: str, reset_time: str):
        await EmailService._send_email(
            email_to=email_to,
            subject_template="You changed your Password",
            template_rel_path="auth/notify-password-reset.html",
            context={"reset_time": reset_time},
        )

    @staticmethod
    async def send_account_deletion_email(email_to: str, verification_code: str):
        await EmailService._send_email(
            email_to=email_to,
            subject_template="Account Deletion Confirmation",
            template_rel_path="account/account-deletion.html",
            context={"verification_code": verification_code},
        )

    @staticmethod
    async def send_account_deletion_scheduled_email(email_to: str):
        await EmailService._send_email(
            email_to=email_to,
            subject_template="Account Scheduled for Deletion",
            template_rel_path="account/scheduled-account-deletion.html",
        )

    @staticmethod
    async def send_account_locked_email(email_to: str):
        await EmailService._send_email(
            email_to=email_to,
            subject_template="Your account has been locked",
            template_rel_path="account/account-locked.html",
        )
