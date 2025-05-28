# GitHub Auditing Tool

A powerful Python tool for auditing GitHub repositories that can:

1. **Generate AI-powered changelists** - Create professional end-of-day work reports by feeding commit diffs to OpenAI
2. **Calculate work hours** - Estimate hours worked based on first and last commit timestamps for any given day

Perfect for developers who need to provide clients with detailed work reports or track their daily productivity.

## Features

- 🤖 **AI-Generated Changelists**: Uses OpenAI GPT-4 to create professional, client-friendly work reports
- ⏰ **Work Hours Calculation**: Automatically calculates hours worked based on commit patterns
- 🎨 **Beautiful CLI**: Colorized output with clear formatting
- 📁 **Export Options**: Save changelists to files for easy sharing
- 🔍 **Flexible Filtering**: Filter by date, author, and repository
- 🛡️ **Secure Configuration**: Environment variable-based API key management

## Installation

### 1. Clone or Download
```bash
git clone <your-repo-url>
cd GitAuditTools
```

### 2. Set up Virtual Environment
```bash
# Activate your existing virtual environment
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
Run the setup command to configure your API credentials:

**Windows (using batch file):**
```bash
audit.bat setup
```

**Manual (all platforms):**
```bash
python github_audit_tool.py setup
```

This will prompt you for:
- **GitHub Personal Access Token**
- **OpenAI API Key**

## API Keys Setup

### GitHub Personal Access Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name like "GitHub Audit Tool"
4. Select the following scopes:
   - `repo` (Full control of private repositories)
   - `read:user` (Read access to user profile data)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

### OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in to your account (or create one)
3. Click "Create new secret key"
4. Give it a name like "GitHub Audit Tool"
5. **Copy the key immediately** (you won't see it again!)

**Note**: You'll need credits in your OpenAI account to use the API. The tool uses GPT-4 which costs approximately $0.03 per 1K tokens.

## Usage

### Generate a Changelist

Generate an AI-powered changelist for today:

**Windows (using batch file):**
```bash
audit.bat changelist username/repository-name
```

**Manual (all platforms):**
```bash
python github_audit_tool.py changelist username/repository-name
```

For a specific date:
```bash
audit.bat changelist username/repository-name --date 2024-01-15
```

Save to a file:
```bash
audit.bat changelist username/repository-name --date 2024-01-15 --output report.txt
```

Filter by specific author:
```bash
audit.bat changelist username/repository-name --author "developer@example.com"
```

### Calculate Work Hours

Calculate hours worked today:
```bash
audit.bat hours username/repository-name
```

For a specific date:
```bash
audit.bat hours username/repository-name --date 2024-01-15
```

### Get Help

```bash
audit.bat --help
audit.bat changelist --help
audit.bat hours --help
```

## Example Output

### Changelist Example
```
============================================================
CHANGELIST FOR 2024-01-15
============================================================

## Daily Work Summary - January 15, 2024

### Overview
Today's development focused on enhancing the user authentication system and improving the overall user experience of the application.

### Key Features Implemented
- **Enhanced User Authentication**: Implemented secure password reset functionality with email verification
- **UI/UX Improvements**: Updated the login page with modern styling and better responsive design
- **Database Optimization**: Added proper indexing to user tables for improved query performance

### Bug Fixes and Improvements
- Fixed issue with session timeout handling
- Resolved responsive design issues on mobile devices
- Improved error messaging throughout the authentication flow

### Technical Details
- Added bcrypt password hashing for enhanced security
- Implemented JWT token refresh mechanism
- Updated database migrations for new user fields
```

### Hours Report Example
```
==================================================
WORK HOURS FOR 2024-01-15
==================================================

Total commits: 8
First commit: 09:15:32 UTC
Last commit:  17:42:18 UTC
Estimated hours worked: 9.4 hours

Commit Summary:
   1. 09:15 - Initial setup of password reset functionality
   2. 10:30 - Add email verification system
   3. 11:45 - Update login page styling
   4. 13:20 - Fix responsive design issues
   5. 14:15 - Add password strength validation
   6. 15:30 - Implement JWT refresh tokens
   7. 16:45 - Update database migrations
   8. 17:42 - Final testing and bug fixes
```

## Configuration File

The tool creates a `.env` file to store your API keys securely:

```env
# GitHub Auditing Tool Configuration
GITHUB_TOKEN=your_github_token_here
OPENAI_API_KEY=your_openai_key_here
```

**Important**: Add `.env` to your `.gitignore` file to keep your API keys secure!

## Troubleshooting

### Common Issues

1. **"Repository not found"**
   - Make sure the repository name is correct (format: `username/repo-name`)
   - Ensure your GitHub token has access to the repository
   - For private repos, make sure the `repo` scope is enabled

2. **"No commits found"**
   - Check if there were actually commits on the specified date
   - Verify the author filter (if used)
   - Try a different date range

3. **OpenAI API errors**
   - Ensure you have credits in your OpenAI account
   - Check if your API key is valid and active
   - Verify your account has access to GPT-4

4. **Permission errors**
   - Make sure your GitHub token has the necessary scopes
   - For organization repos, you might need additional permissions

### GitHub Token Scopes

Make sure your GitHub token has these scopes:
- `repo` - Access to repositories
- `read:user` - Read user information

## Security Notes

- Never commit your `.env` file to version control
- Regularly rotate your API keys
- Use the minimum required scopes for your GitHub token
- Monitor your OpenAI usage to avoid unexpected charges

## Dependencies

- `PyGithub` - GitHub API interaction
- `openai` - OpenAI API integration
- `click` - Command-line interface
- `colorama` - Cross-platform colored output
- `python-dotenv` - Environment variable management
- `python-dateutil` - Date parsing utilities
- `pytz` - Timezone handling

## License

This tool is provided as-is for personal and commercial use. Please ensure you comply with GitHub's and OpenAI's terms of service when using their APIs.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool! 