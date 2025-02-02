import os
from typing import Annotated
from fastapi import APIRouter, Depends, status, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import stripe

from app.db import sessions
from app.db.models import Repositories, Users, Issues
from app.deps import get_current_user

# This test secret API key is a placeholder. Don't include personal details in requests with this key.
# To see your test secret API key embedded in code samples, sign in to your Stripe account.
# You can also find your test secret API key at https://dashboard.stripe.com/test/apikeys.
stripe.api_key = os.environ.get("STRIPE_KEY")


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


@router.get("/repository/{repository_name}")
async def get_repository_html(
    request: Request,
    repository_name: str,
    db: AsyncSession = Depends(sessions.get_async_session),
):
    result_repository = await db.execute(select(Repositories).where(Repositories.name == repository_name))
    repository = result_repository.scalars().first()

    result_issues = await db.execute(select(Issues).where(Issues.repository_id == repository.id))
    issues = result_issues.scalars().all()

    return templates.TemplateResponse(
        name="repository.html",
        request=request,
        context={"repository": repository, "issues": issues},
    )

@router.get("/hot")
async def get_hot_html(

    request: Request,
    db: AsyncSession = Depends(sessions.get_async_session),
):
    """
    Fetches and renders a list of issues with cumulative bounties greater than zero,
    limits the results to 25, and renders them using the "hot.html" template.
    """
    result_issues = await db.execute(select(Issues).where(Issues.cumulative_bounty > 0).limit(25))
    issues = result_issues.scalars().all()

    return templates.TemplateResponse(
        name="hot.html",
        request=request,
        context={"issues": issues},
    )

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: Request,
    repository_name: Annotated[str, Form()],
    number: Annotated[str, Form()],
):
    try:
        checkout_session = stripe.checkout.Session.create(
            metadata={"repository_name": repository_name, "issue_number": number},
            payment_intent_data={
                "metadata": {"repository_name": repository_name, "issue_number": number}
            },
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    "price": "price_1QU5fsHoNPk03hr4E2n5ztVe",
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=f"{request.base_url}repository/{repository_name}#success",
            cancel_url=f"{request.base_url}repository/{repository_name}",
        )
    except Exception as e:
        return str(e)

    return RedirectResponse(checkout_session.url, status_code=status.HTTP_303_SEE_OTHER)
