#!/usr/bin/env python3
"""
Example usage of the GitHub Audit Tool as a library
"""

import os
from datetime import datetime, timedelta
from github_audit_tool import GitHubAuditTool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Example of using the GitHub Audit Tool programmatically."""
    
    # Get API keys from environment
    github_token = os.getenv('GITHUB_TOKEN')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not github_token or not openai_api_key:
        print("Error: Please set GITHUB_TOKEN and OPENAI_API_KEY in your .env file")
        return
    
    # Initialize the audit tool
    audit_tool = GitHubAuditTool(github_token, openai_api_key)
    
    # Example repository (replace with your own)
    repo_name = "username/repository-name"
    
    try:
        # Get repository
        repo = audit_tool.get_repository(repo_name)
        print(f"✅ Successfully connected to repository: {repo.full_name}")
        
        # Get commits for yesterday
        yesterday = datetime.now() - timedelta(days=1)
        commits = audit_tool.get_commits_for_date(repo, yesterday)
        
        print(f"📊 Found {len(commits)} commits for {yesterday.strftime('%Y-%m-%d')}")
        
        if commits:
            # Calculate work hours
            total_hours, first_commit, last_commit, work_blocks = audit_tool.calculate_work_hours(commits)
            print(f"⏰ Estimated work hours: {total_hours:.1f}")
            print(f"🕘 Work period: {first_commit.strftime('%H:%M')} - {last_commit.strftime('%H:%M')}")
            
            # Show work blocks
            print(f"📊 Work blocks:")
            for block in work_blocks:
                print(f"  {block['start'].strftime('%H:%M')} - {block['end'].strftime('%H:%M')} ({block['hours']:.1f} hours, {block['commits']} commits)")
            
            # Generate changelist
            print("🤖 Generating AI changelist...")
            diffs = audit_tool.get_commit_diffs(commits)
            changelist = audit_tool.generate_changelist_with_ai(diffs, yesterday)
            
            # Save to file
            filename = f"changelist_{yesterday.strftime('%Y-%m-%d')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"CHANGELIST FOR {yesterday.strftime('%Y-%m-%d')}\n")
                f.write("="*60 + "\n\n")
                f.write(changelist)
            
            print(f"💾 Changelist saved to: {filename}")
            
        else:
            print("❌ No commits found for the specified date")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 