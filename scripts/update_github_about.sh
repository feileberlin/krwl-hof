#!/bin/bash
#
# Update GitHub Repository Details
# This script updates the repository About section using GitHub CLI
#
# Prerequisites: GitHub CLI (gh) must be installed and authenticated
# Install: https://cli.github.com/
#
# Usage: bash scripts/update_github_about.sh
#

set -e

REPO_OWNER="feileberlin"
REPO_NAME="krwl-hof"
REPO_FULL="${REPO_OWNER}/${REPO_NAME}"

echo "🔧 Updating GitHub repository details for ${REPO_FULL}..."
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed"
    echo "   Please install from: https://cli.github.com/"
    echo ""
    echo "   Or update manually:"
    echo "   1. Go to https://github.com/${REPO_FULL}/settings"
    echo "   2. Update the Description and Website fields"
    echo "   3. Add topics from .github/repository-settings.json"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub CLI"
    echo "   Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

# Load settings from JSON file
SETTINGS_FILE=".github/repository-settings.json"

if [ ! -f "$SETTINGS_FILE" ]; then
    echo "❌ Error: Settings file not found: $SETTINGS_FILE"
    exit 1
fi

DESCRIPTION=$(jq -r '.description' "$SETTINGS_FILE")
HOMEPAGE=$(jq -r '.homepage' "$SETTINGS_FILE")
TOPICS=$(jq -r '.topics | join(",")' "$SETTINGS_FILE")

echo "📝 Repository Details:"
echo "   Description: $DESCRIPTION"
echo "   Homepage: $HOMEPAGE"
echo "   Topics: $TOPICS"
echo ""

# Update repository description and homepage
echo "🔄 Updating repository description and homepage..."
gh repo edit "$REPO_FULL" \
    --description "$DESCRIPTION" \
    --homepage "$HOMEPAGE"

if [ $? -eq 0 ]; then
    echo "✅ Repository description and homepage updated"
else
    echo "❌ Failed to update repository description and homepage"
    exit 1
fi

# Update topics (GitHub CLI doesn't have a direct command for this, use API)
echo ""
echo "🔄 Updating repository topics..."

# Read topics as JSON array
TOPICS_JSON=$(jq '.topics' "$SETTINGS_FILE")

gh api \
    -X PUT \
    "/repos/${REPO_FULL}/topics" \
    -f names="$TOPICS_JSON" \
    --silent

if [ $? -eq 0 ]; then
    echo "✅ Repository topics updated"
else
    echo "❌ Failed to update repository topics"
    exit 1
fi

echo ""
echo "🎉 GitHub repository details updated successfully!"
echo ""
echo "🌐 View at: https://github.com/${REPO_FULL}"
echo ""
echo "Note: You may need to manually configure additional settings at:"
echo "   https://github.com/${REPO_FULL}/settings"
