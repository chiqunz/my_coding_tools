"""
OHLCV data quality checks for mid-term quantitative strategies.

Run these checks BEFORE computing any indicators. Bad data produces
bad signals — garbage in, garbage out.

Dependencies: pandas, numpy.
"""

import pandas as pd

REQUIRED_COLUMNS = {"Open", "High", "Low", "Close", "Volume"}


def check_columns(ohlcv: pd.DataFrame) -> list[str]:
    """Verify required OHLCV columns exist."""
    missing = REQUIRED_COLUMNS - set(ohlcv.columns)
    if missing:
        return [f"Missing required columns: {missing}"]
    return []


def check_ohlc_consistency(ohlcv: pd.DataFrame) -> list[str]:
    """High >= max(O,C) and Low <= min(O,C)."""
    issues = []
    high_ok = (ohlcv["High"] >= ohlcv[["Open", "Close"]].max(axis=1) - 1e-6).all()
    low_ok = (ohlcv["Low"] <= ohlcv[["Open", "Close"]].min(axis=1) + 1e-6).all()
    if not high_ok:
        count = (ohlcv["High"] < ohlcv[["Open", "Close"]].max(axis=1) - 1e-6).sum()
        issues.append(f"OHLC consistency: High < max(Open, Close) on {count} rows")
    if not low_ok:
        count = (ohlcv["Low"] > ohlcv[["Open", "Close"]].min(axis=1) + 1e-6).sum()
        issues.append(f"OHLC consistency: Low > min(Open, Close) on {count} rows")
    return issues


def check_extreme_returns(
    close: pd.Series,
    threshold: float = 0.50,
) -> list[str]:
    """Flag daily returns exceeding threshold — likely splits or data errors."""
    daily_ret = close.pct_change().abs()
    extreme = daily_ret > threshold
    if extreme.any():
        dates = close.index[extreme].tolist()
        return [
            f"Extreme returns (>{threshold * 100:.0f}%): {extreme.sum()} days. "
            f"First 5 dates: {dates[:5]}"
        ]
    return []


def check_volume_anomalies(
    volume: pd.Series,
    multiplier: float = 10.0,
) -> list[str]:
    """Flag volume > multiplier × rolling median — may indicate splits."""
    median_vol = volume.rolling(20, min_periods=10).median()
    ratio = volume / (median_vol + 1e-10)
    extreme = ratio > multiplier
    if extreme.any():
        return [f"Volume anomalies (>{multiplier:.0f}× median): {extreme.sum()} days"]
    return []


def check_zero_or_negative_prices(ohlcv: pd.DataFrame) -> list[str]:
    """Zero or negative prices are data errors."""
    issues = []
    for col in ["Open", "High", "Low", "Close"]:
        bad = (ohlcv[col] <= 0).sum()
        if bad > 0:
            issues.append(f"Zero/negative {col}: {bad} occurrences")
    return issues


def check_zero_volume_days(volume: pd.Series, max_pct: float = 0.05) -> list[str]:
    """Too many zero-volume days suggest illiquid or delisted stock."""
    zero_pct = (volume == 0).mean()
    if zero_pct > max_pct:
        return [
            f"Zero-volume days: {zero_pct * 100:.1f}% of history "
            f"(threshold {max_pct * 100:.0f}%). Stock may be illiquid."
        ]
    return []


def check_stale_prices(close: pd.Series, max_consecutive: int = 5) -> list[str]:
    """Detect consecutive identical close prices — sign of stale/frozen data."""
    unchanged = (close.diff().abs() < 1e-8).astype(int)
    # Rolling sum to detect runs
    runs = unchanged.rolling(max_consecutive, min_periods=max_consecutive).sum()
    if (runs >= max_consecutive).any():
        count = (runs >= max_consecutive).sum()
        return [
            f"Stale prices: {count} instances of {max_consecutive}+ "
            f"consecutive unchanged closes"
        ]
    return []


def check_date_gaps(ohlcv: pd.DataFrame, max_gap_days: int = 5) -> list[str]:
    """Detect large gaps in the date index (missing trading days)."""
    if not isinstance(ohlcv.index, pd.DatetimeIndex):
        return ["Warning: Index is not DatetimeIndex — cannot check date gaps"]
    diffs = ohlcv.index.to_series().diff().dt.days
    large_gaps = diffs[diffs > max_gap_days]
    if len(large_gaps) > 0:
        return [
            f"Date gaps >{max_gap_days} calendar days: {len(large_gaps)} gaps. "
            f"Largest: {large_gaps.max()} days"
        ]
    return []


def run_all_checks(
    ohlcv: pd.DataFrame,
    pe: pd.Series | None = None,
) -> dict:
    """
    Run all data quality checks. Returns a dict with issues list and pass/fail.

    Parameters
    ----------
    ohlcv : DataFrame with columns [Open, High, Low, Close, Volume]
    pe : Optional P/E ratio Series

    Returns
    -------
    dict with keys: issues (list[str]), is_clean (bool), n_rows (int)
    """
    issues: list[str] = []

    issues.extend(check_columns(ohlcv))
    if issues:
        return {"issues": issues, "is_clean": False, "n_rows": len(ohlcv)}

    issues.extend(check_ohlc_consistency(ohlcv))
    issues.extend(check_extreme_returns(ohlcv["Close"]))
    issues.extend(check_volume_anomalies(ohlcv["Volume"]))
    issues.extend(check_zero_or_negative_prices(ohlcv))
    issues.extend(check_zero_volume_days(ohlcv["Volume"]))
    issues.extend(check_stale_prices(ohlcv["Close"]))
    issues.extend(check_date_gaps(ohlcv))

    if pe is not None:
        neg_count = (pe < 0).sum()
        if neg_count > 0:
            issues.append(f"P/E has {neg_count} negative values — exclude from signals")
        extreme_count = (pe > 200).sum()
        if extreme_count > 0:
            issues.append(
                f"P/E has {extreme_count} extreme values (>200) — cap or exclude"
            )

    return {
        "issues": issues,
        "is_clean": len(issues) == 0,
        "n_rows": len(ohlcv),
    }
