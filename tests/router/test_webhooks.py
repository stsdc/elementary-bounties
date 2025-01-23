"""Tests for webhooks."""
import pytest
from fastapi import HTTPException, Request
from httpx import Response
from unittest.mock import AsyncMock, patch
from app.routers.webhooks import gate_by_github_ip

@pytest.mark.anyio
@patch("app.routers.webhooks.GITHUB_IPS_ONLY", True)
async def test_gate_by_github_ip_valid_ip():
    """Test Github hook valid IP."""
    request = AsyncMock(Request)
    request.client.host = "192.30.252.0"  # Example GitHub IP

    async_client_response = Response(200, json={
        "hooks": ["192.30.252.0/22"]
    })

    with patch("app.routers.webhooks.AsyncClient.get", return_value=async_client_response):
        await gate_by_github_ip(request)  # Should not raise an exception

@pytest.mark.anyio
async def test_gate_by_github_ip_invalid_ip():
    """Test Github hook invalid IP."""
    request = AsyncMock(Request)
    request.client.host = "8.8.8.8"  # Example non-GitHub IP

    async_client_response = Response(200, json={
        "hooks": ["192.30.252.0/22"]
    })

    with patch("app.routers.webhooks.AsyncClient.get", return_value=async_client_response):
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
