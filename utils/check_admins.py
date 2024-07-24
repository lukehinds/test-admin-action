import hcl2
import os
from github import Github

def debug_print(msg):
    """Helper function to print debug messages."""
    print(f"[DEBUG] {msg}")

class TerraformFileError(Exception):
    pass

class SsoAccountsError(Exception):
    pass

class GitHubClientError(Exception):
    pass

debug_print("Starting the script.")

# Set your GitHub token and repository name here for testing
# Load GitHub token from environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_NAME = os.getenv('GITHUB_REPOSITORY')

if not GITHUB_TOKEN:
    raise GitHubClientError("GitHub token not found in environment variables.")
if not REPO_NAME:
    raise GitHubClientError("GitHub repository name not found in environment variables.")

debug_print("Loaded environment variables.")

# Read the Terraform file
terraform_file_path = 'iam/identity_center.tf'

if not os.path.exists(terraform_file_path):
    raise TerraformFileError(f"File not found: {terraform_file_path}")

debug_print(f"Found Terraform file at {terraform_file_path}")

try:
    with open(terraform_file_path, 'r') as file:
        content = hcl2.load(file)
    debug_print("Parsed Terraform file.")
except Exception as e:
    raise TerraformFileError(f"Error parsing Terraform file: {e}")

# Extract sso_accounts from locals
try:
    locals_block = content.get('locals', [{}])[0]
    sso_accounts = locals_block.get('sso_accounts', {})
    debug_print("Extracted sso_accounts.")
except Exception as e:
    raise SsoAccountsError(f"Error extracting sso_accounts: {e}")

if not sso_accounts:
    raise SsoAccountsError("sso_accounts not found in the locals block")

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

    debug_print("Generated issue body.")

    # Initialize GitHub client
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        debug_print("Initialized GitHub client.")
    except Exception as e:
        raise GitHubClientError(f"Error initializing GitHub client: {e}")
    
    # Create a new issue
    try:
        repo.create_issue(
            title=issue_title,
            body=issue_body
        )
        debug_print(f"Issue created successfully in repository {REPO_NAME}")
    except Exception as e:
        raise GitHubClientError(f"Error creating issue: {e}")
else:
    debug_print("No admin users found")

debug_print("Script completed successfully.")
