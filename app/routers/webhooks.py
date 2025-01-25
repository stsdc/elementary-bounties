"""This module contains webhooks for Stripe and Github."""

# from typing import Annotated
import hashlib
import hmac
import ipaddress
import json
from os import getenv
from fastapi import APIRouter, Depends, status, Request, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from urllib3 import HTTPResponse
import stripe
from httpx import AsyncClient

from app.db import sessions
from app.db.models import Issues
# from app.deps import get_current_user
import app.crud.issues as crud_issues
from app.log import get_logger

log = get_logger(__name__)

GITHUB_WEBHOOK_SECRET = getenv("GITHUB_WEBHOOK_SECRET", "")
GITHUB_IPS_ONLY = getenv("GITHUB_IPS_ONLY", "True").lower() in ["true", "1"]

# auth_user_dependency = Annotated[Users, Depends(get_current_user)]

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/stripe/checkout")
async def webhook_stripe_post_checkout(
    request: Request,
    db: AsyncSession = Depends(sessions.get_async_session),
):
    """
    Handle Stripe webhook for post-checkout events.

    This function processes the payload from a Stripe webhook event, specifically
    handling the "checkout.session.completed" event type. It extracts metadata and
    bounty amount from the event data and updates the corresponding issue's bounty
    in the database.

    Args:
        request (Request): The incoming HTTP request containing the webhook payload.
        db (AsyncSession): The asynchronous database session dependency.

    Returns:
        HTTPResponse: A response indicating the result of the webhook processing.
    """
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
        await crud_issues.bump_bounty_issue(
            db,
            metadata["repository_name"],
            metadata["issue_number"],
            bounty_amount // 100,
        )

    return {}


# https://github.com/falkben/webhook_receive/blob/6a080fc3800dba94c5cd103f0ad1f59618f6a188/webhook_receive/main.py#L66
async def gate_by_github_ip(request: Request):
    """
    Middleware function to allow requests only from GitHub IP addresses.

    Args:
        request (Request): The incoming HTTP request.

    Raises:
        HTTPException: If the request's IP address is not a valid GitHub
        IP address or if the IP address cannot be determined.

    Returns:
        None: If the request's IP address is a valid GitHub IP address,
        the function completes without raising an exception.
    """
    log.debug("Github IPs check is %s", GITHUB_IPS_ONLY)

    # Allow GitHub IPs only
    if GITHUB_IPS_ONLY:
        try:
            src_ip = ipaddress.ip_address(request.client.host)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not hook sender ip address",
            ) from exc
        async with AsyncClient() as client:
            allowlist = await client.get("https://api.github.com/meta")
        for valid_ip in allowlist.json()["hooks"]:
            if src_ip in ipaddress.ip_network(valid_ip):
                log.debug("IP validation: %s - OK", request.client.host)
                return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a GitHub hooks ip address",
        )


def verify_signature(payload_body, secret_token, signature_header):
    """Verify that the payload was sent from GitHub by validating SHA256.

    Raise and return 403 if not authorized.

    Args:
        payload_body: original request body to verify (request.body())
        secret_token: GitHub app webhook token (WEBHOOK_SECRET)
        signature_header: header received from GitHub (x-hub-signature-256)
    """
    if not signature_header:
        log.debug("x-hub-signature-256 header is missing!")
        raise HTTPException(
            status_code=403, detail="x-hub-signature-256 header is missing!"
        )
    hash_object = hmac.new(
        secret_token.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        log.debug("Request signatures didn't match!")
        raise HTTPException(status_code=403, detail="Request signatures didn't match!")


@router.post("/github/issue", dependencies=[Depends(gate_by_github_ip)])
async def webhook_github_issue(
    request: Request,
    db: AsyncSession = Depends(sessions.get_async_session),
    x_github_event: str = Header(...),
):
    """
    Handle GitHub issue webhook events.

    This function processes incoming GitHub webhook events related to issues.
    It verifies the signature of the payload, parses the payload, and updates
    the issue in the database if necessary.
    """
    log.debug("Received Github Event: %s", x_github_event)

    payload_body = await request.body()
    signature_header = request.headers.get("x-hub-signature-256")
    verify_signature(payload_body, GITHUB_WEBHOOK_SECRET, signature_header)

    try:
        payload = json.loads(payload_body)
    except json.decoder.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad JSON.") from exc

    issue = payload["issue"]

    if crud_issues.is_eligible_for_bounty(issue):
        issue_db: Issues = await crud_issues.get_issue(issue, db)
        if issue["state"] != crud_issues.issue_state_to_str(issue_db.state):
            issue_db.state = crud_issues.issue_state_to_bool(issue["state"])
            await db.commit()
        if issue["title"] != issue_db.title:
            issue_db.title = issue["title"]
            await db.commit()
        return {"message": f"An event for issue #{issue["number"]} received."}
    return {"message": "Received an event for a non-eligible for bounty issue."}
