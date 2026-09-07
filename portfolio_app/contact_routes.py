from __future__ import annotations

import httpx
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError

from .contact import ContactPayload, client_key, contact_limiter, send_contact_email, validation_errors
from .presentation import render

router = APIRouter()
TITLE = "Contact — Alessandro Casadei"
DESCRIPTION = "Contact Alessandro Casadei about engineering roles, AI/data/automation projects or technical collaboration."


def contact_page(request: Request, *, status_code: int = 200, **extra):
    return render(
        request,
        "contact.html",
        title=TITLE,
        description=DESCRIPTION,
        canonical_path="/contact",
        active="contact",
        status_code=status_code,
        **extra,
    )


@router.get("/contact", response_class=HTMLResponse)
async def contact_get(request: Request):
    topic = request.query_params.get("topic", "")
    if topic not in {"hiring", "consulting", "collaboration", "other"}:
        topic = ""
    return contact_page(
        request,
        form={"inquiry_type": topic},
        form_errors={},
        form_status=None,
    )


@router.post("/contact", response_class=HTMLResponse)
async def contact_post(
    request: Request,
    name: str = Form(""),
    email: str = Form(""),
    organization: str = Form(""),
    inquiry_type: str = Form("other"),
    message: str = Form(""),
    website: str = Form(""),
):
    form = {
        "name": name,
        "email": email,
        "organization": organization,
        "inquiry_type": inquiry_type,
        "message": message,
    }

    if website.strip():
        return contact_page(
            request,
            form={},
            form_errors={},
            form_status={"type": "success", "text": "Thanks — your message has been received."},
        )

    try:
        payload = ContactPayload(**form)
    except ValidationError as exc:
        return contact_page(
            request,
            status_code=422,
            form=form,
            form_errors=validation_errors(exc),
            form_status={"type": "error", "text": "Please fix the highlighted fields and try again."},
        )

    if not contact_limiter.allow(client_key(request)):
        return contact_page(
            request,
            status_code=429,
            form=form,
            form_errors={},
            form_status={"type": "error", "text": "Too many attempts from this connection. Please email me directly instead."},
        )

    try:
        await send_contact_email(payload)
    except (httpx.HTTPError, RuntimeError, ValueError):
        return contact_page(
            request,
            status_code=503,
            form=form,
            form_errors={},
            form_status={"type": "error", "text": "The form could not deliver your message. Nothing was marked as sent — please email me directly."},
        )

    return contact_page(
        request,
        form={},
        form_errors={},
        form_status={"type": "success", "text": "Message sent. I’ll reply to the email address you provided."},
    )
