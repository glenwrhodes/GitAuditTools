# 🚀 Quick Start Guide

Get your GitHub Auditing Tool up and running in 5 minutes!

## 📋 Prerequisites

- Python 3.7+ installed
- Git (optional, for cloning)
- GitHub Personal Access Token
- OpenAI API Key with credits

## ⚡ 5-Minute Setup

### 1. Install Dependencies
```bash
# Navigate to the tool directory
cd GitAuditTools

# Install required packages
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
# Windows
audit.bat setup

# Mac/Linux
python github_audit_tool.py setup
```

When prompted, enter:
- **GitHub Token**: Get from [github.com/settings/tokens](https://github.com/settings/tokens)
- **OpenAI Key**: Get from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### 3. Test the Tool
```bash
# Generate today's changelist (replace with your repo)
audit.bat changelist yourusername/your-repo

# Check work hours for today
audit.bat hours yourusername/your-repo
```

## 🎯 Common Use Cases

### Daily Client Reports
```bash
# Generate professional changelist for yesterday
audit.bat changelist mycompany/client-project --date 2024-01-15 --output client-report.txt
```

### Time Tracking
```bash
# See how many hours you worked on a specific day
audit.bat hours mycompany/project --date 2024-01-15
```

### Team Analysis
```bash
# Analyze specific team member's work
audit.bat changelist mycompany/project --author "developer@company.com" --date 2024-01-15
```

## 🛠 GitHub Token Setup (2 minutes)

1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Name it "Audit Tool"
4. Check these boxes:
   - ✅ `repo` (Full repository access)
   - ✅ `read:user` (Read user profile)
5. Click "Generate token"
6. **Copy the token immediately!**

## 💰 OpenAI API Setup (2 minutes)

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create account
3. Click "Create new secret key"
4. Name it "GitHub Audit Tool"
5. **Copy the key immediately!**
6. Add credits to your account ([Billing page](https://platform.openai.com/account/billing))

## 🎉 You're Ready!

Try these commands to see your tool in action:

```bash
# Help
audit.bat --help

# Today's work summary
audit.bat changelist username/repo

# Hours worked today  
audit.bat hours username/repo

# Yesterday's report saved to file
audit.bat changelist username/repo --date 2024-01-15 --output report.txt
```

## 💡 Pro Tips

- **Repository Format**: Always use `username/repository-name` or `organization/repository-name`
- **Date Format**: Use `YYYY-MM-DD` (e.g., `2024-01-15`)
- **Private Repos**: Make sure your GitHub token has `repo` scope
- **Cost Control**: Monitor OpenAI usage - each report costs ~$0.10-0.50

## 🆘 Need Help?

- **Can't find repo**: Check the repository name format and your GitHub token permissions
- **No commits found**: Verify the date and author filters
- **API errors**: Check your API keys and account credits
- **Import errors**: Run `pip install -r requirements.txt` again

## 📚 Next Steps

- Read the full [README.md](README.md) for advanced features
- Check out [example_usage.py](example_usage.py) for programmatic usage
- Customize the AI prompts in the main script for your specific needs

Happy auditing! 🎯 