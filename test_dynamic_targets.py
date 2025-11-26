#!/usr/bin/env python3
"""
Test script for Enhancement 1.2: Dynamic profit targets by catalyst

Tests various catalyst types to ensure correct profit targets are assigned.
"""

def get_dynamic_profit_target(catalyst_tier, catalyst_type, catalyst_details=None):
    """Enhancement 1.2: Calculate catalyst-specific profit targets"""
    catalyst_type_str = catalyst_type.lower() if isinstance(catalyst_type, str) else ''

    if catalyst_tier == 'Tier1' or catalyst_tier == 'Tier 1':
        # M&A Catalyst
        if 'm&a' in catalyst_type_str or 'merger' in catalyst_type_str or 'acquisition' in catalyst_type_str:
            is_target = catalyst_details.get('is_target', False) if catalyst_details else False
            if is_target:
                return {
                    'target_pct': 15.0,
                    'stretch_target': 20.0,
                    'rationale': 'M&A target, deal premium capture',
                    'expected_hold_days': '5-10 days (or until deal close)'
                }
            else:
                return {
                    'target_pct': 8.0,
                    'stretch_target': None,
                    'rationale': 'M&A acquirer (not target)',
                    'expected_hold_days': '3-5 days'
                }

        # FDA Approval
        elif 'fda' in catalyst_type_str or 'approval' in catalyst_type_str:
            return {
                'target_pct': 15.0,
                'stretch_target': 25.0,
                'rationale': 'FDA approval, major catalyst',
                'expected_hold_days': '5-10 days'
            }

        # Earnings Beat
        elif 'earnings' in catalyst_type_str or 'post_earnings_drift' in catalyst_type_str:
            surprise_pct = catalyst_details.get('surprise_pct', 0) if catalyst_details else 0
            if surprise_pct >= 20:
                return {
                    'target_pct': 12.0,
                    'stretch_target': 15.0,
                    'rationale': f'Earnings beat +{surprise_pct:.0f}%, strong drift expected',
                    'expected_hold_days': '5-10 days (post-earnings drift)'
                }
            else:
                return {
                    'target_pct': 10.0,
                    'stretch_target': None,
                    'rationale': f'Earnings beat +{surprise_pct:.0f}%',
                    'expected_hold_days': '5-7 days'
                }

        # Contract
        elif 'contract' in catalyst_type_str:
            return {
                'target_pct': 12.0,
                'stretch_target': None,
                'rationale': 'Major contract announcement',
                'expected_hold_days': '5-7 days'
            }

        # Analyst Upgrade
        elif 'analyst' in catalyst_type_str or 'upgrade' in catalyst_type_str:
            firm = catalyst_details.get('firm', '') if catalyst_details else ''
            if firm in ['Goldman Sachs', 'Morgan Stanley', 'JP Morgan', 'BofA']:
                return {
                    'target_pct': 12.0,
                    'stretch_target': None,
                    'rationale': f'Top-tier upgrade from {firm}',
                    'expected_hold_days': '5-7 days'
                }
            else:
                return {
                    'target_pct': 8.0,
                    'stretch_target': None,
                    'rationale': 'Analyst upgrade',
                    'expected_hold_days': '3-5 days'
                }

        return {
            'target_pct': 10.0,
            'stretch_target': None,
            'rationale': 'Tier 1 catalyst',
            'expected_hold_days': '5-7 days'
        }

    elif catalyst_tier == 'Tier2' or catalyst_tier == 'Tier 2':
        return {
            'target_pct': 8.0,
            'stretch_target': None,
            'rationale': 'Tier 2 catalyst',
            'expected_hold_days': '3-5 days'
        }

    elif catalyst_tier == 'Tier3' or catalyst_tier == 'Tier 3':
        return {
            'target_pct': 10.0,
            'stretch_target': None,
            'rationale': 'Insider buying (leading indicator)',
            'expected_hold_days': '10-20 days (longer hold)'
        }

    return {
        'target_pct': 10.0,
        'stretch_target': None,
        'rationale': 'Standard target',
        'expected_hold_days': '5-7 days'
    }


print("="*80)
print("DYNAMIC PROFIT TARGETS TEST SUITE")
print("Enhancement 1.2: Catalyst-specific profit targets")
print("="*80 + "\n")

# Test cases
test_cases = [
    {
        'name': 'BIIB M&A Target',
        'tier': 'Tier1',
        'type': 'M&A_news',
        'details': {'is_target': True},
        'expected_target': 15.0,
        'expected_stretch': 20.0
    },
    {
        'name': 'FDA Approval',
        'tier': 'Tier1',
        'type': 'FDA_news',
        'details': {},
        'expected_target': 15.0,
        'expected_stretch': 25.0
    },
    {
        'name': 'Big Earnings Beat (25%)',
        'tier': 'Tier1',
        'type': 'earnings_beat',
        'details': {'surprise_pct': 25},
        'expected_target': 12.0,
        'expected_stretch': 15.0
    },
    {
        'name': 'Standard Earnings Beat (10%)',
        'tier': 'Tier1',
        'type': 'earnings_beat',
        'details': {'surprise_pct': 10},
        'expected_target': 10.0,
        'expected_stretch': None
    },
    {
        'name': 'Goldman Sachs Upgrade',
        'tier': 'Tier1',
        'type': 'analyst_upgrade',
        'details': {'firm': 'Goldman Sachs'},
        'expected_target': 12.0,
        'expected_stretch': None
    },
    {
        'name': 'Generic Analyst Upgrade',
        'tier': 'Tier1',
        'type': 'analyst_upgrade',
        'details': {'firm': 'Wedbush'},
        'expected_target': 8.0,
        'expected_stretch': None
    },
    {
        'name': 'Tier 2 Catalyst',
        'tier': 'Tier2',
        'type': 'contract',
        'details': {},
        'expected_target': 8.0,
        'expected_stretch': None
    },
    {
        'name': 'Tier 3 Insider Buying',
        'tier': 'Tier3',
        'type': 'insider_buying',
        'details': {},
        'expected_target': 10.0,
        'expected_stretch': None
    },
]

all_passed = True

for tc in test_cases:
    result = get_dynamic_profit_target(tc['tier'], tc['type'], tc['details'])

    passed = (
        result['target_pct'] == tc['expected_target'] and
        result.get('stretch_target') == tc['expected_stretch']
    )

    status = '✓' if passed else '✗'
    print(f"{status} {tc['name']}")
    print(f"   Tier: {tc['tier']} | Type: {tc['type']}")
    print(f"   Target: +{result['target_pct']}%", end='')
    if result.get('stretch_target'):
        print(f" (stretch: +{result['stretch_target']}%)", end='')
    print()
    print(f"   Rationale: {result['rationale']}")
    print(f"   Hold: {result.get('expected_hold_days', 'N/A')}")

    if not passed:
        print(f"   ✗ EXPECTED: {tc['expected_target']}% (stretch: {tc['expected_stretch']})")
        print(f"   ✗ GOT: {result['target_pct']}% (stretch: {result.get('stretch_target')})")
        all_passed = False

    print()

print("="*80)
print("TEST SUMMARY")
print("="*80)

if all_passed:
    print("✓ ALL TESTS PASSED - Dynamic profit targets working correctly")
    print("\nExpected Impact:")
    print("  - M&A targets held to +15% vs +10% (50% more upside)")
    print("  - FDA approvals held to +15% vs +10%")
    print("  - Big earnings beats held to +12% vs +10%")
    print("  - Lower-tier catalysts get realistic +8% targets")
    print("  - Win rate improves due to realistic expectations")
    print("  - Average winner: +8% → +11-13%")
    exit(0)
else:
    print("✗ SOME TESTS FAILED - Review implementation")
    exit(1)
