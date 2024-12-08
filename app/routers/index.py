from typing import Sequence, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select, delete
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import sessions
from app.db.models import Repositories, Users, Issues
from app.db.schemas import repositories as repos_schema
from app.deps import get_current_user


auth_user_dependency = Annotated[Users, Depends(get_current_user)]

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def index(
    request: Request, db: AsyncSession = Depends(sessions.get_async_session)
):

    q = select(Repositories)
    result = await db.execute(q)
    repos = result.scalars().all()
    return templates.TemplateResponse(
        name="index.html", request=request, context={"repositories": repos}
    )


@router.get("/{repository_name}")
async def get_post(
    request: Request,
    repository_name: str,
    db: AsyncSession = Depends(sessions.get_async_session),
):
    result_repository = await db.execute(
        select(Repositories).where(Repositories.name == repository_name)
    )
    repository = result_repository.scalars().first()

    result_issues = await db.execute(
        select(Issues).where(Issues.repository_id == repository.id)
    )
    issues = result_issues.scalars().all()


    return templates.TemplateResponse(
        name="repository.html", request=request, context={"repository": repository, "issues": issues}
    )
