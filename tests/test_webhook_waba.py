import pytest
from fastapi.testclient import TestClient
from src.main import app
import hmac, hashlib, os

client = TestClient(app)

def test_whatsapp_webhook_invalid_signature():
    response = client.post("/api/webhook/waba", json={}, headers={"X-Hub-Signature-256": "sha256=invalid"})
    assert response.status_code == 401

def test_whatsapp_webhook_valid_signature(monkeypatch):
    secret = "testsecret"
    os.environ["WABA_APP_SECRET"] = secret
    payload = {"entry":[{"changes":[{"value":{"contacts":[{"wa_id":"123","profile":{"name":"Test"}}],"messages":[{"text":{"body":"Hello"}}]}}]}]}
    body = bytes(str(payload), 'utf-8')
    sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    response = client.post("/api/webhook/waba", json=payload, headers={"X-Hub-Signature-256": f"sha256={sig}"})
    assert response.status_code == 200
