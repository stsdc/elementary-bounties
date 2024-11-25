from github import Github

# Replace with your GitHub access token
access_token = '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'

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
