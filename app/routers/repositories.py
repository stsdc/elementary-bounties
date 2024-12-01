from typing import Sequence, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import sessions
from app.db.models import Repositories, Users
from app.db.schemas import repositories as repos_schema
from app.deps import get_current_user


router = APIRouter(prefix="/repositories", tags=["repositories"])

auth_user_dependency = Annotated[Users, Depends(get_current_user)]

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.get("/")
async def get_repositories(db: AsyncSession = Depends(sessions.get_async_session)) -> Sequence[repos_schema.Repositories]:
    q = select(Repositories)
    result = await db.execute(q)
    repos = result.scalars().all()

    if not repos:
        raise HTTPException(status_code=404, detail="No repos found")
    return repos
