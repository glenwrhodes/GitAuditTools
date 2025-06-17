#!/usr/bin/env python3
"""
GitHub Auditing Tool - GUI Frontend
A modern graphical interface for the GitHub Auditing Tool.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import sys
import os
from datetime import datetime
import subprocess
import json
from pathlib import Path

# Import the main audit tool class
from github_audit_tool import GitHubAuditTool, validate_environment

class GitHubAuditGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Auditing Tool")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configure style
        self.setup_styles()
        
        # Variables
        self.setup_variables()
        
        # Create GUI
        self.create_widgets()
        
        # Check environment on startup
        self.check_environment()
    
    def setup_styles(self):
        """Setup modern styling for the GUI."""
        style = ttk.Style()
        
        # Configure colors and fonts
        self.colors = {
            'primary': '#2196F3',
            'secondary': '#1976D2',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#F44336',
            'bg': '#FAFAFA',
            'surface': '#FFFFFF',
            'text': '#212121',
            'text_secondary': '#757575'
        }
        
        # Configure ttk styles
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Action.TButton', font=('Segoe UI', 11, 'bold'))
        
    def setup_variables(self):
        """Setup tkinter variables."""
        # Input variables
        self.repository_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.min_commit_var = tk.StringVar()
        self.max_commit_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.voice_var = tk.StringVar()
        
        # Option variables
        self.format_var = tk.StringVar(value='markdown')
        self.verbose_var = tk.BooleanVar()
        self.display_only_var = tk.BooleanVar()
        self.save_var = tk.BooleanVar()
        
        # Status variables
        self.is_running = tk.BooleanVar()
        self.status_var = tk.StringVar(value="Ready")
    
    def create_widgets(self):
        """Create the main GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="GitHub Auditing Tool", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input section
        self.create_input_section(main_frame)
        
        # Options section
        self.create_options_section(main_frame)
        
        # Action buttons
        self.create_action_buttons(main_frame)
        
        # Output section
        self.create_output_section(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_input_section(self, parent):
        """Create the input fields section."""
        # Input frame
        input_frame = ttk.LabelFrame(parent, text="Repository & Date Settings", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Repository
        ttk.Label(input_frame, text="Repository:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        repo_entry = ttk.Entry(input_frame, textvariable=self.repository_var, font=('Segoe UI', 10))
        repo_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        # Date range
        ttk.Label(input_frame, text="Date Range:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        date_frame = ttk.Frame(input_frame)
        date_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        date_frame.columnconfigure(0, weight=1)
        
        date_entry = ttk.Entry(date_frame, textvariable=self.date_var, font=('Segoe UI', 10))
        date_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Date presets
        date_presets = ['today', 'yesterday', 'week', 'last-week', 'month', 'last-month', 'all']
        date_combo = ttk.Combobox(date_frame, values=date_presets, width=12, state='readonly')
        date_combo.grid(row=0, column=1)
        date_combo.bind('<<ComboboxSelected>>', lambda e: self.date_var.set(date_combo.get()))
        
        # Author
        ttk.Label(input_frame, text="Author:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        author_entry = ttk.Entry(input_frame, textvariable=self.author_var, font=('Segoe UI', 10))
        author_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        # Commit range
        ttk.Label(input_frame, text="Min Commit SHA:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        min_commit_entry = ttk.Entry(input_frame, textvariable=self.min_commit_var, font=('Segoe UI', 10))
        min_commit_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        ttk.Label(input_frame, text="Max Commit SHA:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        max_commit_entry = ttk.Entry(input_frame, textvariable=self.max_commit_var, font=('Segoe UI', 10))
        max_commit_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        # Output file
        ttk.Label(input_frame, text="Output File:").grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        output_frame = ttk.Frame(input_frame)
        output_frame.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        output_frame.columnconfigure(0, weight=1)
        
        output_entry = ttk.Entry(output_frame, textvariable=self.output_var, font=('Segoe UI', 10))
        output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(output_frame, text="Browse", command=self.browse_output_file)
        browse_btn.grid(row=0, column=1)
        
        # Voice/tone
        ttk.Label(input_frame, text="Voice/Tone:").grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        voice_entry = ttk.Entry(input_frame, textvariable=self.voice_var, font=('Segoe UI', 10))
        voice_entry.grid(row=6, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
    
    def create_options_section(self, parent):
        """Create the options section."""
        options_frame = ttk.LabelFrame(parent, text="Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Format selection
        format_frame = ttk.Frame(options_frame)
        format_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(format_frame, text="Format:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        format_markdown = ttk.Radiobutton(format_frame, text="Markdown", variable=self.format_var, value='markdown')
        format_markdown.grid(row=0, column=1, padx=(0, 10))
        
        format_text = ttk.Radiobutton(format_frame, text="Text", variable=self.format_var, value='text')
        format_text.grid(row=0, column=2, padx=(0, 10))
        
        # Checkboxes
        checkbox_frame = ttk.Frame(options_frame)
        checkbox_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        verbose_cb = ttk.Checkbutton(checkbox_frame, text="Verbose (include full diffs)", variable=self.verbose_var)
        verbose_cb.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        display_only_cb = ttk.Checkbutton(checkbox_frame, text="Display only (don't save)", variable=self.display_only_var)
        display_only_cb.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        save_cb = ttk.Checkbutton(checkbox_frame, text="Auto-save with smart filename", variable=self.save_var)
        save_cb.grid(row=0, column=2, sticky=tk.W)
    
    def create_action_buttons(self, parent):
        """Create the action buttons section."""
        action_frame = ttk.LabelFrame(parent, text="Actions", padding="10")
        action_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # First row of buttons
        button_frame1 = ttk.Frame(action_frame)
        button_frame1.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Main action buttons
        changelist_btn = ttk.Button(button_frame1, text="Generate Changelist", 
                                  command=lambda: self.run_command('changelist'),
                                  style='Action.TButton', width=20)
        changelist_btn.grid(row=0, column=0, padx=(0, 10))
        
        timeline_btn = ttk.Button(button_frame1, text="Generate Timeline", 
                                command=lambda: self.run_command('timeline'),
                                style='Action.TButton', width=20)
        timeline_btn.grid(row=0, column=1, padx=(0, 10))
        
        stats_btn = ttk.Button(button_frame1, text="Generate Statistics", 
                             command=lambda: self.run_command('stats'),
                             style='Action.TButton', width=20)
        stats_btn.grid(row=0, column=2, padx=(0, 10))
        
        # Second row of buttons
        button_frame2 = ttk.Frame(action_frame)
        button_frame2.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        hours_btn = ttk.Button(button_frame2, text="Calculate Hours", 
                             command=lambda: self.run_command('hours'),
                             style='Action.TButton', width=20)
        hours_btn.grid(row=0, column=0, padx=(0, 10))
        
        rhythm_btn = ttk.Button(button_frame2, text="Analyze Rhythm", 
                              command=lambda: self.run_command('rhythm'),
                              style='Action.TButton', width=20)
        rhythm_btn.grid(row=0, column=1, padx=(0, 10))
        
        info_btn = ttk.Button(button_frame2, text="Show Commit Info", 
                            command=lambda: self.run_command('info'),
                            style='Action.TButton', width=20)
        info_btn.grid(row=0, column=2, padx=(0, 10))
        
        setup_btn = ttk.Button(button_frame2, text="Setup API Keys", 
                             command=lambda: self.run_command('setup'),
                             style='Primary.TButton', width=20)
        setup_btn.grid(row=0, column=3, padx=(10, 0))
        
        # Store button references for enabling/disabling
        self.action_buttons = [changelist_btn, timeline_btn, stats_btn, hours_btn, rhythm_btn, info_btn, setup_btn]
    
    def create_output_section(self, parent):
        """Create the output section."""
        output_frame = ttk.LabelFrame(parent, text="Output", padding="10")
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # Output text area with scrollbar
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, 
                                                   font=('Consolas', 10), 
                                                   height=15)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear button
        clear_btn = ttk.Button(output_frame, text="Clear Output", command=self.clear_output)
        clear_btn.grid(row=1, column=0, sticky=tk.E, pady=(10, 0))
    
    def create_status_bar(self, parent):
        """Create the status bar."""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        # Status label
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))
    
    def browse_output_file(self):
        """Browse for output file."""
        filename = filedialog.asksaveasfilename(
            title="Save Output As",
            defaultextension=".md" if self.format_var.get() == 'markdown' else ".txt",
            filetypes=[
                ("Markdown files", "*.md"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.output_var.set(filename)
    
    def check_environment(self):
        """Check if environment variables are set."""
        try:
            validation_result = validate_environment()
            if validation_result:
                self.status_var.set("Environment OK - API keys configured")
                self.log_output("✓ API keys are configured and ready to use.\n")
            else:
                self.status_var.set("Environment Error - API keys missing")
                self.log_output("⚠ Missing API keys. Please use 'Setup API Keys' to configure.\n")
        except Exception as e:
            self.status_var.set(f"Environment Error: {str(e)}")
            self.log_output(f"❌ Environment check failed: {str(e)}\n")
    
    def validate_inputs(self, command):
        """Validate inputs before running command."""
        if not self.repository_var.get().strip():
            messagebox.showerror("Input Error", "Repository name is required!")
            return False
        
        if command == 'setup':
            return True  # Setup doesn't need other inputs
        
        # Check for conflicting options
        if self.display_only_var.get() and self.output_var.get().strip():
            messagebox.showwarning("Option Conflict", 
                                 "Display-only mode is selected but output file is specified. "
                                 "Display-only will take precedence.")
        
        if self.display_only_var.get() and self.save_var.get():
            messagebox.showwarning("Option Conflict", 
                                 "Display-only mode is selected but auto-save is enabled. "
                                 "Display-only will take precedence.")
        
        return True
    
    def build_command(self, action):
        """Build the command line arguments."""
        cmd = [sys.executable, 'github_audit_tool.py', action]
        
        # Add repository
        if action != 'setup':
            cmd.append(self.repository_var.get().strip())
        
        # Add options
        if self.date_var.get().strip():
            cmd.extend(['--date', self.date_var.get().strip()])
        
        if self.author_var.get().strip():
            cmd.extend(['--author', self.author_var.get().strip()])
        
        if self.min_commit_var.get().strip():
            cmd.extend(['--min-commit', self.min_commit_var.get().strip()])
        
        if self.max_commit_var.get().strip():
            cmd.extend(['--max-commit', self.max_commit_var.get().strip()])
        
        if self.output_var.get().strip() and not self.display_only_var.get():
            cmd.extend(['--output', self.output_var.get().strip()])
        
        if self.voice_var.get().strip() and action in ['changelist', 'timeline']:
            cmd.extend(['--voice', self.voice_var.get().strip()])
        
        # Format
        cmd.extend(['--format', self.format_var.get()])
        
        # Boolean flags
        if self.verbose_var.get() and action in ['changelist', 'timeline']:
            cmd.append('--verbose')
        
        if self.display_only_var.get() and action in ['changelist', 'timeline']:
            cmd.append('--display-only')
        
        if self.save_var.get() and action in ['hours', 'rhythm', 'stats']:
            cmd.append('--save')
        
        return cmd
    
    def run_command(self, action):
        """Run the specified command in a separate thread."""
        if not self.validate_inputs(action):
            return
        
        if self.is_running.get():
            messagebox.showwarning("Operation in Progress", "Another operation is currently running. Please wait.")
            return
        
        # Build command
        cmd = self.build_command(action)
        
        # Update UI
        self.is_running.set(True)
        self.set_buttons_state(False)
        self.progress_bar.start()
        self.status_var.set(f"Running {action}...")
        
        # Log command
        self.log_output(f"\n{'='*60}\n")
        self.log_output(f"Running: {action.upper()}\n")
        self.log_output(f"Command: {' '.join(cmd)}\n")
        self.log_output(f"{'='*60}\n")
        
        # Run in thread
        thread = threading.Thread(target=self.execute_command, args=(cmd, action), daemon=True)
        thread.start()
    
    def execute_command(self, cmd, action):
        """Execute the command and handle output."""
        try:
            # Run the command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
                bufsize=1
            )
            
            # Read output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.root.after(0, self.log_output, output)
            
            # Get any remaining output
            stdout, stderr = process.communicate()
            
            # Log any remaining output
            if stdout:
                self.root.after(0, self.log_output, stdout)
            if stderr:
                self.root.after(0, self.log_output, f"Error: {stderr}")
            
            # Check return code
            if process.returncode == 0:
                self.root.after(0, self.log_output, f"\n✓ {action} completed successfully!\n")
                self.root.after(0, lambda: self.status_var.set(f"{action} completed successfully"))
            else:
                self.root.after(0, self.log_output, f"\n❌ {action} failed with exit code {process.returncode}\n")
                self.root.after(0, lambda: self.status_var.set(f"{action} failed"))
        
        except Exception as e:
            self.root.after(0, self.log_output, f"\n❌ Error running {action}: {str(e)}\n")
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
        
        finally:
            # Reset UI
            self.root.after(0, self.reset_ui)
    
    def reset_ui(self):
        """Reset UI after command completion."""
        self.is_running.set(False)
        self.set_buttons_state(True)
        self.progress_bar.stop()
    
    def set_buttons_state(self, enabled):
        """Enable or disable all action buttons."""
        state = 'normal' if enabled else 'disabled'
        for button in self.action_buttons:
            button.configure(state=state)
    
    def log_output(self, text):
        """Log output to the text area."""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_output(self):
        """Clear the output text area."""
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Output cleared")

def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = GitHubAuditGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == '__main__':
    main() 