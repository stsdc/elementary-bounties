import os
from github import Github
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
from app.db import sessions
from app.db.models import Repositories, Issues

load_dotenv()

async_session = sessions.get_async_session()

# Replace with your GitHub access token
access_token = os.environ.get("GITHUB_TOKEN")

# Replace with your organization's name
org_name = "elementary"

# Authenticate to GitHub
g = Github(access_token)

# Get the organization
org = g.get_organization(org_name)

# Get all repositories of the organization
repos = org.get_repos()


async def repository_exists(repo, session):
    result = await session.execute(
        select(Repositories).where(Repositories.name == repo.name)
    )
    return result.scalars().first()


async def update_repositories():
    async for session in sessions.get_async_session():
        async with session.begin():
            for repo in repos:
                if not repo.archived:
                    if not await repository_exists(repo, session):
                        print(repo.name)
                        session.add(Repositories(name=repo.name))

        await session.commit()


labels_filter = ["Status: Confirmed"]


async def get_db_repos(session):
    q = select(Repositories)
    result = await session.execute(q)
    return result.scalars().all()

async def issue_exists(issue_number, session):
    result = await session.execute(
        select(Issues).where(Issues.issue_number == issue_number)
    )
    return result.scalars().first()

# async def issue_exists()
async def update_issues():
    counter = 0
    async for session in sessions.get_async_session():
        async with session.begin():
            for repo in repos:
                if not repo.archived:
                    counter += 1
                    if counter >= 7:
                        break
                    for issue in repo.get_issues(labels=labels_filter):
                        if not await issue_exists(issue.number, session):
                            print(repo.name, issue.title)
                            db_repo = await repository_exists(repo, session)
                            session.add(
                                Issues(
                                    title=issue.title,
                                    repository_id=db_repo.id,
                                    issue_number=issue.number,
                                )
                            )
        await session.commit()


async def main():
    # await update_repositories()
    await update_issues()


asyncio.run(main())
