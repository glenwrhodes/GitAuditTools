# GitHub Audit Tool

A powerful tool to generate changelists, calculate work hours, and analyze coding patterns from GitHub repositories.

## Features

- **AI-Powered Changelists**: Generate professional client reports from your commits
- **Customizable Report Voice**: Control the tone and style of your reports (friendly, formal, enthusiastic, etc.)
- **Work Hours Calculation**: Estimate time spent coding based on commit patterns with realistic pre-work assumptions
- **Coding Rhythm Analysis**: Discover your most productive hours and days
- **Date Range Support**: Analyze single days, weeks, months, or custom ranges
- **Smart Token Management**: Automatically optimizes AI requests to stay within limits

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

## Commands

### Generate Changelists

Create professional work reports from your commits:

```bash
# Today's work
python github_audit_tool.py changelist myrepo

# Specific date
python github_audit_tool.py changelist myrepo -d 2023-12-15

# Date range
python github_audit_tool.py changelist myrepo -d "2023-12-01..2023-12-07"

# This week (keywords supported)
python github_audit_tool.py changelist myrepo -d week

# Include full diffs (more detailed but uses more AI tokens)
python github_audit_tool.py changelist myrepo -v

# Markdown format
python github_audit_tool.py changelist myrepo -f markdown -o report.md

# Customize report tone/voice
python github_audit_tool.py changelist myrepo --voice "friendly and upbeat"
python github_audit_tool.py changelist myrepo --voice "formal and concise"
python github_audit_tool.py changelist myrepo --voice "enthusiastic and detailed"
python github_audit_tool.py changelist myrepo --voice "technical but accessible to non-developers"

# Combine voice with other options
python github_audit_tool.py changelist myrepo -d week -f markdown --voice "professional yet conversational" -o weekly_report.md

# Entire repository history
python github_audit_tool.py changelist myrepo -d all
```

**Voice Options**: Use the `--voice` flag to customize how your reports sound:
- `"friendly and upbeat"` - Positive, engaging tone
- `"formal and concise"` - Professional, to-the-point style
- `"enthusiastic and detailed"` - Excited, comprehensive reporting
- `"technical but accessible"` - Detailed but understandable for non-developers
- `"casual and conversational"` - Relaxed, informal tone
- `"confident and results-focused"` - Emphasizes achievements and outcomes

**Supported date keywords**: `today`, `yesterday`, `week`, `this-week`, `last-week`, `month`, `this-month`, `last-month`, `all`, `alltime`

### Calculate Work Hours

Estimate time spent coding based on commit patterns:

```bash
# Today's hours
python github_audit_tool.py hours myrepo

# This week's breakdown
python github_audit_tool.py hours myrepo -d week

# Custom date range
python github_audit_tool.py hours myrepo -d "2023-12-01..2023-12-15"

# Total hours for entire project history
python github_audit_tool.py hours myrepo -d all
```

**How Hours Are Calculated:**
- **Pre-work assumption**: 30 minutes of work is assumed before your first commit (since you likely started working before committing)
- **Work blocks**: Commits separated by more than 2 hours are treated as separate work sessions
- **Post-work buffer**: 10 minutes added after the last commit for cleanup/testing
- **Minimum time**: At least 10 minutes per commit to account for actual work done
- **Display format**: Hours shown in both decimal (3.5 hours) and clock format (03:30) for easy reading

*Example: A single commit at 9:00 AM = 0.7 hours (00:40) total*

### Analyze Coding Rhythm

Discover your productivity patterns:

```bash
# This week's patterns (default)
python github_audit_tool.py rhythm myrepo

# Last month's patterns
python github_audit_tool.py rhythm myrepo -d last-month

# Custom range
python github_audit_tool.py rhythm myrepo -d "2023-11-01..2023-11-30"

# Lifetime coding patterns
python github_audit_tool.py rhythm myrepo -d all
```

The rhythm analysis shows:
- **Hourly patterns**: When you're most active throughout the day
- **Daily patterns**: Which days of the week you're most productive
- **Work insights**: Productivity tips based on your patterns
- **Visual charts**: ASCII bar charts of your coding activity

## Date Range Formats

The tool supports flexible date specifications:

### Single Dates
- `2023-12-15` - Specific date
- `today` - Current date
- `yesterday` - Previous day

### Date Ranges
- `2023-12-01..2023-12-07` - Custom range
- `2023-12-01:2023-12-07` - Alternative syntax
- `week` or `this-week` - Current week (Monday-Sunday)
- `last-week` - Previous week
- `month` or `this-month` - Current month
- `last-month` - Previous month
- `all` or `alltime` - Entire repository history (all commits ever made)

**Supported date keywords**: `today`, `yesterday`, `week`, `this-week`, `last-week`, `month`, `this-month`, `last-month`, `all`, `alltime`

**⚠️ Performance Note**: Using `all` with large repositories (thousands of commits) may take longer to process and could hit API rate limits. Consider using specific date ranges for large projects.

## Token Management

The tool intelligently manages AI token usage:

- **Default mode**: Uses commit messages only (lightweight, <5k tokens)
- **Verbose mode** (`-v`): Includes full diffs (detailed but more tokens)
- **Auto-fallback**: If full diffs exceed 100k tokens, falls back to messages
- **Hard limit**: Errors if data exceeds 128k tokens (suggests smaller range)

## Example Workflow

```bash
# 1. Analyze your week's rhythm
python github_audit_tool.py rhythm myrepo -d week

# 2. Calculate total hours worked
python github_audit_tool.py hours myrepo -d week

# 3. Generate client report with appropriate tone
python github_audit_tool.py changelist myrepo -d week -f markdown --voice "professional yet friendly" -o weekly_report.md
```

### Different Report Scenarios

```bash
# For client presentations (professional tone)
python github_audit_tool.py changelist myrepo -d week --voice "formal and results-focused" -f markdown

# For team standups (casual tone)
python github_audit_tool.py changelist myrepo -d today --voice "casual and conversational"

# For project managers (accessible technical details)
python github_audit_tool.py changelist myrepo -d month --voice "technical but accessible" -f markdown

# For personal review (detailed and enthusiastic)
python github_audit_tool.py changelist myrepo -d week --voice "enthusiastic and detailed"
```

### Project Analysis Workflow

```bash
# 1. Get lifetime coding patterns for the entire project
python github_audit_tool.py rhythm myrepo -d all

# 2. Calculate total project hours
python github_audit_tool.py hours myrepo -d all

# 3. Generate comprehensive project summary
python github_audit_tool.py changelist myrepo -d all -f markdown --voice "comprehensive and professional" -o project_summary.md
```

## Requirements

- Python 3.7+
- GitHub Personal Access Token
- OpenAI API Key

## Realistic Time Tracking

The tool uses intelligent assumptions to provide more accurate work hour estimates:

### Why 30 Minutes Pre-Work?
When you make your first commit of the day, you've likely been:
- Setting up your development environment
- Reading documentation or issues
- Planning your approach
- Writing initial code before the first commit

### Work Block Detection
- **Continuous work**: Commits within 2 hours are grouped as one work session
- **Work breaks**: Gaps longer than 2 hours indicate breaks (lunch, meetings, etc.)
- **Multiple sessions**: Each work block gets its own 30-minute pre-work assumption

### Example Time Calculations
```
Single commit at 9:00 AM:
→ 30 min prep (8:30-9:00) + 10 min commit = 40 minutes total

Three commits: 9:00 AM, 9:30 AM, 10:15 AM:
→ 30 min prep + 1h 15m span + 10 min buffer = 2h 15m total

Two separate sessions: 9:00 AM and 2:00 PM:
→ Session 1: 40 min (30+10)
→ Session 2: 40 min (30+10)
→ Total: 1h 20m
```

This approach provides more realistic billing and productivity tracking compared to simple "first commit to last commit" calculations.

## Dependencies

See `requirements.txt` for the complete list. Key dependencies:
- `PyGithub` - GitHub API integration
- `openai` - AI-powered changelist generation
- `tiktoken` - Token counting for AI optimization
- `click` - Command-line interface
- `colorama` - Colored terminal output

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

**Voice Customization Examples:**

*With `--voice "friendly and upbeat"`*:
> "🎉 What an amazing day of coding! We made fantastic progress on the user authentication system and the results are looking awesome! The new password reset feature is working beautifully..."

*With `--voice "formal and concise"`*:
> "This report summarizes the development activities completed on January 15, 2024. Primary objectives included authentication system enhancements and user interface improvements..."

*With `--voice "technical but accessible"`*:
> "Today's work centered around strengthening our user security infrastructure. We implemented several key improvements that will make the login experience both more secure and user-friendly..."

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

## License

This tool is provided as-is for personal and commercial use. Please ensure you comply with GitHub's and OpenAI's terms of service when using their APIs.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool! 