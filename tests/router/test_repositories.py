# pylint: disable=missing-docstring
"""Test repositories api."""
from httpx import AsyncClient
import pytest


@pytest.mark.anyio
async def test_get_repositories(async_client: AsyncClient) -> None:
    r = await async_client.get("/api/repositories/", follow_redirects=True)
    assert r.status_code == 200
