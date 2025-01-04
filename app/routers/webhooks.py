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

router = APIRouter(prefix="/webhook", tags=["webhook"])

@router.post("/stripe/checkout")
async def webhook_stripe_post_checkout(
    request: Request,
    db: AsyncSession = Depends(sessions.get_async_session),
):
    payload = await request.body()
    event = None

    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    # Handle the event
    if event.type == "checkout.session.completed":
        # print(event.data.object)
        custom_field: str = event.data.object["custom_fields"][0]["text"][
            "default_value"
        ]
        custom_field_splitted = custom_field.split("#", 2)
        repository_name = custom_field_splitted[0]
        issue_number = custom_field_splitted[1]
        bounty_amount = event.data.object["amount_total"]
        await bump_bounty_issue(db, repository_name, issue_number, bounty_amount // 100)

    return {}

async def bump_bounty_issue(
    db, repository_name: str, issue_number: int, bounty_amount: int
):
    print(repository_name, issue_number, bounty_amount)
    result_repository = await db.execute(
        select(Repositories).where(Repositories.name == repository_name)
    )
    repository = result_repository.scalars().first()

    result_issues = await db.execute(
        select(Issues).where(Issues.repository_id == repository.id).where(
            Issues.issue_number == issue_number
        )
    )

    issue = result_issues.scalars().first()

    issue.cumulative_bounty = issue.cumulative_bounty + bounty_amount
    await db.commit()


def is_eligable_for_bounty(issue) -> bool:
    """An issue is eligible if it has the right label attached to it.
    """
    label_whitelist = ["confirmed"]

    labels = issue["labels"]
    label_names = list(map(lambda label: label["name"], labels))

    return any(i in label_whitelist for i in label_names)

async def check_issue_exists(issue, db: AsyncSession) -> Issues:
    repository_name = issue["repository_url"].split('/')[-1]
    result_repository = await db.execute(
        select(Repositories).where(Repositories.name == repository_name)
    )
    repository = result_repository.scalars().first()
    result_issues = await db.execute(
        select(Issues).where(Issues.repository_id == repository.id).where(
            Issues.issue_number == issue["number"]
        )
    )
    return result_issues.scalars().first()

async def repository_exists(repo_name, session):
    result = await session.execute(
        select(Repositories).where(Repositories.name == repo_name)
    )
    return result.scalars().first()


@router.post("/github/issue")
async def webhook_github_issue(
    request: Request,
    db: AsyncSession = Depends(sessions.get_async_session),
):
    payload = json.loads(json.loads(await request.body())["payload"])
    issue = payload["issue"]

    if is_eligable_for_bounty(issue):
        issue_db = await check_issue_exists(issue, db)
        if issue_db:
            print(issue_db.title)
        else:
            print("Issue does not exist.")
            repo_name = issue["repository_url"].split('/')[-1]
            repo = await repository_exists(repo_name, db)
            db.add(Issues(
                title=issue["title"],
                repository_id= repo.id,
                issue_number=issue["number"],
            ))
            await db.commit()
            print("Issue created.")

    # if "closed" == payload["action"]:
    #     print(f"Issue closed: {issue["number"]}")
    # elif "opened" == payload["action"]:
    #     if issue["labels"] in labels:
    #         print(issue["number"])
    
    
