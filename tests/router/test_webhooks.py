"""Tests for webhooks."""

import pytest
from fastapi import HTTPException, Request
from httpx import Response
from unittest.mock import AsyncMock, patch
from app.db import sessions
from app.db.models import Issues
from app.routers.webhooks import gate_by_github_ip, webhook_github_issue
import hmac
import hashlib
from fastapi import HTTPException
from app.routers.webhooks import verify_signature


@pytest.mark.anyio
@patch("app.routers.webhooks.GITHUB_IPS_ONLY", True)
async def test_gate_by_github_ip_valid_ip():
    """Test Github hook valid IP."""
    request = AsyncMock(Request)
    request.client.host = "192.30.252.0"  # Example GitHub IP

    async_client_response = Response(200, json={"hooks": ["192.30.252.0/22"]})

    with patch(
        "app.routers.webhooks.AsyncClient.get", return_value=async_client_response
    ):
        await gate_by_github_ip(request)  # Should not raise an exception


@pytest.mark.anyio
async def test_gate_by_github_ip_invalid_ip():
    """Test Github hook invalid IP."""
    request = AsyncMock(Request)
    request.client.host = "8.8.8.8"  # Example non-GitHub IP

    async_client_response = Response(200, json={"hooks": ["192.30.252.0/22"]})

    with patch(
        "app.routers.webhooks.AsyncClient.get", return_value=async_client_response
    ):
        with pytest.raises(HTTPException) as exc_info:
            await gate_by_github_ip(request)
        assert exc_info.value.status_code == 403


@pytest.mark.anyio
async def test_gate_by_github_ip_invalid_ip_format():
    """Test Github hook invalid IP format."""
    request = AsyncMock(Request)
    request.client.host = "invalid-ip"  # Invalid IP format

    with pytest.raises(HTTPException) as exc_info:
        await gate_by_github_ip(request)
    assert exc_info.value.status_code == 400


def test_verify_signature_valid():
    """Test valid signature."""
    payload_body = b"test payload"
    secret_token = "secret"
    hash_object = hmac.new(
        secret_token.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256
    )
    signature_header = "sha256=" + hash_object.hexdigest()

    try:
        verify_signature(payload_body, secret_token, signature_header)
    except HTTPException:
        pytest.fail("HTTPException raised with valid signature")


def test_verify_signature_missing_header():
    """Test missing signature header."""
    payload_body = b"test payload"
    secret_token = "secret"
    signature_header = None
    with pytest.raises(HTTPException) as exc_info:
        verify_signature(payload_body, secret_token, signature_header)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "x-hub-signature-256 header is missing!"


@pytest.mark.anyio
@patch("app.routers.webhooks.verify_signature")
async def test_webhook_github_issue_non_eligible(mock_verify_signature):
    """Test webhook_github_issue with a non-eligible issue."""
    request = AsyncMock(Request)
    request.body = AsyncMock(return_value=b'{"issue": {"number": 1, "state": "open", "title": "Test Issue", "labels": []}}')
    request.headers = {"x-hub-signature-256": "valid_signature"}
    db = AsyncMock()

    response = await webhook_github_issue(request, db, "issues")
    mock_verify_signature.assert_called_once()
    assert response == {"message": "Received an event for a non-eligible for bounty issue."}

@pytest.mark.anyio
@patch("app.routers.webhooks.verify_signature")
@patch("app.routers.webhooks.crud_issues.get_issue")
async def test_webhook_github_issue_eligible(mock_get_issue, mock_verify_signature):
    """Test webhook_github_issue with a non-eligible issue."""
    request = AsyncMock(Request)
    request.body = AsyncMock(return_value=b'{"issue": {"number": 1, "state": "open", "title": "Test Issue", "labels": [{"name":"confirmed"}]}}')
    request.headers = {"x-hub-signature-256": "valid_signature"}
    db = AsyncMock()
    mock_get_issue.return_value = Issues(
            title="Test Issue",
            repository_id=123,
            state="open",
            number=1,
            url="",
    )
    response = await webhook_github_issue(request, db, "issues")
    mock_verify_signature.assert_called_once()
    assert response == {"message": "An event for issue #1 received."}
