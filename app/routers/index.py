from typing import Sequence, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy import select, delete
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import sessions
from app.db.models import Repositories, Users, Issues
from app.db.schemas import repositories as repos_schema
from app.deps import get_current_user
import os
import dotenv
import json

import stripe

# This test secret API key is a placeholder. Don't include personal details in requests with this key.
# To see your test secret API key embedded in code samples, sign in to your Stripe account.
# You can also find your test secret API key at https://dashboard.stripe.com/test/apikeys.
# stripe.api_key = os.environ.get('STRIPE_KEY')
stripe.api_key = dotenv.dotenv_values()["STRIPE_KEY"]

# print(dotenv.dotenv_values())

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
async def get_repository_html(
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
        name="repository.html",
        request=request,
        context={"repository": repository, "issues": issues},
    )


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: Request,
    repository_name: Annotated[str, Form()],
    number: Annotated[str, Form()],
):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    "price": "price_1QU5fsHoNPk03hr4E2n5ztVe",
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=str(request.base_url) + f"{repository_name}",
            cancel_url=str(request.base_url) + f"{repository_name}",
            custom_fields=[
                {
                    "key": "issue",
                    "label": {
                        "type": "custom",
                        "custom": "Repository and Issue number (do not edit)",
                    },
                    "type": "text",
                    "text": {"default_value": f"{repository_name}#{number}"},
                }
            ],
        )
    except Exception as e:
        return str(e)

    return RedirectResponse(checkout_session.url, status_code=status.HTTP_303_SEE_OTHER)
