from __future__ import annotations

from pathlib import Path

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .content import load_data

ROOT = Path(__file__).resolve().parents[1]
templates = Jinja2Templates(directory=ROOT / "templates")


def page_context(
    request: Request,
    *,
    title: str,
    description: str,
    canonical_path: str,
    active: str,
    **extra,
) -> dict:
    data = load_data()
    site = data["site"]
    person_schema = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": site["name"],
        "url": site["url"],
        "jobTitle": site["role"],
        "email": f"mailto:{site['email']}",
        "sameAs": [site["github"], site["linkedin"]],
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "Politecnico di Torino"},
    }
    return {
        "request": request,
        **data,
        "page_title": title,
        "page_description": description,
        "canonical_url": f"{site['url']}{canonical_path}",
        "active": active,
        "person_schema": person_schema,
        **extra,
    }


def render(
    request: Request,
    template: str,
    *,
    title: str,
    description: str,
    canonical_path: str,
    active: str,
    status_code: int = 200,
    **extra,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name=template,
        context=page_context(
            request,
            title=title,
            description=description,
            canonical_path=canonical_path,
            active=active,
            **extra,
        ),
        status_code=status_code,
    )
