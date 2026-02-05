#!/usr/bin/env python3
"""
Stagnation Scorer Module - Best-in-Class Dead Capital Detection

Detects positions that have failed to realize expected movement given:
- Time held
- Instrument volatility (ATR-based)
- Market regime

Outputs a stagnation score (0-1) and recommended action for Claude to consider.

Based on institutional quant best practices:
- Volatility-adjusted expected move thresholds
- Time-weighted scoring (ramps up after min hold)
- Agent override capability (Claude can extend with good reason)
- Catalyst grace period (don't penalize near upcoming events)

Integration:
- GO command: Calculate scores, include in Claude's context
- EXIT command: Factor into exit decisions
- Learning: Track stagnation exits vs outcomes
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp value between lo and hi"""
    return max(lo, min(hi, x))


class StagnationState(str, Enum):
    """Position stagnation state"""
    OK = "OK"                       # Position moving as expected
    WATCH = "WATCH"                 # Position underperforming, monitor closely
    EXIT_CANDIDATE = "EXIT_CANDIDATE"  # Strong candidate for exit


class StagnationAction(str, Enum):
    """Recommended action based on stagnation"""
    HOLD = "HOLD"   # Keep position
    EXIT = "EXIT"   # Exit position (Claude decides final action)


@dataclass(frozen=True)
class StagnationConfig:
    """Configuration for stagnation scoring"""

    # Movement expectation
    k_atr: float = 0.75          # Expected move threshold as fraction of ATR
    regime_vol_mult: float = 1.0  # External vol regime multiplier (0.8 low vol, 1.2 high vol)

    # Time logic
    min_hold_days: float = 3.0    # Don't penalize before this (let thesis develop)
    max_hold_days: float = 10.0   # Score saturates by this time

    # Action thresholds
    watch_threshold: float = 0.50   # Score above this = WATCH state
    exit_threshold: float = 0.75    # Score above this = EXIT_CANDIDATE state

    # Catalyst grace (reduce penalty near upcoming catalysts)
    catalyst_grace_days: float = 2.0   # Within this many days of catalyst
    catalyst_score_multiplier: float = 0.5  # Score *= this during grace


@dataclass(frozen=True)
class StagnationResult:
    """Result of stagnation scoring"""
    stagnation_score: float      # 0.0 (not stagnant) to 1.0 (very stagnant)
    state: StagnationState       # OK, WATCH, or EXIT_CANDIDATE
    action: StagnationAction     # HOLD or EXIT (recommendation for Claude)
    explain: Dict[str, Any]      # Detailed breakdown for logging/debugging


class StagnationScorer:
    """
    Best-practice stagnation scoring for swing trading positions.

    Key principles:
    - Volatility-adjusted: Uses ATR to set expectations per instrument
    - Time-weighted: Penalty ramps up over time
    - Catalyst-aware: Reduces penalty near upcoming events
    - Agent-friendly: Produces scores for Claude to consider, not hard exits

    Usage:
        scorer = StagnationScorer()
        result = scorer.score(
            entry_price=100.0,
            current_price=101.0,
            entry_date=datetime(2026, 1, 20),
            atr=3.2,
            days_held=7
        )

        if result.state == StagnationState.EXIT_CANDIDATE:
            # Include in Claude's exit review
            pass
    """

    def __init__(self, config: Optional[StagnationConfig] = None) -> None:
        self.cfg = config or StagnationConfig()

    def score(
        self,
        *,
        entry_price: float,
        current_price: float,
        entry_date: datetime,
        atr: float,
        days_held: Optional[int] = None,
        regime_vol_mult: Optional[float] = None,
        catalyst_date: Optional[datetime] = None,
    ) -> StagnationResult:
        """
        Calculate stagnation score for a position.

        Args:
            entry_price: Price at entry
            current_price: Current price
            entry_date: Date of entry
            atr: Average True Range (14-day typical) in dollars
            days_held: Days held (calculated from entry_date if not provided)
            regime_vol_mult: Vol regime multiplier (default 1.0)
            catalyst_date: Upcoming catalyst date (optional, reduces penalty)

        Returns:
            StagnationResult with score, state, action, and explanation
        """
        if entry_price <= 0:
            raise ValueError("entry_price must be > 0")
        if current_price <= 0:
            raise ValueError("current_price must be > 0")
        if atr <= 0:
            # If ATR unavailable, use a conservative proxy (3% of entry price)
            atr = entry_price * 0.03

        cfg = self.cfg
        vol_mult = regime_vol_mult if regime_vol_mult is not None else cfg.regime_vol_mult
        vol_mult = max(0.1, float(vol_mult))

        # Calculate days held if not provided
        now = datetime.now()
        if days_held is None:
            if entry_date.tzinfo:
                entry_date = entry_date.replace(tzinfo=None)
            days_held = (now - entry_date).days

        days_in_trade = float(days_held)

        # Movement calculation
        abs_return_pct = abs((current_price - entry_price) / entry_price) * 100
        abs_move = abs(current_price - entry_price)

        # Expected move in dollars (volatility-adjusted)
        expected_move = cfg.k_atr * atr * vol_mult

        # Deficit: how far short of expected movement
        # deficit = 1.0 means no movement, 0.0 means met/exceeded expectations
        denom = max(expected_move, 1e-9)
        deficit = _clamp((expected_move - abs_move) / denom, 0.0, 1.0)

        # Time factor: ramps from 0 after min_hold to 1 by max_hold
        if cfg.max_hold_days <= cfg.min_hold_days:
            time_factor = 1.0 if days_in_trade >= cfg.min_hold_days else 0.0
        else:
            time_factor = _clamp(
                (days_in_trade - cfg.min_hold_days) / (cfg.max_hold_days - cfg.min_hold_days),
                0.0, 1.0
            )

        # Catalyst factor: reduce score if catalyst is upcoming
        catalyst_factor = 1.0
        catalyst_days = None
        if catalyst_date is not None:
            if catalyst_date.tzinfo:
                catalyst_date = catalyst_date.replace(tzinfo=None)
            catalyst_days = (catalyst_date - now).days
            # If catalyst is within grace window and in the future
            if 0.0 <= catalyst_days <= cfg.catalyst_grace_days:
                catalyst_factor = cfg.catalyst_score_multiplier

        # Final stagnation score
        stagnation_score = _clamp(deficit * time_factor * catalyst_factor, 0.0, 1.0)

        # Determine state and action
        if stagnation_score >= cfg.exit_threshold:
            state = StagnationState.EXIT_CANDIDATE
            action = StagnationAction.EXIT
        elif stagnation_score >= cfg.watch_threshold:
            state = StagnationState.WATCH
            action = StagnationAction.HOLD  # Watch but don't exit yet
        else:
            state = StagnationState.OK
            action = StagnationAction.HOLD

        # Build explanation dict
        explain = {
            "days_in_trade": days_in_trade,
            "abs_return_pct": round(abs_return_pct, 2),
            "abs_move": round(abs_move, 2),
            "atr": round(atr, 2),
            "k_atr": cfg.k_atr,
            "vol_mult": vol_mult,
            "expected_move": round(expected_move, 2),
            "deficit": round(deficit, 3),
            "time_factor": round(time_factor, 3),
            "catalyst_factor": catalyst_factor,
            "catalyst_days": catalyst_days,
            "watch_threshold": cfg.watch_threshold,
            "exit_threshold": cfg.exit_threshold,
            "min_hold_days": cfg.min_hold_days,
            "max_hold_days": cfg.max_hold_days,
        }

        return StagnationResult(
            stagnation_score=round(stagnation_score, 3),
            state=state,
            action=action,
            explain=explain,
        )

    def format_for_claude(self, result: StagnationResult, ticker: str) -> str:
        """
        Format stagnation result for inclusion in Claude's context.

        Args:
            result: StagnationResult from score()
            ticker: Stock ticker symbol

        Returns:
            Formatted string for Claude's context
        """
        exp = result.explain

        if result.state == StagnationState.OK:
            return f"  {ticker}: OK (score {result.stagnation_score:.2f}) - moving as expected"

        elif result.state == StagnationState.WATCH:
            return (
                f"  {ticker}: WATCH (score {result.stagnation_score:.2f}) - "
                f"moved {exp['abs_return_pct']:.1f}% in {exp['days_in_trade']:.0f} days "
                f"(expected {exp['expected_move']:.2f} move based on ATR)"
            )

        else:  # EXIT_CANDIDATE
            return (
                f"  {ticker}: EXIT_CANDIDATE (score {result.stagnation_score:.2f}) - "
                f"STAGNANT: only {exp['abs_return_pct']:.1f}% move in {exp['days_in_trade']:.0f} days "
                f"(expected {exp['expected_move']:.2f} based on {exp['atr']:.2f} ATR). "
                f"Consider freeing capital."
            )


# Default scorer instance for easy import
default_scorer = StagnationScorer()


def score_position(
    entry_price: float,
    current_price: float,
    entry_date: datetime,
    atr: float,
    days_held: Optional[int] = None,
    regime_vol_mult: Optional[float] = None,
    catalyst_date: Optional[datetime] = None,
) -> StagnationResult:
    """
    Convenience function to score a position using default config.

    See StagnationScorer.score() for full documentation.
    """
    return default_scorer.score(
        entry_price=entry_price,
        current_price=current_price,
        entry_date=entry_date,
        atr=atr,
        days_held=days_held,
        regime_vol_mult=regime_vol_mult,
        catalyst_date=catalyst_date,
    )


if __name__ == "__main__":
    # Test the scorer
    print("Stagnation Scorer Test")
    print("=" * 50)

    scorer = StagnationScorer()

    # Test case 1: Position barely moved after 7 days
    result1 = scorer.score(
        entry_price=100.0,
        current_price=101.0,  # Only +1%
        entry_date=datetime(2026, 1, 28),
        atr=3.0,  # $3 ATR = 3%
        days_held=7,
    )
    print(f"\nTest 1: Stagnant position (+1% in 7 days, ATR=3%)")
    print(f"  Score: {result1.stagnation_score}")
    print(f"  State: {result1.state}")
    print(f"  Action: {result1.action}")
    print(f"  {scorer.format_for_claude(result1, 'TEST1')}")

    # Test case 2: Position moved well
    result2 = scorer.score(
        entry_price=100.0,
        current_price=108.0,  # +8%
        entry_date=datetime(2026, 1, 28),
        atr=3.0,
        days_held=7,
    )
    print(f"\nTest 2: Healthy position (+8% in 7 days, ATR=3%)")
    print(f"  Score: {result2.stagnation_score}")
    print(f"  State: {result2.state}")
    print(f"  Action: {result2.action}")
    print(f"  {scorer.format_for_claude(result2, 'TEST2')}")

    # Test case 3: Early in trade (should not penalize)
    result3 = scorer.score(
        entry_price=100.0,
        current_price=100.5,  # Barely moved
        entry_date=datetime(2026, 2, 3),
        atr=3.0,
        days_held=2,  # Only 2 days
    )
    print(f"\nTest 3: Early position (2 days, should not penalize)")
    print(f"  Score: {result3.stagnation_score}")
    print(f"  State: {result3.state}")
    print(f"  Action: {result3.action}")
    print(f"  {scorer.format_for_claude(result3, 'TEST3')}")

    print("\n" + "=" * 50)
    print("Tests complete")
