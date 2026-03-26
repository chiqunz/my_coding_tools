"""
Robustness testing utilities for mid-term quantitative strategy signals.

Provides tools to evaluate whether a signal is exploiting real structure
or fitting noise. Key tests:
  - Parameter perturbation (does the signal survive ±20% changes?)
  - Indicator correlation (are you triple-counting the same info?)
  - Turnover estimation (is the strategy viable after costs?)

Dependencies: pandas, numpy, scipy (for linregress in correlation checks).
"""

from typing import Any

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Parameter perturbation test
# ---------------------------------------------------------------------------


def perturb_parameters(
    base_params: dict[str, Any],
    perturbation: float = 0.20,
) -> list[dict[str, Any]]:
    """
    Generate perturbed parameter sets (±perturbation) for all numeric params.

    Returns a list of (label, params_dict) tuples.
    """
    variants = [("base", base_params.copy())]

    for key, value in base_params.items():
        if not isinstance(value, (int, float)):
            continue
        for direction, mult in [("low", 1 - perturbation), ("high", 1 + perturbation)]:
            variant = base_params.copy()
            variant[key] = type(value)(value * mult)
            variants.append((f"{key}_{direction}", variant))

    return variants


def parameter_robustness_report(
    signal_func: callable,
    ohlcv: pd.DataFrame,
    base_params: dict[str, Any],
    perturbation: float = 0.20,
    metric_func: callable | None = None,
) -> dict:
    """
    Test a signal function across ±perturbation of all numeric parameters.

    Parameters
    ----------
    signal_func : callable(ohlcv, **params) -> pd.Series
    ohlcv : OHLCV DataFrame
    base_params : dict of default parameters
    perturbation : fractional perturbation (default 0.20 = ±20%)
    metric_func : callable(signal_series) -> float, defaults to mean signal

    Returns
    -------
    dict with per-variant metrics, spread, and robustness verdict.
    """
    if metric_func is None:
        metric_func = lambda s: s[s != 0].mean() if (s != 0).any() else 0.0

    variants = perturb_parameters(base_params, perturbation)
    results = {}

    for label, params in variants:
        signal = signal_func(ohlcv, **params)
        results[label] = round(metric_func(signal), 6)

    all_metrics = [v for v in results.values() if not np.isnan(v)]
    if not all_metrics or max(abs(m) for m in all_metrics) < 1e-10:
        return {
            "results": results,
            "spread": float("nan"),
            "is_robust": False,
            "verdict": "NO SIGNAL — all variants produced zero/near-zero metrics",
        }

    base_val = results.get("base", 0)
    spread = (max(all_metrics) - min(all_metrics)) / max(abs(base_val), 1e-6)

    return {
        "results": results,
        "spread": round(spread, 3),
        "is_robust": spread < 0.3,
        "verdict": "ROBUST" if spread < 0.3 else "FRAGILE — likely fitting noise",
    }


# ---------------------------------------------------------------------------
# Indicator correlation / redundancy check
# ---------------------------------------------------------------------------


def check_indicator_redundancy(
    indicators: pd.DataFrame,
    threshold: float = 0.70,
) -> dict:
    """
    Check for redundant indicator pairs (correlation > threshold).

    Parameters
    ----------
    indicators : DataFrame where each column is an indicator series
    threshold : absolute correlation above which pairs are redundant

    Returns
    -------
    dict with correlation matrix, redundant pairs, and action.
    """
    corr = indicators.corr()
    redundant_pairs = []
    cols = corr.columns.tolist()

    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            r = corr.iloc[i, j]
            if abs(r) > threshold:
                redundant_pairs.append((cols[i], cols[j], round(r, 3)))

    return {
        "correlation_matrix": corr.round(3),
        "redundant_pairs": redundant_pairs,
        "has_redundancy": len(redundant_pairs) > 0,
        "action": (
            "Remove one indicator from each redundant pair"
            if redundant_pairs
            else "No redundancy detected — good indicator diversity"
        ),
    }


# ---------------------------------------------------------------------------
# Turnover estimation
# ---------------------------------------------------------------------------


def estimate_annual_turnover(positions: pd.Series) -> float:
    """
    Estimate annual one-way turnover from a position series.

    positions : Series of position values (e.g. +1, 0, -1) indexed by date.
    Returns annualized one-way turnover as a fraction (1.0 = 100%).
    """
    trades = positions.diff().abs()
    daily_turnover = trades.mean()
    return daily_turnover * 252


def estimate_annual_cost(
    positions: pd.Series,
    cost_per_trade_bps: float = 10.0,
) -> dict:
    """
    Estimate annual transaction costs from turnover.

    Parameters
    ----------
    positions : Series of position values indexed by date
    cost_per_trade_bps : one-way cost in basis points (default 10 = large cap)

    Returns
    -------
    dict with turnover_pct, annual_cost_bps, and viability assessment.
    """
    turnover = estimate_annual_turnover(positions)
    # Cost = turnover × 2 (round trip) × cost_per_trade
    annual_cost_bps = turnover * 2 * cost_per_trade_bps

    return {
        "annual_turnover_pct": round(turnover * 100, 1),
        "annual_cost_bps": round(annual_cost_bps, 1),
        "cost_per_trade_bps": cost_per_trade_bps,
        "viability_note": (
            f"Alpha must exceed {annual_cost_bps * 3:.0f} bps (3× cost rule) "
            f"to be viable."
        ),
    }


# ---------------------------------------------------------------------------
# Signal quality summary
# ---------------------------------------------------------------------------


def signal_summary(signal: pd.Series) -> dict:
    """
    Quick summary statistics for a signal series.

    Useful for sanity-checking before deeper analysis.
    """
    non_zero = signal[signal != 0]
    return {
        "total_bars": len(signal),
        "non_zero_signals": len(non_zero),
        "signal_rate_pct": round(len(non_zero) / max(len(signal), 1) * 100, 2),
        "mean_signal": round(non_zero.mean(), 6) if len(non_zero) > 0 else 0,
        "std_signal": round(non_zero.std(), 6) if len(non_zero) > 1 else 0,
        "min_signal": round(non_zero.min(), 6) if len(non_zero) > 0 else 0,
        "max_signal": round(non_zero.max(), 6) if len(non_zero) > 0 else 0,
        "long_signals": int((signal > 0).sum()),
        "short_signals": int((signal < 0).sum()),
    }
