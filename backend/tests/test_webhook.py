"""Tests for the webhook endpoint."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

# We mock heavy deps before importing main
with (
    patch("db.supabase_client.get_supabase"),
    patch("services.whatsapp.TwilioClient"),
):
    from main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "docs" in resp.json()


@patch("routers.webhook.send_whatsapp_message", new_callable=AsyncMock)
@patch("routers.webhook.insert_link", new_callable=AsyncMock)
def test_twilio_webhook_no_url(mock_insert, mock_send):
    """Should respond with ok and send 'no link' message when no URL in body."""
    mock_send.return_value = True
    resp = client.post(
        "/webhook/twilio",
        data={"From": "whatsapp:+919876543210", "Body": "Hello there!"},
    )
    assert resp.status_code == 200
    assert mock_insert.call_count == 0


@patch("routers.webhook.process_link_pipeline", new_callable=AsyncMock)
@patch("routers.webhook.send_whatsapp_message", new_callable=AsyncMock)
@patch("routers.webhook.insert_link", new_callable=AsyncMock, return_value={"id": "test-id"})
def test_twilio_webhook_with_url(mock_insert, mock_send, mock_pipeline):
    """Should insert link and send ACK when URL is included."""
    mock_send.return_value = True
    resp = client.post(
        "/webhook/twilio",
        data={
            "From": "whatsapp:+919876543210",
            "Body": "Save this: https://www.instagram.com/reel/ABC123/",
        },
    )
    assert resp.status_code == 200
    assert mock_insert.called


def test_meta_verify_valid_token():
    resp = client.get("/webhook/meta", params={
        "hub.verify_token": "social_saver_token",
        "hub.challenge": "challenge_string_here",
        "hub.mode": "subscribe",
    })
    assert resp.status_code == 200
    assert resp.text == "challenge_string_here"


def test_meta_verify_invalid_token():
    resp = client.get("/webhook/meta", params={
        "hub.verify_token": "wrong_token",
        "hub.challenge": "any",
        "hub.mode": "subscribe",
    })
    assert resp.status_code == 403
