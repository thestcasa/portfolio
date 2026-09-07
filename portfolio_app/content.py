from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content"


@lru_cache(maxsize=1)
def load_data() -> dict:
    """Load public site content and ordered project records."""
    with (CONTENT_DIR / "site.json").open(encoding="utf-8") as handle:
        data = json.load(handle)

    order = data.pop("project_order")
    projects = []
    for slug in order:
        with (CONTENT_DIR / "projects" / f"{slug}.json").open(encoding="utf-8") as handle:
            projects.append(json.load(handle))
    data["projects"] = projects
    return data


def project_index() -> dict[str, dict]:
    return {project["slug"]: project for project in load_data()["projects"]}
