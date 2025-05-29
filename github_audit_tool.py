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
import tiktoken
from collections import defaultdict

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
            # Initialize token encoder for token counting
            self.token_encoder = tiktoken.encoding_for_model("gpt-4o")
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
    
    def parse_date_range(self, date_input: str) -> Tuple[datetime, datetime]:
        """Parse date input which can be a single date or date range."""
        if not date_input:
            # Default to today
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.UTC)
            return today, today + timedelta(days=1)
        
        # Check for date range (e.g., "2023-12-01..2023-12-07" or "2023-12-01:2023-12-07")
        if '..' in date_input or ':' in date_input:
            separator = '..' if '..' in date_input else ':'
            start_str, end_str = date_input.split(separator, 1)
            start_date = parser.parse(start_str.strip())
            end_date = parser.parse(end_str.strip())
        else:
            # Single date - check for special keywords
            date_input = date_input.lower().strip()
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            if date_input in ['today']:
                start_date = today
                end_date = today
            elif date_input in ['yesterday']:
                start_date = today - timedelta(days=1)
                end_date = start_date
            elif date_input in ['week', 'this-week']:
                # Current week (Monday to Sunday)
                days_since_monday = today.weekday()
                start_date = today - timedelta(days=days_since_monday)
                end_date = start_date + timedelta(days=6)
            elif date_input in ['last-week']:
                days_since_monday = today.weekday()
                this_monday = today - timedelta(days=days_since_monday)
                start_date = this_monday - timedelta(days=7)
                end_date = start_date + timedelta(days=6)
            elif date_input in ['month', 'this-month']:
                start_date = today.replace(day=1)
                if today.month == 12:
                    end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            elif date_input in ['last-month']:
                if today.month == 1:
                    start_date = today.replace(year=today.year - 1, month=12, day=1)
                    end_date = today.replace(day=1) - timedelta(days=1)
                else:
                    start_date = today.replace(month=today.month - 1, day=1)
                    end_date = today.replace(day=1) - timedelta(days=1)
            else:
                # Regular date parsing
                start_date = parser.parse(date_input)
                end_date = start_date
        
        # Ensure timezone awareness
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=pytz.UTC)
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=pytz.UTC)
        
        # Set to start and end of days
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return start_date, end_date
    
    def get_commits_for_date_range(self, repo, start_date: datetime, end_date: datetime, author: Optional[str] = None) -> List:
        """Get all commits for a date range."""
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
    
    def get_commits_for_date(self, repo, target_date: datetime, author: Optional[str] = None) -> List:
        """Get all commits for a specific date (legacy method for backwards compatibility)."""
        # Set timezone to UTC if not specified
        if target_date.tzinfo is None:
            target_date = target_date.replace(tzinfo=pytz.UTC)
        
        # Define the date range (start and end of the day)
        start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        return self.get_commits_for_date_range(repo, start_date, end_date, author)
    
    def analyze_coding_rhythm(self, commits: List) -> Dict:
        """Analyze coding patterns throughout the day and week."""
        if not commits:
            return {}
        
        # Initialize data structures
        hourly_commits = defaultdict(int)
        daily_commits = defaultdict(int)
        hourly_hours = defaultdict(float)
        daily_hours = defaultdict(float)
        
        # Group commits by date for daily analysis
        commits_by_date = defaultdict(list)
        for commit in commits:
            commit_date = commit.commit.author.date.date()
            commits_by_date[commit_date].append(commit)
        
        # Analyze each day
        for date, day_commits in commits_by_date.items():
            # Calculate hours for this day
            day_hours, _, _, _ = self.calculate_work_hours(day_commits)
            day_name = date.strftime('%A')
            daily_commits[day_name] += len(day_commits)
            daily_hours[day_name] += day_hours
            
            # Analyze hourly patterns
            for commit in day_commits:
                hour = commit.commit.author.date.hour
                hourly_commits[hour] += 1
                # Distribute daily hours proportionally across commit hours
                hourly_hours[hour] += day_hours / len(day_commits)
        
        # Calculate productivity metrics
        total_commits = len(commits)
        total_days = len(commits_by_date)
        avg_commits_per_day = total_commits / total_days if total_days > 0 else 0
        
        # Find peak hours and days
        peak_hour = max(hourly_commits.items(), key=lambda x: x[1]) if hourly_commits else (0, 0)
        peak_day = max(daily_commits.items(), key=lambda x: x[1]) if daily_commits else ("Unknown", 0)
        
        # Calculate work span (earliest to latest commit hour)
        if hourly_commits:
            work_hours = [h for h in hourly_commits.keys() if hourly_commits[h] > 0]
            earliest_hour = min(work_hours)
            latest_hour = max(work_hours)
            work_span = latest_hour - earliest_hour + 1
        else:
            earliest_hour = latest_hour = work_span = 0
        
        return {
            'total_commits': total_commits,
            'total_days': total_days,
            'avg_commits_per_day': avg_commits_per_day,
            'hourly_commits': dict(hourly_commits),
            'daily_commits': dict(daily_commits),
            'hourly_hours': dict(hourly_hours),
            'daily_hours': dict(daily_hours),
            'peak_hour': peak_hour,
            'peak_day': peak_day,
            'earliest_hour': earliest_hour,
            'latest_hour': latest_hour,
            'work_span_hours': work_span,
            'date_range': (min(commits_by_date.keys()), max(commits_by_date.keys())) if commits_by_date else None
        }

    def calculate_work_hours(self, commits: List) -> Tuple[float, datetime, datetime, List]:
        """Calculate work hours based on commit patterns, detecting work blocks and gaps."""
        if not commits:
            return 0.0, None, None, []
        
        # Sort commits by date
        sorted_commits = sorted(commits, key=lambda c: c.commit.author.date)
        
        if len(sorted_commits) == 1:
            # Single commit: assume 30 min prep work + 10 min for the commit (40 min total)
            commit_time = sorted_commits[0].commit.author.date
            return 0.67, commit_time, commit_time, [{'start': commit_time, 'end': commit_time, 'hours': 0.67, 'commits': 1}]
        
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
        """Calculate hours for a single work block.
        
        Assumes 30 minutes of work before the first commit, since you likely 
        started working before making your first commit.
        """
        if start_time == end_time:
            # Single commit: assume 30 min prep work + 10 min for the commit
            return 0.67  # 40 minutes total (0.5 + 0.17)
        
        # Calculate actual time span between commits
        time_diff = end_time - start_time
        span_hours = time_diff.total_seconds() / 3600
        
        # Add 30 minutes before first commit + 10 minutes after last commit
        # This accounts for work done before the first commit and cleanup after the last
        buffered_hours = 0.5 + span_hours + 0.17  # 30 min + span + 10 min
        
        # Minimum time per commit is 10 minutes, plus the 30-minute pre-work
        min_hours = (commit_count * 0.17) + 0.5
        
        # Return the larger of the two estimates
        return max(buffered_hours, min_hours)
    
    def _decimal_hours_to_hhmm(self, decimal_hours: float) -> str:
        """Convert decimal hours to HH:MM format."""
        total_minutes = int(decimal_hours * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"
    
    def _format_hours_display(self, decimal_hours: float) -> str:
        """Format hours for display showing both decimal and HH:MM format."""
        hhmm = self._decimal_hours_to_hhmm(decimal_hours)
        return f"{decimal_hours:.1f} hours ({hhmm})"
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using the OpenAI tokenizer."""
        try:
            return len(self.token_encoder.encode(text))
        except Exception:
            # Fallback to rough estimation (4 chars per token)
            return len(text) // 4
    
    def get_commit_messages_only(self, commits: List) -> str:
        """Get commit messages only (lightweight version)."""
        commit_data = []
        
        for commit in commits:
            commit_info = {
                'sha': commit.sha[:8],
                'message': commit.commit.message,
                'timestamp': commit.commit.author.date.isoformat(),
                'files_changed': len(commit.files) if hasattr(commit, 'files') else 0
            }
            commit_data.append(commit_info)
        
        return json.dumps(commit_data, indent=2)

    def get_commit_diffs(self, commits: List, max_tokens: int = 100000) -> Tuple[str, bool]:
        """Get diffs for all commits, with token limit checking."""
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
        
        diff_json = json.dumps(all_diffs, indent=2)
        token_count = self.count_tokens(diff_json)
        
        # Return the data and whether it exceeds token limit
        return diff_json, token_count <= max_tokens
    
    def generate_changelist_with_ai(self, data: str, date_range: Tuple[datetime, datetime], output_format: str = 'text', is_full_diff: bool = True) -> str:
        """Generate a professional changelist using OpenAI."""
        
        start_date, end_date = date_range
        if start_date.date() == end_date.date():
            date_str = start_date.strftime('%Y-%m-%d')
        else:
            date_str = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        data_type = "detailed Git commit data with diffs" if is_full_diff else "Git commit messages and metadata"
        
        # Base prompt for the changelist
        base_prompt = f"""
You are a professional software developer writing an end-of-day work report for a client.

Based on the following {data_type} from {date_str}, please generate a clear, professional changelist that summarizes the work completed. 

Format the response as a client-friendly report with:
1. A brief summary of the work period
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
{data}

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
            return f"Error generating AI changelist: {e}\n\nRaw commit data:\n{data}"

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
@click.option('--date', '-d', help='Date/range to analyze (YYYY-MM-DD, YYYY-MM-DD..YYYY-MM-DD, or keywords: today, yesterday, week, month, etc.). Default: today')
@click.option('--author', '-a', help='Specific author to filter commits. Default: authenticated user')
@click.option('--output', '-o', help='Output file to save the changelist')
@click.option('--format', '-f', type=click.Choice(['text', 'markdown'], case_sensitive=False), 
              default='text', help='Output format: text (plain text) or markdown. Default: text')
@click.option('--verbose', '-v', is_flag=True, help='Include full diffs (may use more tokens). Default: commit messages only')
def changelist(repository, date, author, output, format, verbose):
    """Generate an AI-powered changelist for a specific date or date range."""
    
    # Validate environment
    validation_result = validate_environment()
    if not validation_result:
        sys.exit(1)
    
    _, github_token, openai_api_key = validation_result
    
    try:
        # Initialize the tool
        audit_tool = GitHubAuditTool(github_token, openai_api_key)
        
        # Parse date range
        start_date, end_date = audit_tool.parse_date_range(date)
        
        # Format date range for display
        if start_date.date() == end_date.date():
            date_display = start_date.strftime('%Y-%m-%d')
        else:
            date_display = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        # Get repository
        click.echo(f"{Fore.BLUE}Analyzing repository: {repository}{Style.RESET_ALL}")
        repo = audit_tool.get_repository(repository)
        
        # Get commits for the date range
        click.echo(f"{Fore.BLUE}Getting commits for {date_display}...{Style.RESET_ALL}")
        commits = audit_tool.get_commits_for_date_range(repo, start_date, end_date, author)
        
        if not commits:
            click.echo(f"{Fore.YELLOW}No commits found for {date_display}{Style.RESET_ALL}")
            return
        
        click.echo(f"{Fore.GREEN}Found {len(commits)} commits{Style.RESET_ALL}")
        
        # Get commit data based on verbose flag
        if verbose:
            click.echo(f"{Fore.BLUE}Extracting full diffs...{Style.RESET_ALL}")
            diffs, within_limit = audit_tool.get_commit_diffs(commits)
            
            if not within_limit:
                click.echo(f"{Fore.YELLOW}Warning: Full diffs exceed token limit (>100k tokens). Falling back to commit messages only.{Style.RESET_ALL}")
                commit_data = audit_tool.get_commit_messages_only(commits)
                is_full_diff = False
            else:
                commit_data = diffs
                is_full_diff = True
        else:
            click.echo(f"{Fore.BLUE}Extracting commit messages...{Style.RESET_ALL}")
            commit_data = audit_tool.get_commit_messages_only(commits)
            is_full_diff = False
        
        # Check token count
        token_count = audit_tool.count_tokens(commit_data)
        if token_count > 128000:  # 128k token limit
            click.echo(f"{Fore.RED}Error: Commit data ({token_count:,} tokens) exceeds maximum limit (128k tokens).{Style.RESET_ALL}")
            click.echo(f"{Fore.YELLOW}Try using a smaller date range or fewer commits.{Style.RESET_ALL}")
            return
        
        click.echo(f"{Fore.BLUE}Using {token_count:,} tokens ({('full diffs' if is_full_diff else 'commit messages only')})...{Style.RESET_ALL}")
        
        # Generate AI changelist with specified format
        click.echo(f"{Fore.BLUE}Generating AI changelist ({format} format)...{Style.RESET_ALL}")
        changelist_text = audit_tool.generate_changelist_with_ai(commit_data, (start_date, end_date), format, is_full_diff)
        
        # Display result
        click.echo(f"\n{Fore.GREEN}{'='*60}")
        click.echo(f"CHANGELIST FOR {date_display.upper()} ({format.upper()} FORMAT)")
        click.echo(f"{'='*60}{Style.RESET_ALL}\n")
        click.echo(changelist_text)
        
        # Save to file if requested
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(f"CHANGELIST FOR {date_display.upper()} ({format.upper()} FORMAT)\n")
                f.write("="*60 + "\n\n")
                f.write(changelist_text)
            click.echo(f"\n{Fore.GREEN}Changelist saved to: {output}{Style.RESET_ALL}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

@cli.command()
@click.argument('repository')
@click.option('--date', '-d', help='Date/range to analyze (YYYY-MM-DD, YYYY-MM-DD..YYYY-MM-DD, or keywords: today, yesterday, week, month, etc.). Default: today')
@click.option('--author', '-a', help='Specific author to filter commits. Default: authenticated user')
def hours(repository, date, author):
    """Calculate work hours for a specific date or date range."""
    
    # Validate environment
    validation_result = validate_environment()
    if not validation_result:
        sys.exit(1)
    
    _, github_token, openai_api_key = validation_result
    
    try:
        # Initialize the tool
        audit_tool = GitHubAuditTool(github_token, openai_api_key)
        
        # Parse date range
        start_date, end_date = audit_tool.parse_date_range(date)
        
        # Format date range for display
        if start_date.date() == end_date.date():
            date_display = start_date.strftime('%Y-%m-%d')
        else:
            date_display = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        # Get repository
        click.echo(f"{Fore.BLUE}Analyzing repository: {repository}{Style.RESET_ALL}")
        repo = audit_tool.get_repository(repository)
        
        # Get commits for the date range
        click.echo(f"{Fore.BLUE}Getting commits for {date_display}...{Style.RESET_ALL}")
        commits = audit_tool.get_commits_for_date_range(repo, start_date, end_date, author)
        
        if not commits:
            click.echo(f"{Fore.YELLOW}No commits found for {date_display}{Style.RESET_ALL}")
            return
        
        # Calculate hours for entire range
        total_hours, first_commit, last_commit, work_blocks = audit_tool.calculate_work_hours(commits)
        
        # For multi-day ranges, also break down by day
        if start_date.date() != end_date.date():
            # Group commits by day
            commits_by_day = defaultdict(list)
            for commit in commits:
                day = commit.commit.author.date.date()
                commits_by_day[day].append(commit)
            
            # Display results
            click.echo(f"\n{Fore.GREEN}{'='*60}")
            click.echo(f"WORK HOURS FOR {date_display.upper()}")
            click.echo(f"{'='*60}{Style.RESET_ALL}\n")
            
            click.echo(f"{Fore.CYAN}Total commits: {len(commits)}{Style.RESET_ALL}")
            click.echo(f"{Fore.CYAN}Date range: {first_commit.strftime('%Y-%m-%d %H:%M UTC')} - {last_commit.strftime('%Y-%m-%d %H:%M UTC')}{Style.RESET_ALL}")
            
            # Daily breakdown
            click.echo(f"\n{Fore.BLUE}Daily Breakdown:{Style.RESET_ALL}")
            daily_total = 0
            for day in sorted(commits_by_day.keys()):
                day_commits = commits_by_day[day]
                day_hours, _, _, _ = audit_tool.calculate_work_hours(day_commits)
                daily_total += day_hours
                day_name = day.strftime('%A')
                hours_display = audit_tool._format_hours_display(day_hours)
                click.echo(f"  {day.strftime('%Y-%m-%d')} ({day_name}): {hours_display} ({len(day_commits)} commits)")
            
            total_hours_display = audit_tool._format_hours_display(daily_total)
            click.echo(f"\n{Fore.GREEN}📊 Total estimated hours worked: {total_hours_display}{Style.RESET_ALL}")
            
        else:
            # Single day analysis (existing logic)
            click.echo(f"\n{Fore.GREEN}{'='*50}")
            click.echo(f"WORK HOURS FOR {date_display.upper()}")
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
                hours_display = audit_tool._format_hours_display(hours)
                
                if start_time == end_time:
                    # Single commit block
                    click.echo(f"  Block {i}: {start_time} (isolated commit - {hours_display})")
                else:
                    # Multi-commit block
                    click.echo(f"  Block {i}: {start_time} - {end_time} ({hours_display}, {commit_count} commits)")
            
            total_hours_display = audit_tool._format_hours_display(total_hours)
            click.echo(f"\n{Fore.GREEN}📊 Total estimated hours worked: {total_hours_display}{Style.RESET_ALL}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

@cli.command()
@click.argument('repository')
@click.option('--date', '-d', help='Date/range to analyze (YYYY-MM-DD, YYYY-MM-DD..YYYY-MM-DD, or keywords: today, yesterday, week, month, etc.). Default: this week')
@click.option('--author', '-a', help='Specific author to filter commits. Default: authenticated user')
def rhythm(repository, date, author):
    """Analyze coding rhythm and patterns for a date range."""
    
    # Validate environment
    validation_result = validate_environment()
    if not validation_result:
        sys.exit(1)
    
    _, github_token, openai_api_key = validation_result
    
    # Default to current week if no date specified
    if not date:
        date = 'this-week'
    
    try:
        # Initialize the tool
        audit_tool = GitHubAuditTool(github_token, openai_api_key)
        
        # Parse date range
        start_date, end_date = audit_tool.parse_date_range(date)
        
        # Format date range for display
        if start_date.date() == end_date.date():
            date_display = start_date.strftime('%Y-%m-%d')
        else:
            date_display = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        # Get repository
        click.echo(f"{Fore.BLUE}Analyzing repository: {repository}{Style.RESET_ALL}")
        repo = audit_tool.get_repository(repository)
        
        # Get commits for the date range
        click.echo(f"{Fore.BLUE}Getting commits for {date_display}...{Style.RESET_ALL}")
        commits = audit_tool.get_commits_for_date_range(repo, start_date, end_date, author)
        
        if not commits:
            click.echo(f"{Fore.YELLOW}No commits found for {date_display}{Style.RESET_ALL}")
            return
        
        # Analyze coding rhythm
        click.echo(f"{Fore.BLUE}Analyzing coding patterns...{Style.RESET_ALL}")
        rhythm_data = audit_tool.analyze_coding_rhythm(commits)
        
        # Display results
        click.echo(f"\n{Fore.GREEN}{'='*60}")
        click.echo(f"CODING RHYTHM ANALYSIS FOR {date_display.upper()}")
        click.echo(f"{'='*60}{Style.RESET_ALL}\n")
        
        # Summary stats
        click.echo(f"{Fore.CYAN}📊 Summary:{Style.RESET_ALL}")
        click.echo(f"  Total commits: {rhythm_data['total_commits']}")
        click.echo(f"  Active days: {rhythm_data['total_days']}")
        click.echo(f"  Avg commits/day: {rhythm_data['avg_commits_per_day']:.1f}")
        
        if rhythm_data['date_range']:
            start_date_analysis, end_date_analysis = rhythm_data['date_range']
            click.echo(f"  Analysis period: {start_date_analysis} to {end_date_analysis}")
        
        # Peak times
        peak_hour, peak_commits = rhythm_data['peak_hour']
        peak_day, peak_day_commits = rhythm_data['peak_day']
        click.echo(f"\n{Fore.CYAN}🚀 Peak Activity:{Style.RESET_ALL}")
        click.echo(f"  Most productive hour: {peak_hour:02d}:00 ({peak_commits} commits)")
        click.echo(f"  Most productive day: {peak_day} ({peak_day_commits} commits)")
        click.echo(f"  Work span: {rhythm_data['earliest_hour']:02d}:00 - {rhythm_data['latest_hour']:02d}:00 ({rhythm_data['work_span_hours']} hours)")
        
        # Hourly breakdown
        click.echo(f"\n{Fore.BLUE}⏰ Hourly Commit Pattern:{Style.RESET_ALL}")
        hourly_commits = rhythm_data['hourly_commits']
        max_hourly = max(hourly_commits.values()) if hourly_commits else 1
        
        for hour in range(24):
            count = hourly_commits.get(hour, 0)
            if count > 0:
                # Create a simple bar chart
                bar_length = int((count / max_hourly) * 20)
                bar = '█' * bar_length
                click.echo(f"  {hour:02d}:00 │{bar:<20}│ {count} commits")
        
        # Daily breakdown
        click.echo(f"\n{Fore.BLUE}📅 Weekly Commit Pattern:{Style.RESET_ALL}")
        daily_commits = rhythm_data['daily_commits']
        daily_hours = rhythm_data['daily_hours']
        
        # Ordered days of week
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        max_daily = max(daily_commits.values()) if daily_commits else 1
        
        for day in days_order:
            commits_count = daily_commits.get(day, 0)
            hours_count = daily_hours.get(day, 0)
            if commits_count > 0:
                bar_length = int((commits_count / max_daily) * 15)
                bar = '█' * bar_length
                hours_display = audit_tool._format_hours_display(hours_count)
                click.echo(f"  {day:<9} │{bar:<15}│ {commits_count} commits ({hours_display})")
            else:
                click.echo(f"  {day:<9} │{'':<15}│ 0 commits")
        
        # Productivity insights
        click.echo(f"\n{Fore.YELLOW}💡 Insights:{Style.RESET_ALL}")
        
        # Find most productive time blocks
        if hourly_commits:
            productive_hours = [h for h, c in hourly_commits.items() if c >= max_hourly * 0.7]
            if productive_hours:
                if len(productive_hours) == 1:
                    click.echo(f"  • You're most focused around {productive_hours[0]:02d}:00")
                else:
                    start_hour = min(productive_hours)
                    end_hour = max(productive_hours)
                    click.echo(f"  • Your peak productivity window is {start_hour:02d}:00-{end_hour:02d}:00")
        
        # Analyze work pattern
        if rhythm_data['work_span_hours'] <= 4:
            click.echo(f"  • You have a focused work pattern (4-hour span)")
        elif rhythm_data['work_span_hours'] <= 8:
            click.echo(f"  • You maintain steady productivity throughout the day")
        else:
            click.echo(f"  • You code across long hours - consider work-life balance")
        
        # Weekly pattern insights
        weekday_commits = sum(daily_commits.get(day, 0) for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
        weekend_commits = sum(daily_commits.get(day, 0) for day in ['Saturday', 'Sunday'])
        
        if weekend_commits > weekday_commits * 0.3:
            click.echo(f"  • High weekend activity detected - {weekend_commits} weekend commits")
        
        if daily_commits.get('Monday', 0) > max_daily * 0.8:
            click.echo(f"  • Strong Monday momentum - you start weeks well!")
        
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