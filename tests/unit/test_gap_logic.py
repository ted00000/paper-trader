#!/usr/bin/env python3
"""
Test script for Enhancement 0.1: Gap-aware entry/exit logic
"""

def analyze_premarket_gap(ticker, current_price, previous_close):
    """
    Enhancement 0.1: Analyze premarket gap and determine entry/exit strategy

    BIIB Lesson: Stock gapped +11.7% premarket, then faded to +7.3% at open.
    Large gaps often fade intraday - need smart entry timing.
    """
    gap_pct = ((current_price - previous_close) / previous_close) * 100

    if gap_pct >= 8.0:
        # Exhaustion gap - likely to fade (BIIB scenario)
        return {
            'classification': 'EXHAUSTION_GAP',
            'gap_pct': gap_pct,
            'should_enter_at_open': False,
            'should_exit_at_open': False,
            'reasoning': f'Gap {gap_pct:+.1f}% too large, high fade risk (see BIIB Nov 25). Wait for pullback or consolidation.'
        }
    elif gap_pct >= 5.0:
        # Breakaway gap - strong move, let it prove itself
        return {
            'classification': 'BREAKAWAY_GAP',
            'gap_pct': gap_pct,
            'should_enter_at_open': False,
            'should_exit_at_open': False,
            'reasoning': f'Gap {gap_pct:+.1f}% strong, let it consolidate first. Enter on dip or wait for support confirmation.'
        }
    elif gap_pct >= 2.0:
        # Continuation gap - moderate, tradeable with caution
        return {
            'classification': 'CONTINUATION_GAP',
            'gap_pct': gap_pct,
            'should_enter_at_open': True,
            'should_exit_at_open': True,
            'reasoning': f'Gap {gap_pct:+.1f}% moderate, wait 15min for stability then enter/exit.'
        }
    else:
        # Normal gap or gap down - enter/exit as planned
        return {
            'classification': 'NORMAL',
            'gap_pct': gap_pct,
            'should_enter_at_open': True,
            'should_exit_at_open': True,
            'reasoning': f'Gap {gap_pct:+.1f}% normal, enter/exit as planned.'
        }

print('Testing Gap Analysis Logic')
print('='*80)

# Test cases from BIIB scenario
test_cases = [
    {'name': 'BIIB Exhaustion Gap', 'current': 184.70, 'previous': 165.40, 'expected': 'EXHAUSTION_GAP'},
    {'name': 'Breakaway Gap', 'current': 106.00, 'previous': 100.00, 'expected': 'BREAKAWAY_GAP'},
    {'name': 'Continuation Gap', 'current': 103.00, 'previous': 100.00, 'expected': 'CONTINUATION_GAP'},
    {'name': 'Normal Gap', 'current': 101.00, 'previous': 100.00, 'expected': 'NORMAL'},
    {'name': 'Gap Down', 'current': 95.00, 'previous': 100.00, 'expected': 'NORMAL'},
]

all_passed = True
for tc in test_cases:
    result = analyze_premarket_gap('TEST', tc['current'], tc['previous'])
    passed = result['classification'] == tc['expected']
    status = '✓' if passed else '✗'

    print(f"{status} {tc['name']}")
    print(f"   Current: ${tc['current']:.2f} | Previous: ${tc['previous']:.2f}")
    print(f"   Gap: {result['gap_pct']:+.1f}% | Classification: {result['classification']}")
    print(f"   Enter at open: {result['should_enter_at_open']} | Exit at open: {result['should_exit_at_open']}")
    print(f"   Reasoning: {result['reasoning']}")
    print()

    if not passed:
        all_passed = False

print('='*80)
if all_passed:
    print('✓ All gap analysis tests PASSED')
    exit(0)
else:
    print('✗ Some tests FAILED')
    exit(1)
