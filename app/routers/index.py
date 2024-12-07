from typing import Sequence, Annotated
from fastapi import APIRouter, Depends, HTTPException, status,Request
from sqlalchemy import select, delete
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import sessions
from app.db.models import Repositories, Users
from app.db.schemas import repositories as repos_schema
from app.deps import get_current_user


auth_user_dependency = Annotated[Users, Depends(get_current_user)]

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def index(request: Request, db: AsyncSession = Depends(sessions.get_async_session)):
    
    q = select(Repositories)
    result = await db.execute(q)
    repos = result.scalars().all()
    print(repos)
    return templates.TemplateResponse(name="index.html", request=request, context={"repositories": repos})
