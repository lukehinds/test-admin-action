#!/usr/bin/env python3
import hcl2
import os
from github import Github

def debug_print(msg):
    """Helper function to print debug messages."""
    print(f"[DEBUG] {msg}")

# Set your GitHub token and repository name here for testing
# Load GitHub token from environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_NAME = os.getenv('GITHUB_REPOSITORY')

debug_print("Loaded environment variables.")

# Read the Terraform file
terraform_file_path = 'iam/identity_center.tf'

if not os.path.exists(terraform_file_path):
    raise FileNotFoundError(f"Terraform file not found at {terraform_file_path}")
    exit(1)

debug_print(f"Found Terraform file at {terraform_file_path}")

try:
    with open(terraform_file_path, 'r') as file:
        content = hcl2.load(file)
    debug_print("Parsed Terraform file.")
except Exception as e:
    print(f"Error parsing Terraform file: {e}")
    exit(1)

# Extract sso_accounts from locals
try:
    locals_block = content.get('locals', [{}])[0]
    sso_accounts = locals_block.get('sso_accounts', {})
    debug_print("Extracted sso_accounts.")
except Exception as e:
    print(f"Error extracting sso_accounts: {e}")
    exit(1)

if not sso_accounts:
    print("sso_accounts not found in the locals block")
    exit(1)

# Extract admin users
admin_users = []
for username, user_data in sso_accounts.items():
    if user_data.get('admin') == True:
        admin_users.append(username)

debug_print(f"Found {len(admin_users)} admin users.")

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
        "\nPlease review if you still have a need for admin access, and if not kindly update the Terraform configuration and remove the flag. 🛠️\n\n"
    )
    
    # Initialize GitHub client
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        debug_print("Initialized GitHub client.")
    except Exception as e:
        print(f"Error initializing GitHub client: {e}")
        exit(1)
    
    # Create a new issue
    try:
        repo.create_issue(
            title=issue_title,
            body=issue_body
        )
        debug_print(f"Issue created successfully in repository {REPO_NAME}")
    except Exception as e:
        print(f"Error creating issue: {e}")
        exit(1)
else:
    print("No admin users found")
    exit(0)

debug_print("Script completed successfully.")
exit(0)
