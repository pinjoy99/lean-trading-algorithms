# GitHub Credentials Management

This document explains how your GitHub personal access token is securely stored and used for git operations.

## 🔐 Token Storage

Your GitHub personal access token is stored in multiple secure locations:

### 1. Git Credential Store (`~/.git-credentials`)
- **Location**: `~/.git-credentials`
- **Permissions**: `600` (owner read/write only)
- **Content**: `https://pinjoy99:TOKEN@github.com`
- **Usage**: Automatic authentication for all git operations

### 2. Environment File (`.env`)
- **Location**: `/home/pinjoy/projects/lean/.env`
- **Status**: ❌ Already in `.gitignore` (never committed)
- **Usage**: Source with `source .env` for environment variables

### 3. Setup Script (`setup-github-credentials.sh`)
- **Location**: `/home/pinjoy/projects/lean/setup-github-credentials.sh`
- **Purpose**: One-command credential setup
- **Usage**: `source setup-github-credentials.sh`

## 🚀 Quick Start

### For Current Session
```bash
# Automatically configured - just use git commands
git push origin main
git pull origin main
```

### For New Terminal Session
```bash
# Load credentials
source ~/.bashrc  # or restart terminal
# or manually
source setup-github-credentials.sh
```

### For Git MCP Tools
Your token is configured and ready to use with GitHub MCP tools.

## 🔧 Configuration Details

### Git Global Settings
```bash
git config --global user.name "pinjoy99"
git config --global user.email "pinjoy99@gmail.com"
git config --global credential.helper store
```

### Repository Remote URL
```bash
git remote get-url origin
# Returns: https://[YOUR_TOKEN]@github.com/pinjoy99/lean-trading-algorithms.git
```

## 📝 File Locations

| File | Location | Purpose | Safe to Commit? |
|------|----------|---------|-----------------|
| Token | `~/.git-credentials` | Git authentication | ❌ No (home directory) |
| .env | `/home/pinjoy/projects/lean/.env` | Environment variables | ❌ No (in .gitignore) |
| setup script | `/home/pinjoy/projects/lean/setup-github-credentials.sh` | Credential setup | ✅ Yes |
| README | `/home/pinjoy/projects/lean/GITHUB-CREDENTIALS.md` | This documentation | ✅ Yes |

## 🔒 Security Features

### ✅ What's Protected
1. **Token never in git history**: Stored in home directory, not repository
2. **File permissions**: `~/.git-credentials` is `600` (owner-only)
3. **.gitignore protection**: `.env` excluded from commits
4. **No hardcoded values**: Token stored in secure locations only

### ⚠️ Best Practices
1. **Never commit the token**: It's already protected by .gitignore
2. **Use environment variables**: Load with `source .env` when needed
3. **Rotate token periodically**: Update if security is compromised
4. **Monitor token usage**: Check GitHub account for unauthorized access

## 🔄 Updating Credentials

### If Token Changes
1. **Update credential store**:
   ```bash
   echo "https://pinjoy99:NEW_TOKEN@github.com" > ~/.git-credentials
   chmod 600 ~/.git-credentials
   ```

2. **Update remote URL**:
   ```bash
   git remote set-url origin "https://NEW_TOKEN@github.com/pinjoy99/lean-trading-algorithms.git"
   ```

3. **Update environment file**:
   ```bash
   # Edit /home/pinjoy/projects/lean/.env
   export GITHUB_TOKEN="NEW_TOKEN"
   ```

4. **Update setup script**:
   ```bash
   # Edit /home/pinjoy/projects/lean/setup-github-credentials.sh
   export GITHUB_TOKEN="NEW_TOKEN"
   ```

### Run Setup Again
```bash
source setup-github-credentials.sh
```

## 📊 Verification Commands

### Check Git Configuration
```bash
git config --global --list | grep -E "(user\.|credential)"
```

### Check Credential File
```bash
ls -la ~/.git-credentials
cat ~/.git-credentials
```

### Check Remote URL
```bash
git remote get-url origin
```

### Test Authentication
```bash
git ls-remote origin
```

## 🎯 Usage Examples

### Clone Repository
```bash
git clone https://github.com/pinjoy99/lean-trading-algorithms.git
cd lean-trading-algorithms
```

### Push Changes
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

### Pull Updates
```bash
git pull origin main
```

### Use with Git MCP
```bash
# Token is already configured
# Use GitHub MCP tools normally
```

## 🚨 Troubleshooting

### "Authentication failed"
```bash
# Reload credentials
source setup-github-credentials.sh

# Or manually update
echo "https://pinjoy99:[YOUR_TOKEN]@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials
```

### "Permission denied"
```bash
# Fix credential file permissions
chmod 600 ~/.git-credentials
```

### "Remote not found"
```bash
# Check remote URL
git remote -v
git remote get-url origin
```

## 📞 Support

If you encounter issues:
1. Check this documentation
2. Run verification commands
3. Reload credentials with setup script
4. Verify token hasn't expired in GitHub settings

---

**Last Updated**: November 5, 2025
**Token**: `[YOUR_TOKEN_HERE]`
**Status**: ✅ Active and configured
