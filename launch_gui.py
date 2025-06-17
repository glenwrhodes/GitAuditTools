#!/usr/bin/env python3
"""
GitHub Auditing Tool - GUI Launcher
Simple launcher script for the GUI frontend.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    required_modules = [
        'tkinter',
        'github',
        'openai',
        'colorama',
        'click',
        'python-dotenv',
        'python-dateutil',
        'pytz',
        'tiktoken'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'tkinter':
                import tkinter
            elif module == 'github':
                import github
            elif module == 'openai':
                import openai
            elif module == 'colorama':
                import colorama
            elif module == 'click':
                import click
            elif module == 'python-dotenv':
                import dotenv
            elif module == 'python-dateutil':
                import dateutil
            elif module == 'pytz':
                import pytz
            elif module == 'tiktoken':
                import tiktoken
        except ImportError:
            missing_modules.append(module)
    
    return missing_modules

def install_dependencies(missing_modules):
    """Install missing dependencies."""
    print("Installing missing dependencies...")
    for module in missing_modules:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', module])
            print(f"✓ Installed {module}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {module}")
            return False
    return True

def main():
    """Main launcher function."""
    print("GitHub Auditing Tool - GUI Launcher")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('github_audit_tool.py').exists():
        print("❌ Error: github_audit_tool.py not found in current directory")
        print("Please run this script from the same directory as the GitHub Auditing Tool")
        sys.exit(1)
    
    if not Path('github_audit_gui.py').exists():
        print("❌ Error: github_audit_gui.py not found in current directory")
        sys.exit(1)
    
    # Check dependencies
    print("Checking dependencies...")
    missing_modules = check_dependencies()
    
    if missing_modules:
        print(f"❌ Missing dependencies: {', '.join(missing_modules)}")
        response = input("Would you like to install them automatically? (y/N): ").lower()
        
        if response in ['y', 'yes']:
            if not install_dependencies(missing_modules):
                print("❌ Failed to install some dependencies. Please install them manually:")
                print(f"pip install {' '.join(missing_modules)}")
                sys.exit(1)
        else:
            print("Please install the missing dependencies manually:")
            print(f"pip install {' '.join(missing_modules)}")
            sys.exit(1)
    
    print("✓ All dependencies are available")
    
    # Check for .env file
    if not Path('.env').exists():
        print("⚠ Warning: .env file not found")
        print("You'll need to configure your API keys using the 'Setup API Keys' button in the GUI")
    
    # Launch GUI
    print("🚀 Launching GitHub Auditing Tool GUI...")
    try:
        import github_audit_gui
        github_audit_gui.main()
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        print("\nTrying alternative launch method...")
        try:
            subprocess.run([sys.executable, 'github_audit_gui.py'])
        except Exception as e2:
            print(f"❌ Alternative launch failed: {e2}")
            sys.exit(1)

if __name__ == '__main__':
    main() 