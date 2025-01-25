"""CRUD operations on issues."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Repositories, Issues
import app.crud.repositories as crud_repos
from app.log import get_logger

log = get_logger(__name__)


async def check_issue_exists(issue, repo_db: Repositories, db: AsyncSession) -> Issues:
    """
    Asynchronously checks if an issue exists in the database.

    Args:
        issue (dict): A dictionary object from the Github API.
        db (AsyncSession): The asynchronous database session.

    Returns:
        Issues: The issue object if it exists, otherwise None.
    """
    result_issues = await db.execute(
        select(Issues)
        .where(Issues.repository_id == repo_db.id)
        .where(Issues.number == issue["number"])
    )
    return result_issues.scalars().first()


async def get_issue(issue, db: AsyncSession):
    repo_db = await crud_repos.get_repository_by_issue(issue, db)
    issue_db = await check_issue_exists(issue, repo_db, db)
    if not issue_db:
        log.warning("Issue does not exist in the database")
        log.debug("Trying to add a new issue '%s' in %s", issue["title"], repo_db.id)
        issue_db = Issues(
            title=issue["title"],
            repository_id=repo_db.id,
            number=issue["number"],
            url=issue["html_url"],
        )
        db.add(issue_db)
        await db.commit()
        log.debug("Issue %s '%s' add to the database", issue["number"], issue["title"])
    return issue_db


def is_eligible_for_bounty(issue) -> bool:
    """An issue is eligible if it has the right label attached to it."""
    label_whitelist = ["confirmed"]

    labels = issue["labels"]
    label_names = list(map(lambda label: label["name"], labels))

    return any(i in label_whitelist for i in label_names)


async def bump_bounty_issue(db, repository_name: str, number: int, bounty_amount: int):
    print(repository_name, number, bounty_amount)
    repository = await crud_repos.get_repository_by_name(repository_name, db)

    result_issues = await db.execute(
        select(Issues)
        .where(Issues.repository_id == repository.id)
        .where(Issues.number == number)
    )

    issue = result_issues.scalars().first()

    issue.cumulative_bounty = issue.cumulative_bounty + bounty_amount
    await db.commit()


def issue_state_to_str(state: bool) -> str:
    """Convert a boolean issue state to its corresponding string representation."""
    if state:
        return "open"
    return "closed"


def issue_state_to_bool(state: str) -> bool:
    """Convert issue state to a boolean value."""
    if state == "open":
        return True
    return False
