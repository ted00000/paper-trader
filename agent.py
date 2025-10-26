#!/usr/bin/env python3
"""
Paper Trading Lab - Automated Agent
Executes 'Go' and 'analyze' commands via Claude API on schedule
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# Configuration
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
CLAUDE_API_URL = 'https://api.anthropic.com/v1/messages'
CLAUDE_MODEL = 'claude-sonnet-4-5-20250929'
PROJECT_DIR = Path(__file__).parent / 'paper_trading_lab'

def call_claude_api(command, project_context):
    """Call Claude API with the given command"""
    
    if not CLAUDE_API_KEY:
        print("ERROR: CLAUDE_API_KEY environment variable not set")
        sys.exit(1)
    
    headers = {
        'x-api-key': CLAUDE_API_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
    }
    
    # Build the message with project context
    system_prompt = f"""You are the Paper Trading Lab assistant. 

Project Context:
{project_context}

Execute the user's command following the PROJECT_INSTRUCTIONS.md guidelines."""
    
    payload = {
        'model': CLAUDE_MODEL,
        'max_tokens': 16000,
        'system': system_prompt,
        'messages': [
            {
                'role': 'user',
                'content': command
            }
        ]
    }
    
    try:
        response = requests.post(CLAUDE_API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR calling Claude API: {e}")
        sys.exit(1)

def load_project_context():
    """Load key project files to provide context to Claude"""
    
    context = {}
    
    # Load PROJECT_INSTRUCTIONS.md
    instructions_file = PROJECT_DIR / 'PROJECT_INSTRUCTIONS.md'
    if instructions_file.exists():
        context['instructions'] = instructions_file.read_text()
    
    # Load current portfolio
    portfolio_file = PROJECT_DIR / 'portfolio_data' / 'current_portfolio.json'
    if portfolio_file.exists():
        context['portfolio'] = portfolio_file.read_text()
    
    # Load account status
    account_file = PROJECT_DIR / 'portfolio_data' / 'account_status.json'
    if account_file.exists():
        context['account'] = account_file.read_text()
    
    # Load latest lessons learned
    lessons_file = PROJECT_DIR / 'strategy_evolution' / 'lessons_learned.md'
    if lessons_file.exists():
        context['lessons'] = lessons_file.read_text()
    
    # Format as string
    context_str = f"""
PROJECT INSTRUCTIONS:
{context.get('instructions', 'Not found')}

CURRENT PORTFOLIO:
{context.get('portfolio', 'Not initialized')}

ACCOUNT STATUS:
{context.get('account', 'Not initialized')}

LESSONS LEARNED:
{context.get('lessons', 'None yet')}
"""
    
    return context_str

def save_response(command, response_data):
    """Save the API response to a file"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_dir = PROJECT_DIR / 'daily_reviews'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract the text response
    response_text = response_data.get('content', [{}])[0].get('text', '')
    
    # Save to file
    filename = f"{timestamp}_{command}.md"
    output_file = output_dir / filename
    
    with open(output_file, 'w') as f:
        f.write(f"# {command.upper()} Command Response\n\n")
        f.write(f"**Timestamp:** {timestamp}\n\n")
        f.write("---\n\n")
        f.write(response_text)
    
    print(f"Response saved to: {output_file}")
    
    # Also save to latest file for dashboard
    latest_file = PROJECT_DIR / f'latest_{command}.json'
    with open(latest_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'command': command,
            'response': response_text
        }, f, indent=2)

def main():
    """Main execution function"""
    
    if len(sys.argv) < 2:
        print("Usage: python agent.py [go|analyze]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command not in ['go', 'analyze']:
        print("ERROR: Command must be 'go' or 'analyze'")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"Paper Trading Lab Agent - {command.upper()} Command")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print(f"{'='*60}\n")
    
    # Load project context
    print("Loading project context...")
    context = load_project_context()
    
    # Call Claude API
    print(f"Executing '{command}' command via Claude API...")
    response = call_claude_api(command, context)
    
    # Save response
    print("Saving response...")
    save_response(command, response)
    
    print(f"\n{'='*60}")
    print(f"{command.upper()} command completed successfully!")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
