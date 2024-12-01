import os
from github import Github
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
from app.db import sessions
from app.db.models import Repositories

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


async def update_repositories():
    async for session in sessions.get_async_session():
        async with session.begin():
            for repo in repos:
                if not repo.archived:
                    # Check if the author already exists
                    result = await session.execute(select(Repositories).where(Repositories.name == repo.name))
                    existing_author = result.scalars().first()
                    if not existing_author:
                        print(repo.name)
                        session.add(Repositories(name=repo.name))
        await session.commit()


async def main():
    await update_repositories()


asyncio.run(main())
