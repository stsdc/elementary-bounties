"""Repositories API."""

from typing import Sequence
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import sessions
from app.db.models import Repositories
from app.db.schemas import repositories as repos_schema

router = APIRouter(prefix="/api/repositories", tags=["api", "repositories"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_repositories(
    db: AsyncSession = Depends(sessions.get_async_session),
) -> Sequence[repos_schema.Repositories]:
    """Get all repositories."""
    q = select(Repositories)
    result = await db.execute(q)
    repos = result.scalars().all()
    return repos
