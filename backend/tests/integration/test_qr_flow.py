from __future__ import annotations

import json

import pytest

try:  # pragma: no cover - httpx optional
    from fastapi.testclient import TestClient  # type: ignore
except Exception:  # pragma: no cover
    TestClient = None  # type: ignore

from app.schemas.qrcode import QrOptions

pytestmark = pytest.mark.skipif(TestClient is None, reason="httpx không khả dụng")


def _auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "admin123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_generate_scan_and_analytics(client: TestClient):
    headers = _auth_headers(client)

    customer_res = client.post(
        "/api/customers/",
        headers=headers,
        json={"name": "Test Customer", "email": "c@example.com"},
    )
    customer_id = customer_res.json()["id"]

    product_res = client.post(
        "/api/products/",
        headers=headers,
        json={"sku": "SKU-123", "name": "Demo Product", "owner_customer_id": customer_id},
    )
    product_id = product_res.json()["id"]

    options = QrOptions().json()
    qr_res = client.post(
        "/api/qrcodes/generate",
        headers=headers,
        data={
            "data": json.dumps({"product": "Demo Product"}),
            "product_id": str(product_id),
            "customer_id": str(customer_id),
            "reuse_allowed": "true",
            "options": options,
        },
    )
    qr_payload = qr_res.json()
    code_id = qr_payload["code_id"]

    scan_res = client.post(f"/api/scan?code_id={code_id}")
    assert scan_res.status_code == 200

    analytics_res = client.get("/api/analytics/summary", headers=headers)
    assert analytics_res.status_code == 200
    data = analytics_res.json()
    assert "summary" in data
    assert data["summary"]["total_scans"] >= 1

    qr_analytics = client.get(f"/api/analytics/qr/{code_id}", headers=headers)
    assert qr_analytics.status_code == 200
    timeline = qr_analytics.json()["timeline"]
    assert any(event["event"] == "scan" for event in timeline)
