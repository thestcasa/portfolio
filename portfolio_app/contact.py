from __future__ import annotations

import html
import os
import time
from collections import defaultdict, deque
from typing import Literal
from uuid import uuid4

import httpx
from fastapi import Request
from pydantic import BaseModel, ConfigDict, EmailStr, ValidationError, field_validator

from .content import load_data


class ContactPayload(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    email: EmailStr
    organization: str = ""
    inquiry_type: Literal["hiring", "consulting", "collaboration", "other"]
    message: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not 2 <= len(value) <= 80:
            raise ValueError("Please enter a name between 2 and 80 characters.")
        return value

    @field_validator("organization")
    @classmethod
    def validate_organization(cls, value: str) -> str:
        if len(value) > 120:
            raise ValueError("Organization must be 120 characters or fewer.")
        return value

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        if not 20 <= len(value) <= 4000:
            raise ValueError("Please write between 20 and 4000 characters.")
        return value


class InMemoryRateLimiter:
    """Small contact-form guard; deliberately no database/Redis dependency."""

    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        window = int(os.getenv("CONTACT_RATE_LIMIT_WINDOW_SECONDS", "600"))
        maximum = int(os.getenv("CONTACT_RATE_LIMIT_MAX", "5"))
        events = self._events[key]
        while events and now - events[0] > window:
            events.popleft()
        if len(events) >= maximum:
            return False
        events.append(now)
        return True


contact_limiter = InMemoryRateLimiter()


def client_key(request: Request) -> str:
    if os.getenv("TRUST_CLOUDFLARE_IP") == "1":
        cf_ip = request.headers.get("cf-connecting-ip")
        if cf_ip:
            return cf_ip
    return request.client.host if request.client else "unknown"


def validation_errors(exc: ValidationError) -> dict[str, str]:
    mapped: dict[str, str] = {}
    for error in exc.errors():
        field = str(error["loc"][-1])
        message = error["msg"].replace("Value error, ", "")
        mapped.setdefault(field, message)
    return mapped


async def send_contact_email(payload: ContactPayload) -> str:
    api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("CONTACT_FROM_EMAIL")
    to_email = os.getenv("CONTACT_TO_EMAIL", load_data()["site"]["email"])
    if not api_key or not from_email:
        raise RuntimeError("Contact email delivery is not configured")

    labels = {
        "hiring": "Hiring inquiry",
        "consulting": "Consulting inquiry",
        "collaboration": "Collaboration",
        "other": "Website message",
    }
    label = labels[payload.inquiry_type]
    name = html.escape(payload.name)
    email = html.escape(str(payload.email))
    organization = html.escape(payload.organization or "—")
    message = html.escape(payload.message).replace("\n", "<br>")
    body_html = (
        f"<h2>{label}</h2><p><strong>Name:</strong> {name}</p>"
        f"<p><strong>Email:</strong> {email}</p>"
        f"<p><strong>Organization:</strong> {organization}</p>"
        f"<p><strong>Message:</strong></p><p>{message}</p>"
    )
    body_text = (
        f"{label}\n\nName: {payload.name}\nEmail: {payload.email}\n"
        f"Organization: {payload.organization or '—'}\n\n{payload.message}"
    )
    request_payload = {
        "from": from_email,
        "to": [to_email],
        "subject": f"[Portfolio] {label} — {payload.name}",
        "reply_to": str(payload.email),
        "html": body_html,
        "text": body_text,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Idempotency-Key": f"portfolio-{uuid4()}",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            "https://api.resend.com/emails", headers=headers, json=request_payload
        )
    if response.status_code not in {200, 201}:
        raise RuntimeError("Email provider rejected the message")
    return str(response.json().get("id", "sent"))
