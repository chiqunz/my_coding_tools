# Strategy Mining Report: Volume-Confirmed Price Momentum
**Date**: 2026-03-10
**Request**: Mine mid-term quantitative trading strategies combining volume analysis (VWAP, OBV) with price momentum indicators (RSI, MA crossovers) for high-probability entry/exit signals with volume confirmation.
**Data Constraint**: OHLCV + P/E only
**Holding Period Target**: Days to weeks (no intra-day trading)

---

## Strategy 1: Volume-Regime Momentum Composite (VRMC)

### Idea
This strategy identifies stocks entering a new momentum phase by requiring **three independent confirmations**: (1) a moving average crossover signals a trend shift, (2) OBV slope confirms institutional accumulation/distribution is aligned with price, and (3) RSI occupies the "thrust zone" (50-70 for longs, 30-50 for shorts) indicating momentum without exhaustion. The key insight is that volume-confirmed trend initiations have significantly higher follow-through rates than price-only signals, because institutional accumulation leaves a volume footprint that precedes the full price move.

### Behavioral / Structural Rationale
- **Why this pattern exists**: Large institutions build positions over days to weeks, creating a detectable OBV divergence before the full price move materializes. Information diffuses slowly across market participants — fundamental analysts, technical traders, and index funds react at different speeds. The MA crossover captures the *middle* of this diffusion process, after early movers have acted but before the crowd piles in.
- **Who is on the wrong side**: (1) Anchored investors who dismiss early price moves as noise and wait too long to enter, (2) late contrarians who short the crossover expecting mean reversion but fight institutional flow, (3) fund managers constrained by mandates who must wait for "confirmation" from committees before acting.
- **Academic/empirical support**: Jegadeesh & Titman (1993) documented momentum profits at 3-12 month horizons. Gervais, Kaniel & Mingelgrin (2001) showed that volume contains information about future returns beyond price. Loh (2010) demonstrated that high-volume price changes predict stronger continuation than low-volume changes.

### Signal Logic
- **Indicators used**:
  - EMA(20) and EMA(50) — *Trend Direction* category (crossover detection)
  - OBV 20-day slope — *Volume Flow* category (institutional accumulation)
  - RSI(14) — *Overbought/Oversold* category (momentum state without exhaustion)
- **Signal formula**:
  ```
  trend_signal = sign(EMA(20) - EMA(50))
  obv_slope = linear_regression_slope(OBV, 20 days), normalized by OBV std
  rsi_thrust = 1 if (RSI > 50 and RSI < 70) else (-1 if RSI < 50 and RSI > 30 else 0)

  composite_score = trend_signal × (0.4 × |obv_slope_zscore| + 0.3 × rsi_alignment + 0.3)

  Where:
  - obv_slope_zscore = (current OBV slope - rolling 60d mean slope) / rolling 60d std slope
  - rsi_alignment = 1 if trend_signal and rsi_thrust agree, else 0
  ```
- **Parameters (4 tunable)**:
  1. `ema_fast` = 20 (fast EMA period)
  2. `ema_slow` = 50 (slow EMA period)
  3. `obv_slope_window` = 20 (OBV slope lookback)
  4. `rsi_period` = 14 (RSI lookback)
- **Entry rule**: Go LONG when:
  - EMA(20) crosses above EMA(50) within the last 5 bars, AND
  - OBV 20-day slope z-score > 0.5 (volume accumulation above average), AND
  - RSI is between 50 and 70 (momentum thrust zone, not overbought)
- **Exit rule**: Close LONG when ANY of:
  - EMA(20) crosses below EMA(50), OR
  - RSI > 75 (overbought exhaustion), OR
  - OBV slope z-score turns negative (volume distribution)
  - **Time stop**: Close after 40 trading days if none of the above trigger
- **Holding period**: 2-8 weeks typical
- **Rebalance frequency**: Daily signal evaluation, but buffered entry/exit (see code)

### Position Sizing & Risk Management
- **Position size**: Equal-weight across all open positions, max 10 positions
- **Risk per trade**: 2% of portfolio per position, using ATR(14)-based stops
- **Stop-loss**: Entry price - 2.5 × ATR(14). Trail stop at entry price once position is +1.5 × ATR(14) in profit
- **Max portfolio exposure**: 80% long, 80% short (or 100% long-only)
- **Correlation filter**: Avoid opening >3 positions in the same sector

### Implementation Steps
1. Compute EMA(20) and EMA(50) for each stock in the universe
2. Detect crossover events: EMA(20) crossed above EMA(50) within the last 5 bars
3. Compute OBV series, then calculate the 20-day linear regression slope of OBV
4. Normalize OBV slope using a 60-day expanding z-score (avoid lookahead)
5. Compute RSI(14) and check that it falls in the thrust zone [50, 70]
6. Generate composite score for stocks meeting all three conditions
7. Rank qualifying stocks by composite score; select top N for entry
8. Apply ATR-based stop-loss and trail-stop rules for risk management
9. Monitor exit conditions daily; close positions when any exit trigger fires

### Example Python Code

```python
import pandas as pd
import numpy as np


def vrmc_signal(
    ohlcv: pd.DataFrame,
    pe: pd.Series | None = None,
    ema_fast: int = 20,
    ema_slow: int = 50,
    obv_slope_window: int = 20,
    rsi_period: int = 14,
) -> pd.Series:
    """
    Volume-Regime Momentum Composite (VRMC)

    Combines EMA crossover (trend), OBV slope (volume confirmation),
    and RSI thrust zone (momentum without exhaustion) into a single
    composite signal for mid-term momentum entries.

    Behavioral rationale: Institutional accumulation creates detectable
    OBV trends before full price realization. MA crossovers capture
    the middle of the information diffusion process. RSI thrust zone
    filters out exhausted moves.

    Holding period: 2-8 weeks
    Data required: OHLCV (P/E optional for filtering)

    Parameters
    ----------
    ohlcv : DataFrame with columns [Open, High, Low, Close, Volume]
    pe : Optional P/E ratio series (used as safety filter if provided)
    ema_fast : Fast EMA period (default 20)
    ema_slow : Slow EMA period (default 50)
    obv_slope_window : Window for OBV slope calculation (default 20)
    rsi_period : RSI calculation period (default 14)

    Returns
    -------
    Series of signal values: positive = bullish, negative = bearish,
    magnitude indicates conviction. Range approximately [-2, +2].
    """
    close = ohlcv['Close']
    volume = ohlcv['Volume']

    # --- 1. Trend Direction: EMA crossover ---
    ema_f = close.ewm(span=ema_fast, adjust=False).mean()
    ema_s = close.ewm(span=ema_slow, adjust=False).mean()
    trend_signal = np.sign(ema_f - ema_s)

    # Detect recent crossovers (within last 5 bars)
    prev_trend = trend_signal.shift(5)
    is_fresh_crossover = (trend_signal != prev_trend) & (trend_signal != 0)

    # --- 2. Volume Flow: OBV slope z-score ---
    # Compute On-Balance Volume
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()

    # Rolling linear regression slope of OBV (vectorized for performance)
    def rolling_slope_vectorized(series, window):
        """
        Compute rolling linear regression slope using fully vectorized operations.
        Formula: slope = (n*sum(x*y) - sum(x)*sum(y)) / (n*sum(x^2) - sum(x)^2)
        where x = 0, 1, ..., n-1 for each window.

        Key insight: sum(x*y) for rolling windows can be computed as:
        sum(i * y_{t-n+1+i}) = sum(i * y_{t-n+1+i}) for i in 0..n-1
        This is equivalent to: n * rolling_mean(y * position_weight) but we use
        the weighted rolling sum trick instead.
        """
        n = window
        x = np.arange(n, dtype=float)
        sum_x = x.sum()             # n*(n-1)/2
        sum_x2 = (x ** 2).sum()     # n*(n-1)*(2n-1)/6
        denom = n * sum_x2 - sum_x ** 2

        rolling_sum_y = series.rolling(n).sum()

        # For sum(x*y), use: sum(x*y) = (n-1)*y_t + (n-2)*y_{t-1} + ...
        # = (n-1)*sum(y) - cumulative_trick
        # Simpler: use .rolling().apply() with numpy for correctness
        rolling_sum_xy = series.rolling(n).apply(
            lambda vals: np.dot(x, vals), raw=True
        )

        slope = (n * rolling_sum_xy - sum_x * rolling_sum_y) / denom
        return slope

    obv_slope = rolling_slope_vectorized(obv, obv_slope_window)

    # Z-score of OBV slope (expanding window to avoid lookahead)
    obv_slope_mean = obv_slope.expanding(min_periods=60).mean()
    obv_slope_std = obv_slope.expanding(min_periods=60).std()
    obv_slope_z = (obv_slope - obv_slope_mean) / obv_slope_std.replace(0, np.nan)

    # --- 3. Overbought/Oversold: RSI thrust zone ---
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/rsi_period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/rsi_period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    # RSI alignment with trend
    rsi_bull_thrust = ((rsi > 50) & (rsi < 70)).astype(float)
    rsi_bear_thrust = ((rsi < 50) & (rsi > 30)).astype(float)
    rsi_alignment = np.where(
        trend_signal > 0, rsi_bull_thrust,
        np.where(trend_signal < 0, rsi_bear_thrust, 0)
    )

    # --- 4. Composite Signal ---
    # Volume confirmation strength
    vol_confirm = obv_slope_z.clip(-2, 2).abs() / 2  # Normalize to [0, 1]
    vol_direction_match = np.sign(obv_slope_z) == trend_signal

    composite = (
        trend_signal *
        (0.4 * vol_confirm * vol_direction_match.astype(float) +
         0.3 * rsi_alignment +
         0.3 * is_fresh_crossover.astype(float))
    )

    # --- 5. P/E safety filter (optional) ---
    if pe is not None:
        pe_valid = (pe > 0) & (pe < 200)
        composite = composite.where(pe_valid, 0)

    # Shift by 1: compute signal at close, trade at NEXT open (no lookahead)
    composite = composite.shift(1).fillna(0)

    return composite


def vrmc_positions_with_risk(
    ohlcv: pd.DataFrame,
    signal: pd.Series,
    atr_period: int = 14,
    atr_stop_mult: float = 2.5,
    max_hold_days: int = 40,
) -> pd.DataFrame:
    """
    Convert VRMC signal into positions with ATR-based risk management.

    Returns DataFrame with columns: position, stop_loss, entry_price
    """
    close = ohlcv['Close']
    high = ohlcv['High']
    low = ohlcv['Low']

    # ATR for position sizing and stops
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(atr_period).mean()

    positions = pd.Series(0.0, index=signal.index)
    stop_loss = pd.Series(np.nan, index=signal.index)
    entry_prices = pd.Series(np.nan, index=signal.index)

    current_pos = 0
    current_stop = np.nan
    current_entry = np.nan
    days_held = 0

    for i in range(1, len(signal)):
        if current_pos == 0:
            # Entry logic
            if signal.iloc[i] > 0.3:  # Minimum conviction threshold
                current_pos = 1
                current_entry = close.iloc[i]
                current_stop = current_entry - atr_stop_mult * atr.iloc[i]
                days_held = 0
            elif signal.iloc[i] < -0.3:
                current_pos = -1
                current_entry = close.iloc[i]
                current_stop = current_entry + atr_stop_mult * atr.iloc[i]
                days_held = 0
        else:
            days_held += 1
            # Trail stop for profitable positions
            if current_pos > 0:
                profit_atr = (close.iloc[i] - current_entry) / atr.iloc[i]
                if profit_atr > 1.5:
                    current_stop = max(current_stop, current_entry)
                # Exit conditions
                if (close.iloc[i] < current_stop or
                    signal.iloc[i] < -0.1 or
                    days_held >= max_hold_days):
                    current_pos = 0
            elif current_pos < 0:
                profit_atr = (current_entry - close.iloc[i]) / atr.iloc[i]
                if profit_atr > 1.5:
                    current_stop = min(current_stop, current_entry)
                if (close.iloc[i] > current_stop or
                    signal.iloc[i] > 0.1 or
                    days_held >= max_hold_days):
                    current_pos = 0

        positions.iloc[i] = current_pos
        stop_loss.iloc[i] = current_stop
        entry_prices.iloc[i] = current_entry

    return pd.DataFrame({
        'position': positions,
        'stop_loss': stop_loss,
        'entry_price': entry_prices
    })
```

### Reasoning & Edge Assessment
- **Why this might work**:
  - Three independent information sources (trend, volume, momentum state) from different indicator categories reduce false positive rate significantly
  - OBV slope captures institutional flow that takes days/weeks to complete — by the time the MA crosses, the volume footprint is already established, providing genuine confirmation rather than redundant information
  - RSI thrust zone (50-70) is a non-standard filter that avoids the crowded "RSI < 30 buy" signal; instead it selects for accelerating momentum before exhaustion
- **Why this might fail**:
  - In choppy/range-bound markets (e.g., 2011, 2015), MA crossovers whipsaw frequently and OBV slope oscillates without clear direction — all three conditions rarely align, producing very few signals (low opportunity cost but also low returns)
  - The 5-bar freshness requirement for crossovers may be too tight in slow-moving markets, missing gradual trend shifts
  - In flash crashes or gap-down events, the ATR-based stop may gap through, causing larger-than-expected losses
- **Key risks**: Regime dependency (struggles in range-bound markets), gap risk on overnight events, parameter sensitivity of OBV slope z-score threshold
- **Estimated robustness**: Should survive ±20% parameter changes since it uses standard values (EMA 20/50, RSI 14) and the signal requires agreement across all three indicators. Cross-market applicability is moderate — works best in liquid equity markets with sufficient volume data.

### Viability Scorecard
| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| Behavioral rationale strength | 8 | Strong: institutional flow + information diffusion well-documented |
| Simplicity (fewer params = higher) | 7 | 4 parameters, all standard values |
| Indicator diversity | 9 | Trend (Cat 2) + Volume Flow (Cat 5) + OB/OS (Cat 1) |
| Crowding resistance | 7 | MA crossover is common, but OBV slope + RSI thrust zone are non-standard filters |
| Volume confirmation | 9 | OBV slope z-score is core to the signal, not an afterthought |
| Regime robustness | 5 | Momentum strategy — struggles in choppy/bear regimes |
| **Overall** | **7.5** | |

---

## Strategy 2: Volume Climax Exhaustion Reversal (VCER)

### Idea
This strategy detects **selling exhaustion events** — days where abnormally high volume coincides with sharp price decline and RSI extremes — as precursors to mean-reverting bounces. The key insight is that volume climaxes at price lows often represent forced selling (margin calls, fund redemptions, stop-loss cascading) rather than rational repricing. Once the forced sellers are flushed out, the stock rebounds as the selling pressure evaporates. A P/E floor filter ensures we're buying panic in fundamentally viable companies, not catching falling knives of genuinely impaired businesses.

### Behavioral / Structural Rationale
- **Why this pattern exists**: Three structural frictions converge at volume climax lows: (1) **Margin calls** force leveraged holders to sell regardless of price, creating artificial supply, (2) **Stop-loss cascading** — when price breaks key support levels, clustered stops trigger simultaneous selling that exaggerates the move, (3) **Fund redemptions** during market stress force even good stocks to be liquidated for cash. Once these forced sellers finish, the oversupply disappears and price recovers.
- **Who is on the wrong side**: Panic sellers driven by loss aversion, margin-called leveraged traders who must sell, and late shorts who pile on after the big move. These participants sell for *non-informational* reasons — their trades create temporary mispricing.
- **Academic/empirical support**: Campbell, Grossman & Wang (1993) showed that high-volume declines in stocks with mean-reverting activity are followed by reversals. Kaniel et al. (2008) documented that retail selling pressure creates temporary mispricing. The disposition effect (Shefrin & Statman, 1985) shows that loss aversion causes predictable selling behavior at pain points.

### Signal Logic
- **Indicators used**:
  - Relative Volume (Volume / SMA(Volume, 20)) — *Volume Flow* category
  - RSI(14) — *Overbought/Oversold* category
  - ATR(14) ratio (Today's True Range / ATR(14)) — *Volatility* category
  - P/E ratio (optional safety filter) — *Valuation* category
- **Signal formula**:
  ```
  volume_climax = (Volume / SMA(Volume, 20)) > 2.5
  price_decline = Daily return < -2% (or close < open AND body_ratio > 0.6)
  rsi_oversold = RSI(14) < 30
  range_expansion = True_Range / ATR(14) > 1.8

  exhaustion_signal = volume_climax AND price_decline AND rsi_oversold AND range_expansion

  signal_strength = relative_volume × (30 - RSI) / 30 × tr_ratio
  ```
- **Parameters (4 tunable)**:
  1. `rel_vol_threshold` = 2.5 (relative volume threshold for "climax")
  2. `rsi_oversold` = 30 (RSI oversold level)
  3. `tr_expansion` = 1.8 (True Range / ATR threshold)
  4. `pe_max` = 50 (maximum P/E for safety filter)
- **Entry rule**: Go LONG on the NEXT OPEN after all four conditions fire simultaneously:
  - Relative volume > 2.5× (volume climax)
  - Close-to-close return < -2% (price decline)
  - RSI(14) < 30 (oversold)
  - True Range / ATR(14) > 1.8 (range expansion = panic volatility)
  - P/E between 5 and 50 (fundamentally reasonable — optional)
- **Exit rule**: Close LONG when FIRST of:
  - RSI(14) > 55 (momentum recovered to neutral), OR
  - 15 trading days elapsed (time-based exit), OR
  - Price drops below entry - 1.5 × ATR(14) at entry (hard stop-loss)
- **Holding period**: 5-15 trading days (1-3 weeks)
- **Rebalance frequency**: Signal-based (event-driven entry, rule-based exit)

### Position Sizing & Risk Management
- **Position size**: Risk-based sizing — risk 1.5% of portfolio per trade, size = (1.5% × Portfolio) / (1.5 × ATR)
- **Max simultaneous positions**: 5 (climax events tend to cluster during market stress)
- **Correlation rule**: During broad market selloffs (>3 simultaneous signals), reduce position size by 50% to manage systemic risk
- **Hard stop**: Entry price - 1.5 × ATR(14). No trailing stop — this is a time-bounded mean reversion.
- **Profit target**: None explicit — RSI recovery to 55 or time exit handles profit-taking

### Implementation Steps
1. Compute rolling 20-day SMA of Volume; calculate relative volume ratio each day
2. Compute RSI(14) from daily close prices
3. Compute ATR(14) and daily True Range; calculate TR/ATR ratio
4. Identify "climax days": relative volume > 2.5 AND daily return < -2% AND RSI < 30 AND TR/ATR > 1.8
5. If P/E is available, filter to stocks with P/E between 5 and 50
6. On climax day signal, compute signal strength for ranking (when multiple signals fire)
7. Enter LONG at next day's open price
8. Monitor exit conditions: RSI recovery > 55, time limit (15 days), or stop-loss hit
9. Track max concurrent positions and apply correlation-based sizing adjustment

### Example Python Code

```python
import pandas as pd
import numpy as np


def vcer_signal(
    ohlcv: pd.DataFrame,
    pe: pd.Series | None = None,
    rel_vol_threshold: float = 2.5,
    rsi_oversold: int = 30,
    tr_expansion: float = 1.8,
    pe_max: float = 50.0,
) -> pd.Series:
    """
    Volume Climax Exhaustion Reversal (VCER)

    Detects selling exhaustion events where abnormally high volume meets
    sharp price decline and RSI extremes. These events often represent
    forced selling rather than rational repricing, creating mean-reversion
    opportunities.

    Behavioral rationale: Margin calls, stop-loss cascading, and fund
    redemptions create artificial selling pressure. Once forced sellers
    finish, price rebounds.

    Holding period: 5-15 trading days (1-3 weeks)
    Data required: OHLCV + P/E (optional)

    Parameters
    ----------
    ohlcv : DataFrame with columns [Open, High, Low, Close, Volume]
    pe : Optional P/E ratio series for fundamental safety filter
    rel_vol_threshold : Minimum volume/avg_volume ratio for "climax" (default 2.5)
    rsi_oversold : RSI level for oversold condition (default 30)
    tr_expansion : Minimum True Range/ATR ratio for range expansion (default 1.8)
    pe_max : Maximum P/E for safety filter (default 50)

    Returns
    -------
    Series of signal values: positive values indicate exhaustion reversal
    opportunity, with magnitude proportional to conviction. Zero = no signal.
    """
    close = ohlcv['Close']
    high = ohlcv['High']
    low = ohlcv['Low']
    volume = ohlcv['Volume']

    # --- 1. Volume Climax Detection ---
    vol_sma = volume.rolling(20).mean()
    rel_vol = volume / vol_sma.replace(0, np.nan)
    is_volume_climax = rel_vol > rel_vol_threshold

    # --- 2. Price Decline ---
    daily_return = close.pct_change()
    is_price_decline = daily_return < -0.02  # >2% decline

    # --- 3. RSI Oversold ---
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    is_oversold = rsi < rsi_oversold

    # --- 4. Range Expansion (Volatility) ---
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    tr_ratio = tr / atr.replace(0, np.nan)
    is_range_expansion = tr_ratio > tr_expansion

    # --- 5. Combine: All conditions must fire simultaneously ---
    is_exhaustion = (
        is_volume_climax &
        is_price_decline &
        is_oversold &
        is_range_expansion
    )

    # Signal strength: proportional to extremity
    signal_strength = (
        (rel_vol / rel_vol_threshold).clip(0, 3) *  # Volume intensity
        ((rsi_oversold - rsi).clip(0, 30) / 30) *   # RSI depth below threshold
        (tr_ratio / tr_expansion).clip(0, 2)          # Range expansion intensity
    )

    signal = signal_strength.where(is_exhaustion, 0.0)

    # --- 6. P/E Safety Filter ---
    if pe is not None:
        pe_valid = (pe > 5) & (pe < pe_max)
        signal = signal.where(pe_valid, 0.0)

    # Shift by 1 to trade at NEXT open (no lookahead)
    signal = signal.shift(1).fillna(0)

    return signal


def vcer_backtest_positions(
    ohlcv: pd.DataFrame,
    signal: pd.Series,
    rsi_exit: float = 55.0,
    max_hold_days: int = 15,
    stop_atr_mult: float = 1.5,
) -> pd.DataFrame:
    """
    Convert VCER signal into positions with time-based and RSI-based exits.

    This function processes a single stock's signal. For portfolio-level
    position limits (max 5 simultaneous), apply externally by tracking
    active positions across all stocks in the universe.

    Returns DataFrame with columns: position, exit_reason
    """
    close = ohlcv['Close']
    high = ohlcv['High']
    low = ohlcv['Low']

    # Recompute RSI for exit
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    # ATR for stop-loss
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()

    positions = pd.Series(0.0, index=signal.index)
    exit_reasons = pd.Series('', index=signal.index)

    current_pos = 0
    entry_price = np.nan
    stop_price = np.nan
    days_held = 0

    for i in range(1, len(signal)):
        if current_pos == 0:
            if signal.iloc[i] > 0:
                current_pos = 1
                entry_price = close.iloc[i]
                stop_price = entry_price - stop_atr_mult * atr.iloc[i]
                days_held = 0
        else:
            days_held += 1
            # Exit conditions
            if rsi.iloc[i] > rsi_exit:
                current_pos = 0
                exit_reasons.iloc[i] = 'rsi_recovery'
            elif days_held >= max_hold_days:
                current_pos = 0
                exit_reasons.iloc[i] = 'time_exit'
            elif close.iloc[i] < stop_price:
                current_pos = 0
                exit_reasons.iloc[i] = 'stop_loss'

        positions.iloc[i] = current_pos

    return pd.DataFrame({
        'position': positions,
        'exit_reason': exit_reasons
    })
```

### Reasoning & Edge Assessment
- **Why this might work**:
  - Volume climaxes at lows are structurally driven by non-informational selling (margin calls, forced liquidation) creating temporary oversupply — the fundamental picture hasn't changed
  - Four simultaneous conditions (volume, price, RSI, range) are extremely selective — false positive rate is very low because coincidence of all four is rare
  - P/E filter prevents buying into genuinely distressed companies (the "falling knife" problem)
- **Why this might fail**:
  - During systemic bear markets (2008, 2022), what looks like exhaustion is often just the beginning of a larger decline — the signal fires early and repeatedly as the stock continues falling
  - Survivorship bias in backtests inflates mean-reversion returns because delisted stocks (which had volume climaxes before going to zero) are excluded
  - Signal fires very rarely (~5-15 times per year per stock universe), making the strategy difficult to implement as a standalone system
- **Key risks**: Regime risk in bear markets (severe), survivorship bias, low signal frequency, systemic risk concentration (signals cluster during market stress)
- **Estimated robustness**: Parameters are set at natural "knee" points (2.5× volume is clearly abnormal, RSI 30 is standard oversold). Should survive ±20% parameter changes well. Cross-market: works better in large-cap liquid markets where volume data is reliable.

### Viability Scorecard
| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| Behavioral rationale strength | 9 | Forced selling + loss aversion is one of the strongest behavioral edges |
| Simplicity (fewer params = higher) | 7 | 4 parameters, all with natural interpretations |
| Indicator diversity | 9 | Volume Flow (Cat 5) + OB/OS (Cat 1) + Volatility (Cat 4) + Valuation (Cat 7) |
| Crowding resistance | 7 | "Buy the dip" is common, but 4-condition simultaneous filter is rare |
| Volume confirmation | 10 | Volume climax IS the primary signal — maximum confirmation |
| Regime robustness | 4 | Dangerous in bear markets — mean reversion fails during capitulation |
| **Overall** | **7.7** | |

---

## Strategy 3: OBV-Price Divergence Anticipation Engine (OPDAE)

### Idea
This strategy exploits the **slow diffusion of information** by detecting sustained divergences between On-Balance Volume (OBV) trend and price trend. When OBV rises for 15+ days while price remains flat or declines, it signals stealth accumulation by informed players (institutions, corporate insiders acting through intermediaries). The strategy waits for this divergence to build, then enters when price begins to confirm the OBV signal with a VWAP reclaim. This "divergence + trigger" approach provides both direction (from OBV) and timing (from the VWAP breakout).

### Behavioral / Structural Rationale
- **Why this pattern exists**: Large institutional orders are broken into small lots and executed over weeks to minimize market impact. This creates a detectable footprint: each up-close day has higher volume than each down-close day, causing OBV to rise even as price moves sideways. The full price adjustment doesn't happen until a catalyst forces the broader market to notice — at which point the stock "breaks out" on high volume. This is the classic information asymmetry pattern documented in Kyle (1985).
- **Who is on the wrong side**: (1) Retail traders who see a "boring, flat stock" and ignore it, (2) Short sellers who target flat/declining stocks without noticing the volume accumulation pattern, (3) Passive index investors who only react to price changes, not volume.
- **Academic/empirical support**: Blume, Easley & O'Hara (1994) showed that volume contains information about future prices beyond what's in price history alone. Chordia & Swaminathan (2000) documented that high-volume stocks lead low-volume stocks, suggesting volume carries informational content. The OBV concept itself (Granville, 1963) captures the idea that volume precedes price.

### Signal Logic
- **Indicators used**:
  - OBV 20-day EMA slope — *Volume Flow* category (accumulation detection)
  - Close relative to 20-day VWAP — *Trend Direction* category (price confirmation trigger)
  - Close location value (C - L) / (H - L) — *OHLC Structure* category (buying conviction)
- **Signal formula**:
  ```
  # Phase 1: Detect divergence (OBV rising, price flat/declining)
  obv_ema = EMA(OBV, 20)
  obv_trend = sign(obv_ema - obv_ema.shift(15))  # +1 if OBV trending up over 15 days
  price_trend = sign(Close - Close.shift(15))      # +1 if price trending up over 15 days

  bullish_divergence = (obv_trend > 0) AND (price_trend <= 0)  # OBV up, price flat/down
  bearish_divergence = (obv_trend < 0) AND (price_trend >= 0)  # OBV down, price flat/up

  # Phase 2: VWAP trigger (price confirms volume's direction)
  vwap_20 = cumulative_sum(Close × Volume, 20) / cumulative_sum(Volume, 20)
  price_reclaims_vwap = Close > vwap_20 AND Close.shift(1) <= vwap_20.shift(1)

  # Phase 3: Close location filter (buying conviction)
  close_location = (Close - Low) / (High - Low)
  strong_close = close_location > 0.7  # Closes near the high

  # Full signal
  long_signal = bullish_divergence AND price_reclaims_vwap AND strong_close
  ```
- **Parameters (4 tunable)**:
  1. `obv_ema_span` = 20 (OBV smoothing period)
  2. `divergence_lookback` = 15 (days to measure divergence)
  3. `vwap_period` = 20 (rolling VWAP period)
  4. `close_location_min` = 0.7 (minimum close location for conviction)
- **Entry rule**: Go LONG at next open when:
  - OBV EMA has risen over the last 15 days, AND
  - Price has NOT risen over the last 15 days (flat or down), AND
  - Close crosses above 20-day rolling VWAP (price confirmation), AND
  - Close location value > 0.7 (closes in the top 30% of daily range = buying conviction)
- **Exit rule**: Close LONG when FIRST of:
  - OBV EMA slope turns negative (accumulation stops), OR
  - Close falls below 20-day VWAP by more than 1× ATR(14) (trend failure), OR
  - 30 trading days elapsed (time stop)
- **Holding period**: 2-6 weeks typical
- **Rebalance frequency**: Daily signal evaluation, signal-based entry, rule-based exit

### Position Sizing & Risk Management
- **Position size**: 2% risk per trade, sized by ATR: shares = (0.02 × Portfolio) / (1.5 × ATR(14))
- **Max positions**: 8 concurrent
- **Stop-loss**: VWAP(20) - 1.0 × ATR(14). Dynamic — adjusts with VWAP.
- **Scaling in**: If divergence persists and signal fires again after 10+ days, add half a position at the new signal price
- **No averaging down**: If stopped out, must wait for a fresh divergence cycle

### Implementation Steps
1. Compute OBV series from daily close and volume
2. Apply EMA(20) smoothing to OBV; compute its 15-day directional trend
3. Compute 15-day price directional trend from close prices
4. Identify bullish divergences: OBV trend positive + price trend non-positive
5. Compute 20-day rolling VWAP = sum(Close × Volume, 20) / sum(Volume, 20)
6. Detect VWAP reclaim: today close > VWAP AND yesterday close <= VWAP
7. Compute close location value = (Close - Low) / (High - Low)
8. Generate entry signal when divergence + VWAP reclaim + close location > 0.7
9. Apply shift(1) to signal to trade at next open (avoid lookahead)
10. Monitor exit conditions: OBV slope reversal, VWAP breakdown, or time limit

### Example Python Code

```python
import pandas as pd
import numpy as np


def opdae_signal(
    ohlcv: pd.DataFrame,
    pe: pd.Series | None = None,
    obv_ema_span: int = 20,
    divergence_lookback: int = 15,
    vwap_period: int = 20,
    close_location_min: float = 0.7,
) -> pd.Series:
    """
    OBV-Price Divergence Anticipation Engine (OPDAE)

    Detects stealth institutional accumulation via OBV-price divergence,
    then times entry using VWAP reclaim + close location conviction filter.

    Behavioral rationale: Institutions split large orders over weeks,
    creating OBV trends before price moves. The VWAP reclaim signals
    the start of broader market recognition.

    Holding period: 2-6 weeks
    Data required: OHLCV + P/E (optional)

    Parameters
    ----------
    ohlcv : DataFrame with columns [Open, High, Low, Close, Volume]
    pe : Optional P/E ratio series for fundamental safety filter
    obv_ema_span : EMA period for OBV smoothing (default 20)
    divergence_lookback : Days to measure divergence (default 15)
    vwap_period : Rolling VWAP period (default 20)
    close_location_min : Min close location for conviction (default 0.7)

    Returns
    -------
    Series of signal values: positive = bullish divergence with
    price confirmation. Magnitude indicates conviction strength.
    """
    close = ohlcv['Close']
    high = ohlcv['High']
    low = ohlcv['Low']
    volume = ohlcv['Volume']

    # --- 1. On-Balance Volume with EMA smoothing ---
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
    obv_ema = obv.ewm(span=obv_ema_span, adjust=False).mean()

    # OBV trend: direction over lookback period
    obv_direction = np.sign(obv_ema - obv_ema.shift(divergence_lookback))

    # OBV trend strength: magnitude of change relative to volume
    obv_change = (obv_ema - obv_ema.shift(divergence_lookback)).abs()
    obv_change_normalized = obv_change / volume.rolling(divergence_lookback).sum()

    # --- 2. Price trend over same period ---
    price_return = close.pct_change(divergence_lookback)

    # --- 3. Divergence detection ---
    # Bullish: OBV rising, price flat or declining
    bullish_div = (obv_direction > 0) & (price_return <= 0.02)
    # Bearish: OBV declining, price flat or rising
    bearish_div = (obv_direction < 0) & (price_return >= -0.02)

    # --- 4. Rolling VWAP as trigger ---
    typical_price = close  # Using close for simplicity; (H+L+C)/3 also valid
    vwap = (
        (typical_price * volume).rolling(vwap_period).sum() /
        volume.rolling(vwap_period).sum()
    )

    # VWAP reclaim: close crosses above VWAP
    vwap_reclaim = (close > vwap) & (close.shift(1) <= vwap.shift(1))
    # VWAP breakdown: close crosses below VWAP
    vwap_breakdown = (close < vwap) & (close.shift(1) >= vwap.shift(1))

    # --- 5. Close location (OHLC structure conviction) ---
    daily_range = high - low
    close_location = (close - low) / daily_range.replace(0, np.nan)
    strong_close = close_location > close_location_min

    # --- 6. Composite signal ---
    # Bullish signal: divergence + VWAP reclaim + strong close
    long_signal = (bullish_div & vwap_reclaim & strong_close).astype(float)

    # Short signal: bearish divergence + VWAP breakdown + weak close
    weak_close = close_location < (1 - close_location_min)
    short_signal = (bearish_div & vwap_breakdown & weak_close).astype(float)

    # Conviction scaling
    signal = long_signal * obv_change_normalized.clip(0, 1) - \
             short_signal * obv_change_normalized.clip(0, 1)

    # --- 7. P/E filter (optional) ---
    if pe is not None:
        pe_valid = (pe > 0) & (pe < 150)
        signal = signal.where(pe_valid, 0.0)

    # Shift by 1: trade at next open
    signal = signal.shift(1).fillna(0)

    return signal


def opdae_positions(
    ohlcv: pd.DataFrame,
    signal: pd.Series,
    max_hold_days: int = 30,
    vwap_period: int = 20,
) -> pd.DataFrame:
    """
    Convert OPDAE signal to positions with VWAP-based stop and time exit.
    """
    close = ohlcv['Close']
    volume = ohlcv['Volume']

    # VWAP for dynamic stop
    vwap = (close * volume).rolling(vwap_period).sum() / \
           volume.rolling(vwap_period).sum()

    # ATR for stop buffer
    high = ohlcv['High']
    low = ohlcv['Low']
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()

    # OBV for exit monitoring
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
    obv_ema = obv.ewm(span=20, adjust=False).mean()
    obv_slope = obv_ema.diff(5)  # 5-day OBV slope

    positions = pd.Series(0.0, index=signal.index)
    current_pos = 0
    days_held = 0

    for i in range(1, len(signal)):
        if current_pos == 0:
            if signal.iloc[i] > 0:
                current_pos = 1
                days_held = 0
            elif signal.iloc[i] < 0:
                current_pos = -1
                days_held = 0
        else:
            days_held += 1
            if current_pos > 0:
                # Exit: OBV slope turns negative, VWAP breakdown, or time
                stop_level = vwap.iloc[i] - 1.0 * atr.iloc[i]
                if (obv_slope.iloc[i] < 0 or
                    close.iloc[i] < stop_level or
                    days_held >= max_hold_days):
                    current_pos = 0
            elif current_pos < 0:
                stop_level = vwap.iloc[i] + 1.0 * atr.iloc[i]
                if (obv_slope.iloc[i] > 0 or
                    close.iloc[i] > stop_level or
                    days_held >= max_hold_days):
                    current_pos = 0

        positions.iloc[i] = current_pos

    return pd.DataFrame({'position': positions})
```

### Reasoning & Edge Assessment
- **Why this might work**:
  - OBV-price divergence has genuine theoretical backing — Kyle (1985) model shows informed traders leave volume footprints. This is not a narrative fallacy; it's a mathematically demonstrable consequence of informed trading
  - The "divergence + trigger" pattern (Pattern D from methodology) provides both direction (OBV) AND timing (VWAP reclaim) — pure divergence strategies suffer from the "being early = being wrong" problem, but the VWAP trigger solves this
  - Close location filter adds a third, independent confirmation from a different indicator category (OHLC Structure), reducing false positives from random VWAP crossings
- **Why this might fail**:
  - Not all OBV divergences represent institutional accumulation — some are driven by short covering (which looks the same in volume data) or retail dip-buying that runs out of steam
  - In highly efficient, liquid large-caps, the OBV divergence may be too small to detect reliably because institutions use dark pools and algorithmic execution to minimize their volume footprint
  - Bearish divergences (OBV declining while price rises) are less reliable because distribution can happen gradually without strong OBV signals — unlike accumulation, selling by institutions is often spread more evenly
- **Key risks**: False divergences from noise, signal rarity (divergence + VWAP reclaim + close location is rare), latency in detecting institutional flow in highly liquid markets, OBV sensitivity to data quality
- **Estimated robustness**: Parameters are structurally motivated — 15-day divergence lookback matches the typical institutional accumulation timeline, 20-day VWAP is a standard period, close location 0.7 is a natural "conviction" threshold. Should survive ±20% changes. Works best in mid-cap equities where institutional activity is detectable but not fully absorbed by dark pools.

### Viability Scorecard
| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| Behavioral rationale strength | 9 | Information asymmetry / institutional footprint is well-documented |
| Simplicity (fewer params = higher) | 7 | 4 parameters, structurally motivated |
| Indicator diversity | 9 | Volume Flow (Cat 5) + Trend (Cat 2 via VWAP) + OHLC Structure (Cat 6) |
| Crowding resistance | 8 | OBV divergence + VWAP reclaim + close location is a non-obvious combination |
| Volume confirmation | 9 | OBV divergence IS the core signal |
| Regime robustness | 6 | Works in transitions (bear→bull, consolidation→trend); less useful in strong trends |
| **Overall** | **8.0** | |

---

## Comparison Matrix

| Aspect | Strategy 1: VRMC | Strategy 2: VCER | Strategy 3: OPDAE |
|--------|:---:|:---:|:---:|
| **Style** | Momentum (trend following) | Mean reversion (event-driven) | Divergence (anticipatory) |
| **Primary Signal** | EMA crossover | Volume climax + RSI extreme | OBV-price divergence |
| **Volume Role** | OBV slope confirms trend | Relative volume IS the signal | OBV trend leads price |
| **Categories Used** | Trend + Volume + OB/OS | Volume + OB/OS + Volatility + Value | Volume + Trend (VWAP) + OHLC |
| **Parameters** | 4 | 4 | 4 |
| **Hold Period** | 2-8 weeks | 1-3 weeks | 2-6 weeks |
| **Signal Frequency** | Moderate (weekly) | Low (event-driven) | Low-Moderate |
| **Best Regime** | Trending (bull or bear) | Post-selloff recovery | Accumulation → breakout |
| **Worst Regime** | Choppy/range-bound | Sustained bear market | Strong trends (no divergence) |
| **Turnover** | ~200% annually | ~100% annually | ~150% annually |
| **Overall Score** | **7.5/10** | **7.7/10** | **8.0/10** |
| **Complementarity** | Pairs well with VCER (different regimes) | Pairs well with VRMC | Standalone or with either |

### Portfolio Construction Note
These three strategies are **deliberately complementary**:
- **VRMC** captures established trends (momentum)
- **VCER** captures panic overshoots (mean reversion)
- **OPDAE** captures stealth accumulation before moves (anticipatory)

Running all three together provides natural regime diversification: when momentum signals are scarce (choppy markets), exhaustion reversals become more frequent. When neither trend nor exhaustion signals fire, OBV divergences may detect quiet accumulation before the next move.

---

## Appendix: Data Quality & Implementation Notes

### Data Requirements
- **Minimum history**: 200 trading days for indicator warm-up (EMA 50 needs ~150 days, OBV slope z-score needs 60-day expanding window)
- **Price adjustment**: Use split- and dividend-adjusted close prices for all return calculations; split-adjusted volume
- **Universe filtering**: Minimum $5 price and $1M average daily volume to ensure tradability and reliable volume data
- **P/E data**: Lag by at least 1 day after earnings announcements to avoid lookahead

### Common Implementation Pitfalls
1. **Lookahead bias**: All signals use `.shift(1)` before generating trade signals — compute signal at day's close, trade at next open
2. **Survivorship bias**: When backtesting, use a point-in-time universe (not current S&P 500 membership)
3. **Volume data quality**: Check for stock splits causing artificial volume spikes; use split-adjusted volume
4. **OBV initialization**: OBV is cumulative — its absolute level is arbitrary, only changes and trends matter. Always use slope or change metrics, not absolute OBV levels.

---

## Web Research Sources
- Jegadeesh & Titman (1993), "Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency"
- Gervais, Kaniel & Mingelgrin (2001), "The High-Volume Return Premium"
- Campbell, Grossman & Wang (1993), "Trading Volume and Serial Correlation in Stock Returns"
- Blume, Easley & O'Hara (1994), "Market Statistics and Technical Analysis: The Role of Volume"
- Kyle (1985), "Continuous Auctions and Insider Trading"
- Chordia & Swaminathan (2000), "Trading Volume and Cross-Autocorrelations in Stock Returns"
- Kaniel, Saar & Titman (2008), "Individual Investor Trading and Stock Returns"
- Loh (2010), "Investor Inattention and the Underreaction to Stock Recommendations"
- Harvey, Liu & Zhu (2016), "...and the Cross-Section of Expected Returns"
- Lo & MacKinlay, "Data-Snooping Biases in Tests of Financial Asset Pricing Models"
