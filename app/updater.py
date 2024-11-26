import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

# Replace with your GitHub access token
access_token = os.environ.get("GITHUB_TOKEN")

# Replace with your organization's name
org_name = 'elementary'

# Authenticate to GitHub
g = Github(access_token)

# Get the organization
org = g.get_organization(org_name)

# Get all repositories of the organization
repos = org.get_repos()

# Print repository names
for repo in repos:
    if not repo.archived:
        print(repo.name)
