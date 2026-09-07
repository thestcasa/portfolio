"""Alessandro Casadei portfolio application."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from portfolio_app.contact_routes import router as contact_router
from portfolio_app.content import load_data
from portfolio_app.presentation import render
from portfolio_app.routes import router as site_router

ROOT = Path(__file__).parent

app = FastAPI(title="Alessandro Casadei", docs_url=None, redoc_url=None)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CONTACT_ALLOWED_ORIGINS",
        "https://alessandrocasadei.com,https://www.alessandrocasadei.com,https://alessandro-casadei-static.onrender.com",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Accept", "Content-Type"],
)

app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
app.include_router(site_router)
app.include_router(contact_router)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()"
    )
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; connect-src 'self' https://alessandro-casadei.onrender.com; "
        "font-src 'self'; form-action 'self'; base-uri 'self'; frame-ancestors 'none'",
    )
    if request.url.path.startswith("/static/"):
        response.headers.setdefault("Cache-Control", "public, max-age=86400")
    else:
        response.headers.setdefault("Cache-Control", "no-cache")
    return response


@app.exception_handler(404)
async def not_found(request: Request, _exc):
    return render(
        request,
        "404.html",
        title="Page not found — Alessandro Casadei",
        description="The requested page does not exist.",
        canonical_path=request.url.path,
        active="",
        status_code=404,
    )
