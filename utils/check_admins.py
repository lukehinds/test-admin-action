#!/usr/bin/env python3
import os
import json
from github import Github
from tfparse import load

# Load GitHub token from environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_NAME = os.getenv('GITHUB_REPOSITORY')

# Read the Terraform file
terraform_file_path = 'iam/identity_center.tf'

if not os.path.exists(terraform_file_path):
    print(f"File not found: {terraform_file_path}")
    exit(1)

# Parse the Terraform file using tfparse
with open(terraform_file_path, 'r') as file:
    config = load(file)

# Extract sso_accounts from locals
locals_block = config['locals'][0]
sso_accounts = locals_block['sso_accounts']

if not sso_accounts:
    raise ValueError("sso_accounts not found in the locals block")

# Extract admin users
admin_users = []
for username, user_data in sso_accounts.items():
    if user_data.get('admin') == True:
        admin_users.append(username)

if admin_users:
    issue_title = "Weekly Admin Access Report"
    issue_body = (
        "## 🚀 Weekly Admin Access Report\n\n"
        "Hello team! 👋\n\n"
        "Here's the list of users with admin access for this week:\n\n"
        "| GitHub Username | Full Name |\n"
        "| --- | --- |\n"
    )
    for username, user_data in sso_accounts.items():
        if user_data.get('admin') == True:
            full_name = f"{user_data['given']} {user_data['family']}"
            issue_body += f"| @{username} | {full_name} |\n"
    
    issue_body += (
        "\nPlease review the list and ensure that it is up-to-date. "
        "If there are any discrepancies, kindly update the Terraform configuration. 🛠️\n\n"
        "Have a great week! ✨"
    )

    print(issue_body)
    
    # Initialize GitHub client
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    # Create a new issue
    repo.create_issue(
        title=issue_title,
        body=issue_body
    )
    print(f"Issue created successfully in repository {REPO_NAME}")
else:
    print("No admin users found")
