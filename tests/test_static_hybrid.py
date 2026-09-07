from fastapi.testclient import TestClient

import main


def test_contact_api_accepts_static_frontend(monkeypatch):
    async def fake_send(_payload):
        return "email-id"

    monkeypatch.setattr("portfolio_app.contact_routes.send_contact_email", fake_send)
    client = TestClient(main.app)
    response = client.post(
        "/api/contact",
        headers={"Origin": "https://alessandrocasadei.com"},
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
    assert response.json()["ok"] is True
    assert response.headers["access-control-allow-origin"] == "https://alessandrocasadei.com"


def test_contact_api_returns_validation_errors():
    client = TestClient(main.app)
    response = client.post(
        "/api/contact",
        headers={"Origin": "https://alessandrocasadei.com"},
        data={
            "name": "A",
            "email": "not-an-email",
            "organization": "",
            "inquiry_type": "hiring",
            "message": "short",
            "website": "",
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["ok"] is False
    assert "name" in payload["errors"]
    assert "email" in payload["errors"]
    assert "message" in payload["errors"]
