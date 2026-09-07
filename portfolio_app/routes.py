from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from .content import load_data, project_index
from .presentation import render

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    featured = [project for project in load_data()["projects"] if project.get("featured")]
    return render(
        request,
        "index.html",
        title="Alessandro Casadei — AI, Data & Automation Engineer",
        description="AI, data and automation engineer building reliable software systems, ML pipelines, LLM workflows and operational automation.",
        canonical_path="/",
        active="home",
        featured_projects=featured,
    )


@router.get("/work", response_class=HTMLResponse)
async def work(request: Request):
    selected = [project for project in load_data()["projects"] if project.get("case_study")]
    archive = [project for project in load_data()["projects"] if not project.get("case_study")]
    return render(
        request,
        "work.html",
        title="Selected Work — Alessandro Casadei",
        description="Case studies across AI systems, LLM research, machine learning, NLP, time-aware evaluation and federated deep learning.",
        canonical_path="/work",
        active="work",
        selected_projects=selected,
        archive_projects=archive,
    )


@router.get("/work/{slug}", response_class=HTMLResponse)
async def project(request: Request, slug: str):
    item = project_index().get(slug)
    if not item or not item.get("case_study"):
        return render(
            request,
            "404.html",
            title="Page not found — Alessandro Casadei",
            description="The requested page does not exist.",
            canonical_path=request.url.path,
            active="",
            status_code=404,
        )
    project_schema = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": item["title"],
        "description": item["summary"],
        "creator": {"@type": "Person", "name": load_data()["site"]["name"]},
        "url": f"{load_data()['site']['url']}/work/{slug}",
        "codeRepository": item["repo"],
    }
    return render(
        request,
        "project.html",
        title=f"{item['title']} — Alessandro Casadei",
        description=item["summary"],
        canonical_path=f"/work/{slug}",
        active="work",
        project=item,
        project_schema=project_schema,
    )


@router.get("/consulting", response_class=HTMLResponse)
async def consulting(request: Request):
    return render(
        request,
        "consulting.html",
        title="AI & Automation Consulting — Alessandro Casadei",
        description="Practical workflow automation, internal AI systems, RevOps/data automation and process opportunity audits built around real operational problems.",
        canonical_path="/consulting",
        active="consulting",
    )


@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return render(
        request,
        "about.html",
        title="About — Alessandro Casadei",
        description="Engineering background across software, data, AI and automation, with current RevOps work at papernest and an MSc in Data Science and Engineering.",
        canonical_path="/about",
        active="about",
    )


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    site_url = load_data()["site"]["url"]
    return f"User-agent: *\nAllow: /\nSitemap: {site_url}/sitemap.xml\n"


@router.get("/sitemap.xml")
async def sitemap():
    site_url = load_data()["site"]["url"]
    paths = ["/", "/work", "/consulting", "/about", "/contact"]
    paths.extend(
        f"/work/{project['slug']}"
        for project in load_data()["projects"]
        if project.get("case_study")
    )
    urls = "".join(f"<url><loc>{site_url}{path}</loc></url>" for path in paths)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{urls}</urlset>"
    )
    return Response(content=xml, media_type="application/xml")


@router.get("/healthz", response_class=PlainTextResponse, include_in_schema=False)
async def healthz():
    return "ok"
