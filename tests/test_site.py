import re

import pytest
from fastapi.testclient import TestClient

import main
from portfolio_app import contact


@pytest.fixture(autouse=True)
def reset_rate_limit():
    contact.contact_limiter._events.clear()


@pytest.fixture()
def client():
    return TestClient(main.app)


def test_primary_pages_render(client):
    for path in ["/", "/work", "/consulting", "/about", "/contact", "/healthz", "/robots.txt", "/sitemap.xml"]:
        response = client.get(path)
        assert response.status_code == 200, path


def test_project_routes_render(client):
    for project in main.load_data()["projects"]:
        if project.get("case_study"):
            response = client.get(f"/work/{project['slug']}")
            assert response.status_code == 200
            assert project["title"] in response.text
            assert project["repo"] in response.text


def test_non_case_study_slug_is_404(client):
    response = client.get("/work/network-dynamics-learning")
    assert response.status_code == 404
    assert "This route does not exist" in response.text


def test_unknown_route_uses_custom_404(client):
    response = client.get("/definitely-not-a-page")
    assert response.status_code == 404
    assert "This route does not exist" in response.text


def test_home_has_recruiter_and_client_paths(client):
    text = client.get("/").text
    assert 'href="/work"' in text
    assert 'href="/consulting"' in text
    assert 'href="/contact?topic=consulting"' in text
    assert "AI, Data &amp; Automation Engineer" in text
    assert "MSc Data Science and Engineering Student" not in text


def test_metadata_and_structured_data(client):
    text = client.get("/work/careeros").text
    assert '<link rel="canonical" href="https://alessandrocasadei.com/work/careeros">' in text
    assert 'property="og:title"' in text
    assert '"@type": "Person"' in text
    assert '"@type": "CreativeWork"' in text


def test_project_links_are_specific_repositories():
    for project in main.load_data()["projects"]:
        assert project["repo"].startswith("https://github.com/")
        assert project["repo"] not in {"https://github.com/thestcasa", "https://github.com/thestcasa/"}


def test_internal_navigation_paths_resolve(client):
    for source in ["/", "/work", "/consulting", "/about", "/contact"]:
        html = client.get(source).text
        hrefs = set(re.findall(r'href="(/[^"#?]*)', html))
        for href in hrefs:
            if href.startswith("/static/"):
                continue
            response = client.get(href)
            assert response.status_code < 400, (source, href, response.status_code)


def test_contact_prefills_topic(client):
    response = client.get("/contact?topic=consulting")
    assert 'value="consulting" selected' in response.text


def test_contact_validation_returns_field_errors(client):
    response = client.post(
        "/contact",
        data={
            "name": "A",
            "email": "not-an-email",
            "organization": "",
            "inquiry_type": "hiring",
            "message": "too short",
            "website": "",
        },
    )
    assert response.status_code == 422
    assert "Please fix the highlighted fields" in response.text
    assert 'aria-invalid="true"' in response.text


def test_contact_without_provider_is_honest_error(client, monkeypatch):
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.delenv("CONTACT_FROM_EMAIL", raising=False)
    response = client.post(
        "/contact",
        data={
            "name": "Recruiter Name",
            "email": "recruiter@example.com",
            "organization": "Example Co",
            "inquiry_type": "hiring",
            "message": "I am contacting you about an applied AI engineering role on our team.",
            "website": "",
        },
    )
    assert response.status_code == 503
    assert "Nothing was marked as sent" in response.text
    assert "Message sent" not in response.text


def test_contact_honeypot_does_not_call_provider(client, monkeypatch):
    called = False

    async def should_not_send(_payload):
        nonlocal called
        called = True
        raise AssertionError("provider should not be called")

    monkeypatch.setattr("portfolio_app.contact_routes.send_contact_email", should_not_send)
    response = client.post(
        "/contact",
        data={
            "name": "Spam Bot",
            "email": "bot@example.com",
            "organization": "",
            "inquiry_type": "other",
            "message": "This looks valid but the hidden field is filled by a bot.",
            "website": "https://spam.example",
        },
    )
    assert response.status_code == 200
    assert not called


def test_contact_success_with_mocked_provider(client, monkeypatch):
    captured = {}

    async def fake_send(payload):
        captured["payload"] = payload
        return "email-id"

    monkeypatch.setattr("portfolio_app.contact_routes.send_contact_email", fake_send)
    response = client.post(
        "/contact",
        data={
            "name": "Technical Founder",
            "email": "founder@example.com",
            "organization": "Small Co",
            "inquiry_type": "consulting",
            "message": "We have a manual CRM and reporting workflow that we want to map and automate.",
            "website": "",
        },
    )
    assert response.status_code == 200
    assert "Message sent" in response.text
    assert str(captured["payload"].email) == "founder@example.com"
