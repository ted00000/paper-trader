import re

with open('/root/paper_trading_lab/dashboard_v2/backend/api_enhanced.py', 'r') as f:
    content = f.read()

old_code = '''try:
        with open(latest_file) as f:
            data = json.load(f)

        # Extract text content from Claude response
        content = data.get('content', [{}])[0].get('text', '')'''

new_code = '''try:
        with open(latest_file) as f:
            data = json.load(f)

        # Extract text content from Claude response OR format structured execute log
        content = data.get('content', [{}])[0].get('text', '')

        # If no content, check if this is a structured execute log
        if not content and operation == 'execute' and 'summary' in data:
            # Format execute log nicely
            summary = data.get('summary', {})
            closed_trades = data.get('closed_trades', [])
            new_entries = data.get('new_entries', [])
            timestamp = data.get('timestamp', 'Unknown')

            lines = []
            lines.append('# EXECUTE Results')
            lines.append('')
            lines.append(f'**Timestamp:** {timestamp}')
            lines.append('')
            lines.append('## Summary')
            lines.append('')
            lines.append(f'- **Holding:** {summary.get("holding", 0)} positions')
            lines.append(f'- **New Entries:** {summary.get("entered", 0)}')
            lines.append(f'- **Closed:** {summary.get("closed", 0)}')
            lines.append(f'- **Total Active:** {summary.get("total_active", 0)}')
            lines.append('')

            if new_entries:
                lines.append('## New Entries')
                lines.append('')
                for entry in new_entries:
                    ticker = entry.get('ticker', 'N/A')
                    price = entry.get('entry_price', 0)
                    lines.append(f'- **{ticker}** @ ${price:.2f}')
                lines.append('')

            if closed_trades:
                lines.append('## Closed Trades')
                lines.append('')
                for trade in closed_trades:
                    ticker = trade.get('ticker', 'N/A')
                    exit_price = trade.get('exit_price', 0)
                    pnl = trade.get('pnl_pct', 0)
                    reason = trade.get('reason', 'Unknown')
                    lines.append(f'- **{ticker}** @ ${exit_price:.2f} ({pnl:+.2f}%) - {reason}')
                lines.append('')

            if not new_entries and not closed_trades:
                lines.append('*No trades executed this session.*')

            content = '\n'.join(lines)'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('/root/paper_trading_lab/dashboard_v2/backend/api_enhanced.py', 'w') as f:
        f.write(content)
    print('SUCCESS: Fixed execute log formatting')
else:
    print('ERROR: Could not find old code pattern')
