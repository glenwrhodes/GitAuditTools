#!/usr/bin/env python3
"""
GitHub Auditing Tool
A tool to generate changelists and calculate work hours from GitHub repositories.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import click
from colorama import init, Fore, Style
from github import Github, GithubException
from openai import OpenAI
from dotenv import load_dotenv
import json
from dateutil import parser
import pytz

# Initialize colorama for cross-platform colored output
init()

# Load environment variables
load_dotenv()

class GitHubAuditTool:
    def __init__(self, github_token: str, openai_api_key: str):
        """Initialize the GitHub audit tool with API keys."""
        try:
            self.github = Github(github_token)
            self.user = self.github.get_user()
        except Exception as e:
            raise Exception(f"Failed to initialize GitHub client: {e}")
        
        try:
            # Simple OpenAI client initialization - automatically uses OPENAI_API_KEY from environment
            self.openai_client = OpenAI()
        except Exception as e:
            raise Exception(f"Failed to initialize OpenAI client: {e}")
        
    def get_repository(self, repo_name: str):
        """Get a GitHub repository object."""
        try:
            # Try user's repository first
            return self.user.get_repo(repo_name)
        except GithubException:
            # Try organization repository
            try:
                return self.github.get_repo(repo_name)
            except GithubException as e:
                raise Exception(f"Repository '{repo_name}' not found: {e}")
    
    def get_commits_for_date(self, repo, target_date: datetime, author: Optional[str] = None) -> List:
        """Get all commits for a specific date."""
        # Set timezone to UTC if not specified
        if target_date.tzinfo is None:
            target_date = target_date.replace(tzinfo=pytz.UTC)
        
        # Define the date range (start and end of the day)
        start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        commits = []
        
        try:
            # Get commits for the date range
            repo_commits = repo.get_commits(
                since=start_date,
                until=end_date,
                author=author or self.user.login
            )
            
            for commit in repo_commits:
                commits.append(commit)
                
        except GithubException as e:
            click.echo(f"{Fore.YELLOW}Warning: {e}{Style.RESET_ALL}")
        
        return commits
    
    def calculate_work_hours(self, commits: List) -> Tuple[float, datetime, datetime, List]:
        """Calculate work hours based on commit patterns, detecting work blocks and gaps."""
        if not commits:
            return 0.0, None, None, []
        
        # Sort commits by date
        sorted_commits = sorted(commits, key=lambda c: c.commit.author.date)
        
        if len(sorted_commits) == 1:
            # Single commit = 10 minutes of work
            commit_time = sorted_commits[0].commit.author.date
            return 0.17, commit_time, commit_time, [{'start': commit_time, 'end': commit_time, 'hours': 0.17, 'commits': 1}]
        
        # Group commits into work blocks
        work_blocks = []
        current_block_start = sorted_commits[0].commit.author.date
        current_block_commits = [sorted_commits[0]]
        
        # Consider a gap of more than 2 hours as a break between work sessions
        MAX_GAP_HOURS = 2
        
        for i in range(1, len(sorted_commits)):
            current_commit = sorted_commits[i]
            previous_commit = sorted_commits[i-1]
            
            time_gap = current_commit.commit.author.date - previous_commit.commit.author.date
            gap_hours = time_gap.total_seconds() / 3600
            
            if gap_hours > MAX_GAP_HOURS:
                # End current block and start a new one
                block_end = previous_commit.commit.author.date
                block_hours = self._calculate_block_hours(current_block_start, block_end, len(current_block_commits))
                
                work_blocks.append({
                    'start': current_block_start,
                    'end': block_end, 
                    'hours': block_hours,
                    'commits': len(current_block_commits)
                })
                
                # Start new block
                current_block_start = current_commit.commit.author.date
                current_block_commits = [current_commit]
            else:
                # Continue current block
                current_block_commits.append(current_commit)
        
        # Add the final block
        block_end = sorted_commits[-1].commit.author.date
        block_hours = self._calculate_block_hours(current_block_start, block_end, len(current_block_commits))
        
        work_blocks.append({
            'start': current_block_start,
            'end': block_end,
            'hours': block_hours, 
            'commits': len(current_block_commits)
        })
        
        # Calculate total hours
        total_hours = sum(block['hours'] for block in work_blocks)
        first_commit_time = sorted_commits[0].commit.author.date
        last_commit_time = sorted_commits[-1].commit.author.date
        
        return total_hours, first_commit_time, last_commit_time, work_blocks
    
    def _calculate_block_hours(self, start_time: datetime, end_time: datetime, commit_count: int) -> float:
        """Calculate hours for a single work block."""
        if start_time == end_time:
            # Single commit in block = 10 minutes
            return 0.17
        
        # Calculate actual time span
        time_diff = end_time - start_time
        span_hours = time_diff.total_seconds() / 3600
        
        # Add 15 minutes buffer (before first and after last commit in block)
        buffered_hours = span_hours + 0.25
        
        # Minimum time per commit is 10 minutes
        min_hours = commit_count * 0.17
        
        # Return the larger of the two estimates
        return max(buffered_hours, min_hours)
    
    def get_commit_diffs(self, commits: List) -> str:
        """Get diffs for all commits."""
        all_diffs = []
        
        for commit in commits:
            try:
                # Get the commit details with diff
                commit_data = {
                    'sha': commit.sha[:8],
                    'message': commit.commit.message,
                    'timestamp': commit.commit.author.date.isoformat(),
                    'files_changed': []
                }
                
                # Get files changed in this commit
                for file in commit.files:
                    file_data = {
                        'filename': file.filename,
                        'status': file.status,
                        'additions': file.additions,
                        'deletions': file.deletions,
                        'patch': file.patch if hasattr(file, 'patch') and file.patch else None
                    }
                    commit_data['files_changed'].append(file_data)
                
                all_diffs.append(commit_data)
                
            except Exception as e:
                click.echo(f"{Fore.YELLOW}Warning: Could not get diff for commit {commit.sha[:8]}: {e}{Style.RESET_ALL}")
        
        return json.dumps(all_diffs, indent=2)
    
    def generate_changelist_with_ai(self, diffs: str, date: datetime, output_format: str = 'text') -> str:
        """Generate a professional changelist using OpenAI."""
        
        # Base prompt for the changelist
        base_prompt = f"""
You are a professional software developer writing an end-of-day work report for a client.

Based on the following Git commit data from {date.strftime('%Y-%m-%d')}, please generate a clear, professional changelist that summarizes the work completed. 

Format the response as a client-friendly report with:
1. A brief summary of the day's work
2. Key features/changes implemented
3. Bug fixes or improvements made
4. Any technical details that might be relevant - but make sure not to be too technical. This is for a non-technical audience. Don't quote filenames or anything like that. Keep it digestible.

Make it sound professional and client-appropriate, avoiding overly technical jargon where possible.
"""

        # Add format-specific instructions
        if output_format.lower() == 'markdown':
            format_instruction = """
Please format your response using Markdown syntax. You may use headers, bullet points, code blocks, emphasis, and other Markdown formatting to make the report well-structured and readable.
"""
        else:  # text format
            format_instruction = """
Please format your response as plain text only. Do NOT use any Markdown formatting, asterisks for emphasis, hash symbols for headers, or any other special formatting characters. Use only plain text with proper spacing and line breaks for structure.
"""

        full_prompt = base_prompt + format_instruction + f"""
Git commit data:
{diffs}

Please provide a well-structured report:
"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional software developer writing client reports."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=5500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating AI changelist: {e}\n\nRaw commit data:\n{diffs}"

def validate_environment():
    """Validate that required environment variables are set."""
    github_token = os.getenv('GITHUB_TOKEN')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    missing = []
    if not github_token:
        missing.append('GITHUB_TOKEN')
    if not openai_api_key:
        missing.append('OPENAI_API_KEY')
    
    if missing:
        click.echo(f"{Fore.RED}Error: Missing required environment variables: {', '.join(missing)}{Style.RESET_ALL}")
        click.echo(f"{Fore.YELLOW}Please set these in your .env file or environment.{Style.RESET_ALL}")
        return False
    
    return True, github_token, openai_api_key

@click.group()
def cli():
    """GitHub Auditing Tool - Generate changelists and calculate work hours."""
    pass

@cli.command()
@click.argument('repository')
@click.option('--date', '-d', help='Date to analyze (YYYY-MM-DD). Default: today')
@click.option('--author', '-a', help='Specific author to filter commits. Default: authenticated user')
@click.option('--output', '-o', help='Output file to save the changelist')
@click.option('--format', '-f', type=click.Choice(['text', 'markdown'], case_sensitive=False), 
              default='text', help='Output format: text (plain text) or markdown. Default: text')
def changelist(repository, date, author, output, format):
    """Generate an AI-powered changelist for a specific date."""
    
    # Validate environment
    validation_result = validate_environment()
    if not validation_result:
        sys.exit(1)
    
    _, github_token, openai_api_key = validation_result
    
    # Parse date
    if date:
        try:
            target_date = parser.parse(date)
        except ValueError:
            click.echo(f"{Fore.RED}Error: Invalid date format. Use YYYY-MM-DD{Style.RESET_ALL}")
            sys.exit(1)
    else:
        target_date = datetime.now()
    
    try:
        # Initialize the tool
        audit_tool = GitHubAuditTool(github_token, openai_api_key)
        
        # Get repository
        click.echo(f"{Fore.BLUE}Analyzing repository: {repository}{Style.RESET_ALL}")
        repo = audit_tool.get_repository(repository)
        
        # Get commits for the date
        click.echo(f"{Fore.BLUE}Getting commits for {target_date.strftime('%Y-%m-%d')}...{Style.RESET_ALL}")
        commits = audit_tool.get_commits_for_date(repo, target_date, author)
        
        if not commits:
            click.echo(f"{Fore.YELLOW}No commits found for {target_date.strftime('%Y-%m-%d')}{Style.RESET_ALL}")
            return
        
        click.echo(f"{Fore.GREEN}Found {len(commits)} commits{Style.RESET_ALL}")
        
        # Get diffs
        click.echo(f"{Fore.BLUE}Extracting diffs...{Style.RESET_ALL}")
        diffs = audit_tool.get_commit_diffs(commits)
        
        # Generate AI changelist with specified format
        click.echo(f"{Fore.BLUE}Generating AI changelist ({format} format)...{Style.RESET_ALL}")
        changelist_text = audit_tool.generate_changelist_with_ai(diffs, target_date, format)
        
        # Display result
        click.echo(f"\n{Fore.GREEN}{'='*60}")
        click.echo(f"CHANGELIST FOR {target_date.strftime('%Y-%m-%d')} ({format.upper()} FORMAT)")
        click.echo(f"{'='*60}{Style.RESET_ALL}\n")
        click.echo(changelist_text)
        
        # Save to file if requested
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(f"CHANGELIST FOR {target_date.strftime('%Y-%m-%d')} ({format.upper()} FORMAT)\n")
                f.write("="*60 + "\n\n")
                f.write(changelist_text)
            click.echo(f"\n{Fore.GREEN}Changelist saved to: {output}{Style.RESET_ALL}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

@cli.command()
@click.argument('repository')
@click.option('--date', '-d', help='Date to analyze (YYYY-MM-DD). Default: today')
@click.option('--author', '-a', help='Specific author to filter commits. Default: authenticated user')
def hours(repository, date, author):
    """Calculate work hours for a specific date."""
    
    # Validate environment
    validation_result = validate_environment()
    if not validation_result:
        sys.exit(1)
    
    _, github_token, openai_api_key = validation_result
    
    # Parse date
    if date:
        try:
            target_date = parser.parse(date)
        except ValueError:
            click.echo(f"{Fore.RED}Error: Invalid date format. Use YYYY-MM-DD{Style.RESET_ALL}")
            sys.exit(1)
    else:
        target_date = datetime.now()
    
    try:
        # Initialize the tool
        audit_tool = GitHubAuditTool(github_token, openai_api_key)
        
        # Get repository
        click.echo(f"{Fore.BLUE}Analyzing repository: {repository}{Style.RESET_ALL}")
        repo = audit_tool.get_repository(repository)
        
        # Get commits for the date
        click.echo(f"{Fore.BLUE}Getting commits for {target_date.strftime('%Y-%m-%d')}...{Style.RESET_ALL}")
        commits = audit_tool.get_commits_for_date(repo, target_date, author)
        
        if not commits:
            click.echo(f"{Fore.YELLOW}No commits found for {target_date.strftime('%Y-%m-%d')}{Style.RESET_ALL}")
            return
        
        # Calculate hours
        total_hours, first_commit, last_commit, work_blocks = audit_tool.calculate_work_hours(commits)
        
        # Display results
        click.echo(f"\n{Fore.GREEN}{'='*50}")
        click.echo(f"WORK HOURS FOR {target_date.strftime('%Y-%m-%d')}")
        click.echo(f"{'='*50}{Style.RESET_ALL}\n")
        
        click.echo(f"{Fore.CYAN}Total commits: {len(commits)}{Style.RESET_ALL}")
        click.echo(f"{Fore.CYAN}First commit: {first_commit.strftime('%H:%M:%S UTC')}{Style.RESET_ALL}")
        click.echo(f"{Fore.CYAN}Last commit:  {last_commit.strftime('%H:%M:%S UTC')}{Style.RESET_ALL}")
        
        # Show commit summary first (limit to last 20 commits for readability)
        click.echo(f"\n{Fore.BLUE}Commit Summary:{Style.RESET_ALL}")
        commits_to_show = commits[-20:]  # Show last 20 commits
        start_index = len(commits) - len(commits_to_show) + 1
        
        if len(commits) > 20:
            click.echo(f"  ... (showing last 20 of {len(commits)} commits)")
        
        for i, commit in enumerate(commits_to_show, start_index):
            timestamp = commit.commit.author.date.strftime('%H:%M')
            message = commit.commit.message.split('\n')[0][:60]
            click.echo(f"  {i:2d}. {timestamp} - {message}")
        
        # Show work blocks analysis
        click.echo(f"\n{Fore.BLUE}Work Blocks Analysis ({len(work_blocks)} blocks detected):{Style.RESET_ALL}")
        for i, block in enumerate(work_blocks, 1):
            start_time = block['start'].strftime('%H:%M')
            end_time = block['end'].strftime('%H:%M')
            hours = block['hours']
            commit_count = block['commits']
            
            if start_time == end_time:
                # Single commit block
                click.echo(f"  Block {i}: {start_time} (isolated commit - {hours:.1f} hours)")
            else:
                # Multi-commit block
                click.echo(f"  Block {i}: {start_time} - {end_time} ({hours:.1f} hours, {commit_count} commits)")
        
        # Show total hours at the end
        click.echo(f"\n{Fore.GREEN}📊 Total estimated hours worked: {total_hours:.1f} hours{Style.RESET_ALL}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

@cli.command()
def setup():
    """Setup GitHub and OpenAI API credentials."""
    click.echo(f"{Fore.BLUE}GitHub Auditing Tool Setup{Style.RESET_ALL}")
    click.echo("This will help you configure your API credentials.\n")
    
    # Check if .env file exists
    env_file = ".env"
    env_vars = {}
    
    if os.path.exists(env_file):
        click.echo(f"{Fore.YELLOW}Found existing .env file. Current values will be shown.{Style.RESET_ALL}\n")
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    # GitHub Token
    current_github = env_vars.get('GITHUB_TOKEN', '')
    if current_github:
        click.echo(f"Current GitHub token: {current_github[:8]}...")
    github_token = click.prompt('GitHub Personal Access Token', default=current_github, hide_input=True)
    
    # OpenAI API Key
    current_openai = env_vars.get('OPENAI_API_KEY', '')
    if current_openai:
        click.echo(f"Current OpenAI key: {current_openai[:8]}...")
    openai_key = click.prompt('OpenAI API Key', default=current_openai, hide_input=True)
    
    # Write to .env file
    with open(env_file, 'w') as f:
        f.write(f"# GitHub Auditing Tool Configuration\n")
        f.write(f"GITHUB_TOKEN={github_token}\n")
        f.write(f"OPENAI_API_KEY={openai_key}\n")
    
    click.echo(f"\n{Fore.GREEN}Configuration saved to .env file!{Style.RESET_ALL}")
    click.echo(f"{Fore.YELLOW}Make sure to add .env to your .gitignore file to keep your keys secure.{Style.RESET_ALL}")

if __name__ == '__main__':
    cli() 