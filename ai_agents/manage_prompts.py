#!/usr/bin/env python3
"""
Prompt Management Utility

A command-line tool for managing AI agent system prompts.
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from ai_agents.prompt_manager import PromptManager

def list_prompts():
    """List all available prompts"""
    manager = PromptManager()
    prompts = manager.list_available_prompts()
    
    print("📋 Available System Prompts:")
    print("=" * 40)
    
    if not prompts:
        print("No prompts found.")
        return
    
    for prompt in prompts:
        print(f"  • {prompt}")
        
        # Validate the prompt
        validation = manager.validate_prompt_file(prompt)
        status = "✅" if validation['valid'] else "❌"
        print(f"    {status} Valid: {validation['valid']}")
        
        if validation['warnings']:
            for warning in validation['warnings']:
                print(f"    ⚠️  {warning}")
        
        if validation['errors']:
            for error in validation['errors']:
                print(f"    ❌ {error}")
        
        print()

def validate_prompt(agent_name):
    """Validate a specific prompt"""
    manager = PromptManager()
    
    print(f"🔍 Validating {agent_name} prompt...")
    print("=" * 40)
    
    validation = manager.validate_prompt_file(agent_name)
    
    print(f"Valid: {validation['valid']}")
    print(f"File exists: {validation['file_exists']}")
    print(f"File size: {validation['file_size']} characters")
    
    if validation['errors']:
        print("\n❌ Errors:")
        for error in validation['errors']:
            print(f"  • {error}")
    
    if validation['warnings']:
        print("\n⚠️  Warnings:")
        for warning in validation['warnings']:
            print(f"  • {warning}")
    
    if validation['valid']:
        print("\n✅ Prompt is valid and ready to use!")

def show_prompt(agent_name):
    """Show the content of a prompt"""
    manager = PromptManager()
    
    try:
        prompt = manager.get_system_prompt(agent_name)
        print(f"📄 System Prompt for {agent_name}:")
        print("=" * 60)
        print(prompt)
        print("=" * 60)
        print(f"Total length: {len(prompt)} characters")
    except Exception as e:
        print(f"❌ Error loading prompt: {e}")

def edit_prompt(agent_name):
    """Open a prompt file for editing"""
    manager = PromptManager()
    prompts_dir = manager.prompts_dir
    prompt_file = os.path.join(prompts_dir, f"{agent_name}_system_prompt.md")
    
    if not os.path.exists(prompt_file):
        print(f"❌ Prompt file not found: {prompt_file}")
        return
    
    # Try to open with default editor
    import subprocess
    import shutil
    
    editor = os.environ.get('EDITOR', 'nano')
    
    try:
        subprocess.run([editor, prompt_file])
        print(f"✅ Opened {prompt_file} for editing")
        
        # Validate after editing
        print("\n🔍 Validating after edit...")
        validate_prompt(agent_name)
        
    except FileNotFoundError:
        print(f"❌ Editor '{editor}' not found. Please edit manually:")
        print(f"   {prompt_file}")

def create_prompt(agent_name):
    """Create a new prompt from template"""
    manager = PromptManager()
    prompts_dir = manager.prompts_dir
    
    template_file = os.path.join(prompts_dir, "agent_prompt_template.md")
    new_prompt_file = os.path.join(prompts_dir, f"{agent_name}_system_prompt.md")
    
    if os.path.exists(new_prompt_file):
        print(f"❌ Prompt file already exists: {new_prompt_file}")
        return
    
    if not os.path.exists(template_file):
        print(f"❌ Template file not found: {template_file}")
        return
    
    try:
        with open(template_file, 'r') as f:
            template_content = f.read()
        
        with open(new_prompt_file, 'w') as f:
            f.write(template_content)
        
        print(f"✅ Created new prompt file: {new_prompt_file}")
        print("📝 Please edit the file to customize it for your agent")
        
        # Open for editing
        edit_prompt(agent_name)
        
    except Exception as e:
        print(f"❌ Error creating prompt: {e}")

def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(description="Manage AI agent system prompts")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    subparsers.add_parser('list', help='List all available prompts')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a prompt')
    validate_parser.add_argument('agent_name', help='Name of the agent')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show prompt content')
    show_parser.add_argument('agent_name', help='Name of the agent')
    
    # Edit command
    edit_parser = subparsers.add_parser('edit', help='Edit a prompt')
    edit_parser.add_argument('agent_name', help='Name of the agent')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new prompt from template')
    create_parser.add_argument('agent_name', help='Name of the agent')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'list':
        list_prompts()
    elif args.command == 'validate':
        validate_prompt(args.agent_name)
    elif args.command == 'show':
        show_prompt(args.agent_name)
    elif args.command == 'edit':
        edit_prompt(args.agent_name)
    elif args.command == 'create':
        create_prompt(args.agent_name)

if __name__ == "__main__":
    main()
