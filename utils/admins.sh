#!/bin/bash

set -e

# Load GitHub token and repository name from environment variables
GITHUB_TOKEN=${GITHUB_TOKEN}
REPO_NAME=${GITHUB_REPOSITORY}

# Read the Terraform file
TERRAFORM_FILE_PATH="iam/identity_center.tf"

if [ ! -f "$TERRAFORM_FILE_PATH" ]; then
    echo "Terraform file not found at $TERRAFORM_FILE_PATH"
    exit 1
fi

# Print the contents of the Terraform file for debugging
echo "Contents of the Terraform file:"
cat $TERRAFORM_FILE_PATH

# Parse the Terraform file using jq
CONTENT=$(cat $TERRAFORM_FILE_PATH)
LOCALS_BLOCK=$(echo "$CONTENT" | jq -r '.locals[0]' || { echo "Error parsing locals block"; exit 1; })
SSO_ACCOUNTS=$(echo "$LOCALS_BLOCK" | jq -r '.sso_accounts' || { echo "Error parsing sso_accounts"; exit 1; })

if [ -z "$SSO_ACCOUNTS" ]; then
    echo "sso_accounts not found in the locals block"
    exit 1
fi

# Extract admin users
ADMIN_USERS=$(echo "$SSO_ACCOUNTS" | jq -r 'to_entries | map(select(.value.admin == true)) | .[].key')

if [ -n "$ADMIN_USERS" ]; then
    ISSUE_TITLE="Weekly Admin Access Report"
    ISSUE_BODY="## 🚀 Weekly Admin Access Report\n\nHello team! 👋\n\nHere's the list of users with admin access for this week:\n\n| GitHub Username | Full Name |\n| --- | --- |\n"

    for USERNAME in $ADMIN_USERS; do
        USER_DATA=$(echo "$SSO_ACCOUNTS" | jq -r --arg USERNAME "$USERNAME" '.[$USERNAME]')
        GIVEN=$(echo "$USER_DATA" | jq -r '.given')
        FAMILY=$(echo "$USER_DATA" | jq -r '.family')
        FULL_NAME="$GIVEN $FAMILY"
        ISSUE_BODY+="| @$USERNAME | $FULL_NAME |\n"
    done

    ISSUE_BODY+="\nPlease review if you still have a need for admin access, and if not kindly update the Terraform configuration and remove the flag. 🛠️\n\n"

    # Create a new issue using GitHub CLI
    echo "$ISSUE_BODY" | gh issue create --repo "$REPO_NAME" --title "$ISSUE_TITLE" --body -
else
    echo "No admin users found"
fi

exit 0
