@app.route('/api/v2/screening-decisions', methods=['GET'])
def get_screening_decisions():
    """
    Get today screening decisions from GO log
    Returns all stocks analyzed (ENTER and REJECTED) with their details
    """
    import re

    # Find most recent GO log
    daily_reviews_dir = PROJECT_DIR / 'daily_reviews'
    go_files = sorted(daily_reviews_dir.glob('go_*.json'), reverse=True)

    if not go_files:
        return jsonify({
            'decisions': [],
            'summary': 'No screening data available - run GO command',
            'timestamp': None,
            'is_today': False,
            'total_reviewed': 0
        })

    latest_go = go_files[0]

    try:
        with open(latest_go) as f:
            data = json.load(f)

        content = data.get('content', [{}])[0].get('text', '')

        # Extract date from filename (go_YYYYMMDD_HHMMSS.json)
        filename = latest_go.name
        date_match = re.search(r'go_(\d{8})_(\d{6})', filename)
        if date_match:
            file_date = date_match.group(1)
            file_time = date_match.group(2)
            data_date = f'{file_date[:4]}-{file_date[4:6]}-{file_date[6:8]}'
            data_time = f'{file_time[:2]}:{file_time[2:4]}:{file_time[4:6]}'
            timestamp = f'{data_time} ET'
        else:
            data_date = ''
            timestamp = ''

        today = datetime.now().strftime('%Y-%m-%d')
        is_today = (data_date == today)

        decisions = []

        # Load screener data for scores (used as fallback for all stocks)
        screener_file = PROJECT_DIR / 'screener_candidates.json'
        screener_scores = {}
        if screener_file.exists():
            try:
                with open(screener_file) as f:
                    screener_data = json.load(f)
                for c in screener_data.get('candidates', []):
                    t = c.get('ticker')
                    screener_scores[t] = {
                        'score': c.get('composite_score', 0),
                        'rs': c.get('relative_strength', {}).get('rs_pct', 0),
                        'sector': c.get('sector', 'Unknown')
                    }
            except:
                pass

        # Parse BUY decisions from JSON block
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                decisions_json = json.loads(json_match.group(1))
                for b in decisions_json.get('buy', []):
                    ticker = b.get('ticker', '')
                    catalyst = b.get('catalyst', 'Unknown')
                    confidence = b.get('confidence_level', 'MEDIUM')
                    size_pct = b.get('position_size_pct', 0)

                    # Determine display decision
                    if size_pct == 0:
                        decision = 'Accepted (Low Conviction - 0% size)'
                    else:
                        decision = f'Accepted ({confidence} conviction)'

                    # Extract score from content - look for "Score:** XX.X"
                    score_match = re.search(rf'\*\*{ticker}.*?Score:\*\*\s*([\d.]+)', content, re.DOTALL)
                    score = float(score_match.group(1)) if score_match else size_pct * 10

                    # Extract RS from content
                    rs_match = re.search(rf'{ticker}.*?\|\s*\*\*RS:\*\*\s*\+?([\d.-]+)%', content, re.DOTALL)
                    rs = float(rs_match.group(1)) if rs_match else 0

                    decisions.append({
                        'ticker': ticker,
                        'decision': decision,
                        'status': 'ACCEPTED',
                        'reason': f'Catalyst: {catalyst} | Tier: Tier1 | RS: {rs:.1f}%',
                        'score': score,
                        'conviction': confidence,
                        'size_pct': size_pct,
                        'tier': 'Tier1' if size_pct >= 8 else 'Tier2'
                    })
            except json.JSONDecodeError:
                pass

        # Parse PASS decisions with detailed analysis
        # Pattern: ### N. **TICKER (Sector) - PASS**
        pass_pattern = r'### \d+\.\s*\*\*(\w+)\s*\(([^)]+)\)\s*-\s*PASS'
        for match in re.finditer(pass_pattern, content):
            ticker = match.group(1)
            sector = match.group(2)

            # Extract score - look for "Score:** XX.X" pattern
            score_match = re.search(rf'\*\*{ticker}.*?Score:\*\*\s*([\d.]+)', content, re.DOTALL)
            score = float(score_match.group(1)) if score_match else 0

            # Get RS from screener (more reliable than parsing Claude's text)
            screener_info = screener_scores.get(ticker, {})
            rs = screener_info.get('rs', 0)

            decisions.append({
                'ticker': ticker,
                'decision': 'Rejected',
                'status': 'REJECTED',
                'reason': f'Sector: {sector} | RS: {rs:.1f}%',
                'score': score,
                'conviction': 'SKIP',
                'size_pct': 0,
                'tier': 'N/A'
            })

        # Parse "Other Candidates" brief rejects - get scores from screener
        other_match = re.search(r'\*\*Other Candidates \(([^)]+)\).*?PASS', content)
        if other_match:
            other_tickers = [t.strip() for t in other_match.group(1).split(',')]
            for ticker in other_tickers:
                screener_info = screener_scores.get(ticker, {})
                score = screener_info.get('score', 0)
                rs = screener_info.get('rs', 0)
                sector = screener_info.get('sector', 'Unknown')

                decisions.append({
                    'ticker': ticker,
                    'decision': 'Rejected',
                    'status': 'REJECTED',
                    'reason': f'Sector: {sector} | RS: {rs:.1f}%',
                    'score': score,
                    'conviction': 'SKIP',
                    'size_pct': 0,
                    'tier': 'N/A'
                })

        # Sort: Accepted first, then by score descending
        decisions.sort(key=lambda x: (0 if x['status'] == 'ACCEPTED' else 1, -x['score']))

        # Build summary
        accepted = sum(1 for d in decisions if d['status'] == 'ACCEPTED')
        rejected = sum(1 for d in decisions if d['status'] == 'REJECTED')
        total = len(decisions)

        if total == 0:
            summary = 'No stocks analyzed yet'
        elif accepted == 0:
            summary = f'Analyzed {total} stocks - None met criteria'
        else:
            summary = f'Analyzed {total} stocks - {accepted} accepted, {rejected} rejected'

        return jsonify({
            'decisions': decisions,
            'summary': summary,
            'timestamp': timestamp,
            'is_today': is_today,
            'total_reviewed': total
        })

    except Exception as e:
        return jsonify({
            'error': f'Error loading screening decisions: {str(e)}',
            'decisions': [],
            'summary': 'Error loading data',
            'timestamp': None,
            'is_today': False,
            'total_reviewed': 0
        }), 500

