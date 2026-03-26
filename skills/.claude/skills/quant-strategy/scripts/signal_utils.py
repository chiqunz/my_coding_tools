"""
Core indicator computation utilities for mid-term quantitative strategies.

All functions operate on daily OHLCV DataFrames and return pandas Series.
No intra-day data, tick data, or sub-daily granularity is used or assumed.

Dependencies: pandas, numpy (standard data stack only).
"""

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Price-based indicators
# ---------------------------------------------------------------------------


def sma(series: pd.Series, window: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window, min_periods=window).mean()


def ema(series: pd.Series, span: int) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=span, adjust=False).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index.

    Standard 14-period RSI. Values range 0-100.
    """
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    return 100 - 100 / (1 + rs)


def macd(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal_period: int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    MACD: returns (macd_line, signal_line, histogram).
    """
    fast_ema = ema(close, fast)
    slow_ema = ema(close, slow)
    macd_line = fast_ema - slow_ema
    signal_line = ema(macd_line, signal_period)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def bollinger_bands(
    close: pd.Series,
    window: int = 20,
    num_std: float = 2.0,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Bollinger Bands: returns (upper, middle, lower).
    """
    middle = sma(close, window)
    std = close.rolling(window, min_periods=window).std()
    upper = middle + num_std * std
    lower = middle - num_std * std
    return upper, middle, lower


def bollinger_width(
    close: pd.Series, window: int = 20, num_std: float = 2.0
) -> pd.Series:
    """Bollinger Band width as a fraction of the middle band."""
    upper, middle, lower = bollinger_bands(close, window, num_std)
    return (upper - lower) / (middle + 1e-10)


def atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    """Average True Range."""
    tr = true_range(high, low, close)
    return tr.rolling(period, min_periods=period).mean()


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """True Range (single-period)."""
    prev_close = close.shift(1)
    return pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)


def normalized_atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    """ATR divided by close price — percentage-based volatility."""
    return atr(high, low, close, period) / (close + 1e-10)


def roc(close: pd.Series, period: int = 21) -> pd.Series:
    """Rate of Change — percentage return over N periods."""
    return close / close.shift(period) - 1


def log_return(close: pd.Series, period: int = 1) -> pd.Series:
    """Log return over N periods."""
    return np.log(close / close.shift(period))


def stochastic_k(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    """Stochastic %K."""
    lowest = low.rolling(period, min_periods=period).min()
    highest = high.rolling(period, min_periods=period).max()
    return 100 * (close - lowest) / (highest - lowest + 1e-10)


def cci(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 20,
) -> pd.Series:
    """Commodity Channel Index."""
    tp = (high + low + close) / 3
    tp_sma = sma(tp, period)
    mean_dev = tp.rolling(period).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    return (tp - tp_sma) / (0.015 * mean_dev + 1e-10)


# ---------------------------------------------------------------------------
# Volume-based indicators
# ---------------------------------------------------------------------------


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On-Balance Volume."""
    direction = np.sign(close.diff())
    return (volume * direction).cumsum()


def volume_ratio(volume: pd.Series, window: int = 20) -> pd.Series:
    """Current volume divided by its N-day SMA."""
    return volume / (sma(volume, window) + 1e-10)


def relative_volume(volume: pd.Series, window: int = 20) -> pd.Series:
    """Current volume divided by its N-day median."""
    return volume / (volume.rolling(window).median() + 1e-10)


def mfi(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series,
    period: int = 14,
) -> pd.Series:
    """
    Money Flow Index — volume-weighted RSI.

    Values range 0-100.
    """
    tp = (high + low + close) / 3
    raw_mf = tp * volume
    tp_diff = tp.diff()
    pos_mf = (raw_mf * (tp_diff > 0).astype(float)).rolling(period).sum()
    neg_mf = (raw_mf * (tp_diff < 0).astype(float)).rolling(period).sum()
    mr = pos_mf / (neg_mf + 1e-10)
    return 100 - 100 / (1 + mr)


def ad_line(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series,
) -> pd.Series:
    """Accumulation/Distribution Line."""
    clv = ((close - low) - (high - close)) / (high - low + 1e-10)
    return (clv * volume).cumsum()


def volume_momentum(volume: pd.Series, fast: int = 5, slow: int = 20) -> pd.Series:
    """Ratio of short-term to long-term average volume — acceleration of interest."""
    return sma(volume, fast) / (sma(volume, slow) + 1e-10)


# ---------------------------------------------------------------------------
# OHLC structure indicators
# ---------------------------------------------------------------------------


def body_ratio(
    open_: pd.Series,
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
) -> pd.Series:
    """Absolute body size as fraction of total range — measures conviction."""
    return (close - open_).abs() / (high - low + 1e-10)


def close_location_value(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
) -> pd.Series:
    """Where close sits within the day's range (0 = at low, 1 = at high)."""
    return (close - low) / (high - low + 1e-10)


def gap(open_: pd.Series, close: pd.Series) -> pd.Series:
    """Overnight gap: today's open vs yesterday's close."""
    return open_ / close.shift(1) - 1


def daily_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """Daily range as percentage of close."""
    return (high - low) / (close + 1e-10)


# ---------------------------------------------------------------------------
# Valuation (P/E) utilities
# ---------------------------------------------------------------------------


def clean_pe(pe: pd.Series, max_pe: float = 200.0) -> pd.Series:
    """Remove non-sensical P/E values (negative earnings, extremes)."""
    cleaned = pe.copy()
    cleaned[cleaned <= 0] = np.nan
    cleaned[cleaned > max_pe] = np.nan
    return cleaned


def pe_rank(pe: pd.Series, max_pe: float = 200.0) -> pd.Series:
    """Cross-sectional percentile rank of P/E (lower rank = cheaper)."""
    return clean_pe(pe, max_pe).rank(pct=True)


def pe_zscore(pe: pd.Series, window: int = 252, max_pe: float = 200.0) -> pd.Series:
    """Time-series z-score of P/E over trailing window."""
    cleaned = clean_pe(pe, max_pe)
    mu = cleaned.rolling(window, min_periods=63).mean()
    sigma = cleaned.rolling(window, min_periods=63).std()
    return (cleaned - mu) / (sigma + 1e-10)


def earnings_yield(pe: pd.Series, max_pe: float = 200.0) -> pd.Series:
    """Earnings yield = 1 / P/E."""
    cleaned = clean_pe(pe, max_pe)
    return 1.0 / cleaned


# ---------------------------------------------------------------------------
# Rolling statistics helpers
# ---------------------------------------------------------------------------


def rolling_percentile(series: pd.Series, window: int = 126) -> pd.Series:
    """Rolling percentile of a series within its own trailing window."""
    return series.rolling(window, min_periods=max(window // 2, 20)).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
    )


def rolling_zscore(series: pd.Series, window: int = 63) -> pd.Series:
    """Rolling z-score of a series."""
    mu = series.rolling(window, min_periods=max(window // 2, 10)).mean()
    sigma = series.rolling(window, min_periods=max(window // 2, 10)).std()
    return (series - mu) / (sigma + 1e-10)
