"""Pre-render the FastAPI/Jinja portfolio into a static dist/ directory."""

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi.testclient import TestClient

import main
from portfolio_app.content import load_data

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def output_path(route: str) -> Path:
    if route == "/":
        return DIST / "index.html"
    if route.endswith((".xml", ".txt")):
        return DIST / route.lstrip("/")
    return DIST / route.strip("/") / "index.html"


def write_response(client: TestClient, route: str) -> None:
    response = client.get(route)
    response.raise_for_status()
    target = output_path(route)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(response.content)


def build() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    client = TestClient(main.app)
    routes = ["/", "/work", "/consulting", "/about", "/contact", "/robots.txt", "/sitemap.xml"]
    routes.extend(
        f"/work/{project['slug']}"
        for project in load_data()["projects"]
        if project.get("case_study")
    )

    for route in routes:
        write_response(client, route)

    not_found = client.get("/static-build-404")
    (DIST / "404.html").write_bytes(not_found.content)

    shutil.copytree(ROOT / "static", DIST / "static", dirs_exist_ok=True)

    generated = sum(1 for path in DIST.rglob("*") if path.is_file())
    print(f"Static build complete: {generated} files in {DIST}")


if __name__ == "__main__":
    build()
