"""
REST API integration tests (PDF section 23 + API TESTING requirements).

Uses FastAPI's TestClient against the real application:
  POST /api/analyze, POST /api/generate-password,
  GET /api/dashboard/stats, GET /api/analytics/weaknesses, GET /api/health
"""
from __future__ import annotations

import json

from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_analyze_response_structure():
    r = client.post("/api/analyze", json={"password": "Api-Test-9921!"})
    assert r.status_code == 200
    body = r.json()
    for key in ("score", "classification", "findings", "suggestions",
                "metrics", "policy", "breach_check", "meta", "disclaimer"):
        assert key in body
    assert isinstance(body["score"], int) and 0 <= body["score"] <= 100
    assert body["classification"] in (
        "VERY WEAK", "WEAK", "MODERATE", "STRONG", "VERY STRONG")
    assert body["meta"]["privacy"].startswith("Password was processed")
    # the request password never appears in the response
    assert "Api-Test-9921!" not in r.text


def test_analyze_with_context_and_policy_override():
    r = client.post("/api/analyze", json={
        "password": "Rahul@90210",
        "context": {"first_name": "Rahul", "birth_year": "",
                    "organization": ""},
        "policy": {"minimum_length": 12},
    })
    assert r.status_code == 200
    body = r.json()
    assert "personal_info_name" in [f["type"] for f in body["findings"]]
    assert body["policy"]["policy"]["minimum_length"] == 12
    assert body["policy"]["policy_result"] == "POLICY FAIL"


def test_analyze_empty_and_max_length_handling():
    r = client.post("/api/analyze", json={"password": ""})
    assert r.status_code == 200
    assert r.json()["classification"] == "VERY WEAK"
    r = client.post("/api/analyze", json={"password": "Ab3!" * 32})  # 128 chars
    assert r.status_code == 200
    r = client.post("/api/analyze", json={"password": "A" * 129})
    assert r.status_code == 422                       # too long -> rejected


def test_analyze_missing_or_wrong_body():
    assert client.post("/api/analyze", json={}).status_code == 422
    assert client.post("/api/analyze",
                       json={"password": 1234}).status_code == 422
    assert client.post("/api/analyze",
                       content="not json",
                       headers={"Content-Type": "application/json"}
                       ).status_code == 422


def test_generate_password_endpoint():
    r = client.post("/api/generate-password", json={
        "mode": "password", "length": 20, "symbols": True})
    assert r.status_code == 200
    body = r.json()
    assert len(body["generated"]) == 20
    assert "secrets" in body["note"]


def test_generate_passphrase_endpoint_and_validation():
    r = client.post("/api/generate-password", json={"mode": "passphrase",
                                                    "words": 4})
    assert r.status_code == 200
    assert len(r.json()["generated"].split("-")) == 4
    assert client.post("/api/generate-password",
                       json={"mode": "password", "length": 4}
                       ).status_code == 422   # below minimum length
    assert client.post("/api/generate-password",
                       json={"mode": "bogus"}).status_code == 422


def test_dashboard_stats_and_weakness_endpoints():
    stats = client.get("/api/dashboard/stats")
    assert stats.status_code == 200
    s = stats.json()
    assert set(s["classifications"].keys()) == {
        "VERY WEAK", "WEAK", "MODERATE", "STRONG", "VERY STRONG"}
    assert "average_score" in s and "total_analyses" in s
    # no password-bearing KEY exists anywhere in the stats payload
    def _keys(obj):
        keys = set()
        if isinstance(obj, dict):
            for k, v in obj.items():
                keys.add(str(k))
                keys |= _keys(v)
        elif isinstance(obj, list):
            for v in obj:
                keys |= _keys(v)
        return keys
    forbidden = {"password", "password_hash", "pwd", "credential"}
    assert not (_keys(s) & forbidden)
    w = client.get("/api/analytics/weaknesses")
    assert w.status_code == 200
    assert {"weakness_types", "pattern_frequency"} <= set(w.json().keys())


def test_analyze_records_safe_analytics(tmp_path):
    r = client.post("/api/analyze",
                    json={"password": "Audit-Trail-5567!"})
    assert r.status_code == 200
    assert r.json()["meta"]["analytics_recorded"] is True
