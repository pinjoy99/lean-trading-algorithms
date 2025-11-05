#!/bin/bash
# GitHub Credentials Setup Script
# This script configures git to use your GitHub personal access token

echo "🔐 Setting up GitHub credentials..."

# Set your GitHub credentials
export GITHUB_TOKEN="[YOUR_TOKEN_HERE]"
export GITHUB_USERNAME="pinjoy99"
export GITHUB_EMAIL="pinjoy99@gmail.com"

# Configure git globally (if not already done)
git config --global user.name "$GITHUB_USERNAME"
git config --global user.email "$GITHUB_EMAIL"

# Store credentials in git credential store
echo "https://$GITHUB_USERNAME:$GITHUB_TOKEN@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

# Update remote URL to use token (for this repository)
git remote set-url origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/lean-trading-algorithms.git"

echo "✅ GitHub credentials configured successfully!"
echo ""
echo "Current configuration:"
echo "  Username: $GITHUB_USERNAME"
echo "  Email: $GITHUB_EMAIL"
echo "  Remote URL: $(git remote get-url origin)"
echo ""
echo "Now you can use:"
echo "  git push origin main"
echo "  git pull origin main"
echo "  git clone https://github.com/$GITHUB_USERNAME/lean-trading-algorithms.git"
echo ""
echo "The token is saved in ~/.git-credentials (permissions: 600)"
echo "Load this script anytime with: source setup-github-credentials.sh"
