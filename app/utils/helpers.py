# app/utils/helpers.py

import random
import string


def generate_verification_code(length: int = 6):
    return "".join(random.choices(string.digits, k=length))


def mask_ip(ip: str) -> str:
    """Mask IP for GDPR compliance."""
    if ":" in ip:  # IPv6
        parts = ip.split(":")
        return ":".join(parts[:4]) + ":xxxx:xxxx"
    else:  # IPv4
        parts = ip.split(".")
        return ".".join(parts[:2] + ["xxx"])


def mask_email(email: str) -> str:
    """
    Masks an email address for logging.

    Example:
        "johndoe@example.com" -> "joh***@example.com"
    """
    try:
        local, domain = email.split("@")
        visible = 3 if len(local) > 3 else len(local)
        masked_local = local[:visible] + "*" * (len(local) - visible)
        return f"{masked_local}@{domain}"
    except Exception:
        return "****@****"
