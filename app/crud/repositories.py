from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Repositories

async def check_repository_exists(repo_name: str, db: AsyncSession) -> Repositories | None:
    """
    Check if a repository with the given name exists in the database.

    Args:
        repo_name (str): The name of the repository to check.
        db (AsyncSession): The database session to use for the query.

    Returns:
        Repositories or None: The repository object if it exists, otherwise None.
    """
    result = await db.execute(
        select(Repositories).where(Repositories.name == repo_name)
    )
    return result.scalars().first()

async def get_repository_by_issue(issue, db: AsyncSession) -> Repositories:
    """
    Get or create a repository by issue.

    Args:
        issue (dict): The issue containing the repository URL.
        db (AsyncSession): The database session to use for the query.

    Returns:
        Repositories: The repository object.
    """
    repo_name = issue["repository_url"].split('/')[-1]
    repo_db = await check_repository_exists(repo_name, db)
    if not repo_db:
        print("Repository does not exist.")
        repo_db = Repositories(name=repo_name)
        db.add(repo_db)
        await db.commit()
        print("Issue created.")
    return repo_db

async def get_repository_by_name(repo_name: str, db: AsyncSession) -> Repositories:
    """Fetch a repository by its name from the database."""
    result_repository = await db.execute(
        select(Repositories).where(Repositories.name == repo_name)
    )
    return result_repository.scalars().first()