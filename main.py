"""
main.py — FastAPI Portfolio Application
========================================
Architecture:
  - Single-page SSR using Jinja2Templates
  - All content loaded from data.json (no hardcoded text in templates)
  - GET  /        → renders full portfolio page
  - POST /contact → handles contact form submission, returns same page with a flash message
"""

import json
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ── App Initialisation ───────────────────────────────────────────────────────

app = FastAPI(title="Portfolio", docs_url=None, redoc_url=None)

# Mount the /static directory so templates can reference CSS/images/etc.
# StaticFiles serves everything under ./static at the URL prefix /static.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2Templates points to the ./templates directory.
# All .html files there are discoverable via templates.TemplateResponse().
templates = Jinja2Templates(directory="templates")

# ── Data Loading ─────────────────────────────────────────────────────────────

DATA_FILE = Path(__file__).parent / "data.json"


def load_data() -> dict:
    """
    Load portfolio content from data.json.
    
    Called on each request so edits to data.json are reflected immediately
    without a server restart — ideal for development. In production you
    could cache this with functools.lru_cache or a startup event.
    """
    with DATA_FILE.open(encoding="utf-8") as f:
        return json.load(f)


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Render the main portfolio page.
    All template variables are sourced from data.json.
    """
    data = load_data()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            **data,                    # Unpacks personal, experience, projects, etc.
            "flash": None,             # No flash message on a fresh GET
        },
    )


@app.post("/contact", response_class=HTMLResponse)
async def contact(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
):
    """
    Handle the contact form POST.
    
    Currently prints received data to the terminal and passes a success
    flash message back to the template. Swap the print() for an email
    library (e.g. fastapi-mail) or a database insert when ready.
    """
    # ── Log to terminal (replace with real handler in production) ──────────
    print("\n" + "=" * 50)
    print("📬  New Contact Form Submission")
    print(f"  Name   : {name}")
    print(f"  Email  : {email}")
    print(f"  Message: {message}")
    print("=" * 50 + "\n")

    data = load_data()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            **data,
            "flash": {
                "type": "success",
                "text": f"Thanks {name}! Your message has been received. I'll get back to you soon.",
            },
        },
    )