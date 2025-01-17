from typing import Annotated
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from urllib3 import HTTPResponse
from app.db import sessions
from app.db.models import Users, Issues
from app.deps import get_current_user
import app.crud.issues as crud_issues
import dotenv
import json

import stripe

# stripe.api_key = dotenv.dotenv_values()["STRIPE_KEY"]

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
        print(e)
        return HTTPResponse(status=status.HTTP_400_BAD_REQUEST)

    # Handle the event
    if event.type == "checkout.session.completed":
        print(event.data.object["metadata"])
        metadata = event.data.object["metadata"]
        bounty_amount = event.data.object["amount_total"]
        await crud_issues.bump_bounty_issue(db, metadata["repository_name"], metadata["issue_number"], bounty_amount // 100)

    return {}

@router.post("/github/issue")
async def webhook_github_issue(
    request: Request,
    db: AsyncSession = Depends(sessions.get_async_session),
):
    payload = json.loads(await request.body())
    issue = payload["issue"]

    if crud_issues.is_eligable_for_bounty(issue):
        issue_db: Issues = await crud_issues.get_issue(issue, db)
        if issue["state"] != crud_issues.issue_state_to_str(issue_db.state):
            issue_db.state = crud_issues.issue_state_to_bool(issue["state"])
            await db.commit()
        if issue["title"] != issue_db.title:
            issue_db.title = issue["title"]
            await db.commit()
