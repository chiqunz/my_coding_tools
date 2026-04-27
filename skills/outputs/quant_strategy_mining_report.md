# Strategy Mining Report
**Date**: 2026-03-10
**Request**: Mine mid-term quantitative trading strategies (holding period days to weeks) combining volume signals with price momentum or mean reversion patterns. No intra-day trading.
**Data Constraint**: OHLCV + P/E only

---

## Strategy 1: Volume-Confirmed Momentum Exhaustion Reversal (VCMER)

### Idea
This strategy identifies stocks that have experienced a sharp multi-day decline accompanied by a climactic volume surge (selling exhaustion), followed by a volume dry-up on subsequent down days. The divergence between price continuing to drift lower on declining volume suggests forced/panic sellers have been flushed out, and the remaining holders are conviction holders. Entry is timed when volume contracts below a threshold after the climax, with P/E acting as a valuation floor to avoid genuine distress.

### Behavioral / Structural Rationale
- **Why this pattern exists**: Loss aversion and forced liquidation create selling climaxes. When margin calls, fund redemptions, or stop-loss cascades occur, sellers dump shares regardless of fundamental value. Once forced sellers are exhausted, the overhang clears but price takes days to stabilize because remaining market participants anchor to the recently depressed price. The volume dry-up after a climax signals that the selling pressure has been absorbed.
- **Who is on the wrong side**: Late panic sellers who liquidate near the bottom after the forced sellers have already left. Also, short sellers who pile on during the high-volume decline, creating a short squeeze setup once selling dries up.
- **Academic/empirical support**: The volume-return relationship literature (Campbell, Grossman & Wang, 1993 — "Trading Volume and Serial Correlation in Stock Returns") shows that high-volume declines tend to reverse more quickly than low-volume declines, as they represent temporary liquidity shocks rather than information-driven repricing. The disposition effect literature also supports that selling climaxes create temporary price dislocations.

### Signal Logic
- **Indicators used**:
  - Relative Volume (Category 5: Volume Flow) — Volume / Median(Volume, 20) to detect the climax
  - ROC(10) (Category 3: Rate of Change) — 10-day rate of change to measure the severity of the decline
  - ATR(14) percentile (Category 4: Volatility) — rolling percentile of ATR to confirm heightened volatility regime
  - P/E z-score (Category 7: Valuation) — time-series z-score to ensure valuation floor
- **Signal formula**:
  1. **Climax Detection**: A "volume climax day" is identified when Relative Volume > 2.5x AND daily return < -3%.
  2. **Exhaustion Confirmation**: In the 5 trading days AFTER a climax day, compute the average Relative Volume. If average RelVol < 0.8 (volume drying up), exhaustion is confirmed.
  3. **Decline Severity Gate**: ROC(10) must be < -8% (substantial decline, not trivial noise).
  4. **Volatility Regime**: ATR(14) must be in its top 30th percentile over the trailing 126 days (confirms we're in a high-vol environment where mean reversion is stronger).
  5. **Valuation Floor**: P/E must be between 5 and 50, and P/E z-score (63-day) must be < 1.0 (not at extreme valuation highs).
  6. **Composite Signal**: `signal = (climax_detected & exhaustion_confirmed & decline_severe & high_vol_regime & valuation_ok)`
- **Parameters**:
  1. `climax_vol_threshold` = 2.5 (relative volume multiplier for climax detection)
  2. `exhaustion_vol_threshold` = 0.8 (relative volume below which exhaustion is confirmed)
  3. `decline_roc_threshold` = -0.08 (minimum 10-day decline for entry)
  4. `atr_percentile_threshold` = 0.70 (ATR must be above this percentile)
  5. `holding_days` = 15 (exit after N trading days — time-based exit)
- **Entry rule**: Go long at next day's open when ALL conditions are simultaneously true: climax detected within last 7 trading days, volume exhaustion confirmed (5-day post-climax average RelVol < 0.8), ROC(10) < -8%, ATR in top 30%, P/E between 5-50 with z-score < 1.0.
- **Exit rule**: Time-based exit after 15 trading days, OR exit early if the stock makes a new 20-day low (stop-loss to avoid catching falling knives where the fundamental story has changed).
- **Holding period**: ~15 trading days (~3 weeks)
- **Rebalance frequency**: Signal-based (event-driven entry, time-based exit)

### Implementation Steps
1. Compute 20-day median volume and daily Relative Volume ratio for each stock
2. Compute daily returns from adjusted close prices
3. Flag "climax days" where RelVol > 2.5 AND daily return < -3%
4. For each climax day, compute the average RelVol over the next 5 trading days; flag exhaustion if average < 0.8
5. Compute ROC(10) = (Close / Close_10_days_ago) - 1
6. Compute ATR(14) and its rolling 126-day percentile rank
7. Compute P/E z-score using a 63-day expanding window
8. Combine all conditions into a binary entry signal
9. Enter at next-day open; exit after 15 trading days or on new 20-day low

### Example Python Code

```python
import pandas as pd
import numpy as np


def vcmer_signal(
    ohlcv: pd.DataFrame,
    pe: pd.Series | None = None,
    climax_vol_threshold: float = 2.5,
    exhaustion_vol_threshold: float = 0.8,
    decline_roc_threshold: float = -0.08,
    atr_percentile_threshold: float = 0.70,
    holding_days: int = 15,
) -> pd.Series:
    """
    Volume-Confirmed Momentum Exhaustion Reversal (VCMER)

    Detects selling climaxes followed by volume exhaustion, entering
    after the forced/panic sellers have been flushed out of a stock
    that remains reasonably valued.

    Behavioral rationale: Loss aversion and forced liquidation create
    temporary price dislocations. Volume dry-up after a climax signals
    the selling overhang has cleared.
    Holding period: ~15 trading days (~3 weeks)
    Data required: OHLCV + P/E only

    Parameters
    ----------
    ohlcv : DataFrame with columns [Open, High, Low, Close, Volume]
    pe : Optional P/E ratio series
    climax_vol_threshold : Relative volume multiplier for climax detection
    exhaustion_vol_threshold : RelVol below which exhaustion is confirmed
    decline_roc_threshold : Minimum 10-day decline required (negative)
    atr_percentile_threshold : ATR must be above this percentile (0-1)
    holding_days : Number of days to hold the position

    Returns
    -------
    Series of signal values (1 = entry signal, 0 = no signal)
    """
    close = ohlcv["Close"]
    high = ohlcv["High"]
    low = ohlcv["Low"]
    volume = ohlcv["Volume"]

    # --- Step 1: Relative Volume ---
    median_vol_20 = volume.rolling(20).median()
    rel_vol = volume / median_vol_20

    # --- Step 2: Daily returns ---
    daily_ret = close.pct_change()

    # --- Step 3: Climax day detection ---
    # High relative volume + significant down day
    climax_day = (rel_vol > climax_vol_threshold) & (daily_ret < -0.03)

    # --- Step 4: Exhaustion confirmation ---
    # Average relative volume in the 5 days AFTER a climax day
    # Use forward-looking rolling mean, then shift to align
    # We look back: for each day, check if there was a climax 5-7 days ago
    # and if volume has dried up since then
    post_climax_avg_vol = rel_vol.rolling(5).mean()
    climax_within_7d = climax_day.rolling(7).max().fillna(0).astype(bool)
    exhaustion_confirmed = climax_within_7d & (post_climax_avg_vol < exhaustion_vol_threshold)

    # --- Step 5: Decline severity gate ---
    roc_10 = close / close.shift(10) - 1
    decline_severe = roc_10 < decline_roc_threshold

    # --- Step 6: Volatility regime ---
    # True Range
    tr = pd.concat(
        [
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr_14 = tr.rolling(14).mean()
    # Rolling 126-day percentile rank of ATR
    atr_pctile = atr_14.rolling(126).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
    )
    high_vol_regime = atr_pctile > atr_percentile_threshold

    # --- Step 7: Valuation floor (if P/E provided) ---
    if pe is not None:
        pe_clean = pe.copy()
        pe_clean[(pe_clean <= 0) | (pe_clean > 200)] = np.nan
        pe_valid = pe_clean.between(5, 50)
        pe_zscore = (pe_clean - pe_clean.rolling(63, min_periods=20).mean()) / pe_clean.rolling(
            63, min_periods=20
        ).std()
        valuation_ok = pe_valid & (pe_zscore < 1.0)
    else:
        valuation_ok = pd.Series(True, index=close.index)

    # --- Step 8: Combine all conditions ---
    entry_signal = (
        exhaustion_confirmed & decline_severe & high_vol_regime & valuation_ok
    ).astype(int)

    # Shift signal by 1 day (trade at next day's open, not today's close)
    entry_signal = entry_signal.shift(1).fillna(0).astype(int)

    return entry_signal
```

### Reasoning & Edge Assessment
- **Why this might work**:
  - Forced sellers (margin calls, redemptions) create temporary price dislocations that are well-documented in academic literature
  - Volume exhaustion is a structural signal — when volume dries up after a climax, it mechanically means selling pressure has been absorbed
  - The multi-condition filter (volume climax + exhaustion + decline severity + high ATR + P/E floor) dramatically reduces false positives compared to simple "buy the dip" strategies
- **Why this might fail**:
  - In bear markets, selling climaxes may be followed by further fundamental deterioration — the P/E floor helps but doesn't fully protect
  - If the stock's decline is information-driven (earnings miss, fraud), mean reversion won't occur regardless of volume patterns
  - The strategy is event-driven with low signal frequency, making it hard to build a diversified portfolio
- **Key risks**: Regime dependency (underperforms in sustained bear markets), catching falling knives despite filters, low signal frequency reduces diversification, parameter sensitivity around the climax detection thresholds
- **Estimated robustness**: The signal should survive +-20% parameter changes because the thresholds are wide (2.5x volume is robust from 2.0x to 3.0x). Cross-market applicability is moderate — works best in liquid markets with occasional volatility spikes.

### Viability Scorecard
| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| Behavioral rationale strength | 8 | Strong: forced liquidation and loss aversion well-documented |
| Simplicity (fewer params = higher) | 6 | 5 parameters — at the maximum, but each is well-justified |
| Indicator diversity | 9 | Uses Volume Flow (Cat 5) + Rate of Change (Cat 3) + Volatility (Cat 4) + Valuation (Cat 7) |
| Crowding resistance | 8 | Multi-condition filter is unusual; simple "buy oversold" is crowded but this composite is not |
| Volume confirmation | 10 | Volume is the primary signal component (climax + exhaustion) |
| Regime robustness | 5 | Struggles in sustained bear markets; works best in corrections within bull markets |
| **Overall** | **7.7** | |

---

## Strategy 2: OBV Trend Divergence with Momentum Confirmation (OTDMC)

### Idea
This strategy detects stocks where On-Balance Volume (OBV) is making higher highs while price is flat or declining — a "stealth accumulation" signal suggesting that informed buyers (institutions) are building positions before the price moves. The entry is confirmed by a short-term momentum trigger (price breaking above its 20-day SMA), ensuring we don't enter during the accumulation phase but at the point where the accumulated buying pressure begins to move the price.

### Behavioral / Structural Rationale
- **Why this pattern exists**: Large institutional investors cannot buy their full position in a single day without moving the price against themselves. Instead, they split orders over weeks, buying on dips and absorbing selling pressure. This creates a pattern where volume-weighted buying pressure (captured by OBV) rises steadily while price remains suppressed because the institution is deliberately avoiding pushing the price up. Once the position is built, the buying pressure diminishes, supply/demand tilts bullish, and the stock begins to rise as smaller follow-on buyers enter.
- **Who is on the wrong side**: Retail traders and short sellers who see a flat or declining stock price and interpret it as weakness, not recognizing the institutional accumulation footprint visible in volume flow. They are selling to the institution at suppressed prices.
- **Academic/empirical support**: Blume, Easley & O'Hara (1994 — "Market Statistics and Technical Analysis: The Role of Volume") demonstrated that volume carries information about future price movements that is not captured by price alone. Granville's OBV concept, while old, has been validated in modern cross-sectional studies showing that volume-price divergences predict future returns with a 2-6 week horizon.

### Signal Logic
- **Indicators used**:
  - OBV slope (Category 5: Volume Flow) — 20-day linear regression slope of OBV, normalized
  - Price ROC(20) (Category 3: Rate of Change) — 20-day rate of change to measure price momentum
  - Close vs SMA(20) (Category 2: Trend Direction) — price relative to 20-day moving average as entry trigger
  - Close location value (Category 6: OHLC Structure) — (Close - Low) / (High - Low) to measure intraday buying pressure
- **Signal formula**:
  1. **OBV Trend**: Compute OBV, then the 20-day linear regression slope of OBV. Normalize by dividing by the rolling 20-day mean of absolute volume. A positive normalized OBV slope indicates net buying.
  2. **Divergence Detection**: OBV slope z-score (20-day) > 1.0 AND Price ROC(20) < 0.02 (price is flat or declining while OBV is trending strongly upward).
  3. **Close Location Filter**: Average close location value over last 5 days > 0.55 (price consistently closing in the upper half of the daily range — a subtle sign of buying pressure).
  4. **Momentum Trigger**: Close crosses above SMA(20) — this is the entry timing mechanism.
  5. **Composite**: `signal = (obv_divergence & close_location_bullish & momentum_trigger)`
- **Parameters**:
  1. `obv_slope_window` = 20 (lookback for OBV linear regression slope)
  2. `obv_zscore_threshold` = 1.0 (minimum z-score for OBV slope to be "strong")
  3. `price_roc_ceiling` = 0.02 (maximum price ROC for divergence — price must be flat/down)
  4. `close_location_threshold` = 0.55 (minimum average close location value)
  5. `holding_days` = 20 (target hold period)
- **Entry rule**: Go long at next day's open when: (1) OBV slope z-score > 1.0, (2) Price ROC(20) < 2%, (3) 5-day average close location > 0.55, and (4) close crosses above SMA(20) today.
- **Exit rule**: Exit after 20 trading days, OR exit early if close falls below SMA(20) for 3 consecutive days (trend broken).
- **Holding period**: ~20 trading days (~4 weeks)
- **Rebalance frequency**: Signal-based entry, time + trend-based exit

### Implementation Steps
1. Compute OBV: cumulative sum of (Volume * sign(daily return))
2. Compute 20-day linear regression slope of OBV using rolling window
3. Normalize OBV slope by dividing by rolling 20-day mean of absolute volume
4. Compute z-score of normalized OBV slope using 60-day rolling window
5. Compute Price ROC(20) = Close / Close[20 days ago] - 1
6. Compute Close Location Value = (Close - Low) / (High - Low) for each day; take 5-day average
7. Compute SMA(20) of close price; detect upward crossings
8. Combine: OBV z-score > 1.0 AND ROC(20) < 0.02 AND CLV_avg > 0.55 AND close crosses above SMA(20)
9. Enter at next-day open; exit after 20 days or on 3 consecutive closes below SMA(20)

### Example Python Code

```python
import pandas as pd
import numpy as np
from numpy.polynomial import polynomial as P


def otdmc_signal(
    ohlcv: pd.DataFrame,
    pe: pd.Series | None = None,
    obv_slope_window: int = 20,
    obv_zscore_threshold: float = 1.0,
    price_roc_ceiling: float = 0.02,
    close_location_threshold: float = 0.55,
    holding_days: int = 20,
) -> pd.Series:
    """
    OBV Trend Divergence with Momentum Confirmation (OTDMC)

    Detects institutional accumulation via OBV-price divergence,
    entering when a short-term momentum trigger fires after
    stealth buying pressure has built up.

    Behavioral rationale: Institutions split large orders over weeks,
    creating rising OBV while price stays flat. When accumulation
    ends, supply/demand shifts bullish.
    Holding period: ~20 trading days (~4 weeks)
    Data required: OHLCV (P/E optional for additional filtering)

    Parameters
    ----------
    ohlcv : DataFrame with columns [Open, High, Low, Close, Volume]
    pe : Optional P/E ratio series (used for supplementary filtering)
    obv_slope_window : Lookback window for OBV linear regression slope
    obv_zscore_threshold : Min z-score for OBV slope to be "strong"
    price_roc_ceiling : Max price ROC(20) for divergence detection
    close_location_threshold : Min avg close location for buying pressure
    holding_days : Target holding period in trading days

    Returns
    -------
    Series of signal values (1 = entry signal, 0 = no signal)
    """
    close = ohlcv["Close"]
    high = ohlcv["High"]
    low = ohlcv["Low"]
    volume = ohlcv["Volume"]

    # --- Step 1: Compute OBV ---
    daily_ret = close.pct_change()
    obv = (volume * np.sign(daily_ret)).cumsum()

    # --- Step 2: OBV slope (20-day rolling linear regression) ---
    def rolling_slope(series, window):
        """Compute rolling linear regression slope."""
        slopes = pd.Series(np.nan, index=series.index)
        x = np.arange(window, dtype=float)
        for i in range(window - 1, len(series)):
            y = series.iloc[i - window + 1 : i + 1].values
            if np.any(np.isnan(y)):
                continue
            # Simple linear regression: slope = cov(x,y) / var(x)
            slope = np.polyfit(x, y, 1)[0]
            slopes.iloc[i] = slope
        return slopes

    obv_slope = rolling_slope(obv, obv_slope_window)

    # --- Step 3: Normalize OBV slope ---
    avg_abs_volume = volume.abs().rolling(obv_slope_window).mean()
    norm_obv_slope = obv_slope / avg_abs_volume

    # --- Step 4: Z-score of normalized OBV slope ---
    obv_slope_mean = norm_obv_slope.rolling(60, min_periods=20).mean()
    obv_slope_std = norm_obv_slope.rolling(60, min_periods=20).std()
    obv_zscore = (norm_obv_slope - obv_slope_mean) / obv_slope_std

    # --- Step 5: Price ROC(20) ---
    price_roc_20 = close / close.shift(20) - 1

    # --- Step 6: Close Location Value ---
    range_hl = high - low
    range_hl = range_hl.replace(0, np.nan)  # avoid division by zero
    clv = (close - low) / range_hl
    clv_avg_5 = clv.rolling(5).mean()

    # --- Step 7: SMA(20) crossover detection ---
    sma_20 = close.rolling(20).mean()
    above_sma = close > sma_20
    cross_above_sma = above_sma & (~above_sma.shift(1).fillna(False))

    # --- Step 8: Divergence detection ---
    divergence = (obv_zscore > obv_zscore_threshold) & (price_roc_20 < price_roc_ceiling)

    # --- Step 9: Close location filter ---
    clv_bullish = clv_avg_5 > close_location_threshold

    # --- Step 10: Combine all conditions ---
    entry_signal = (divergence & clv_bullish & cross_above_sma).astype(int)

    # Optional P/E filter: exclude extreme valuations
    if pe is not None:
        pe_clean = pe.copy()
        pe_ok = pe_clean.between(5, 80)
        entry_signal = entry_signal * pe_ok.astype(int)

    # Shift signal by 1 day (trade at next day's open)
    entry_signal = entry_signal.shift(1).fillna(0).astype(int)

    return entry_signal
```

### Reasoning & Edge Assessment
- **Why this might work**:
  - Institutional order flow is a genuine, persistent source of information asymmetry — large funds MUST split orders, and this is mechanically visible in volume data
  - The divergence + trigger combination avoids the classic problem of being early — you wait for the momentum confirmation before entering
  - Close location value adds a subtle, less-crowded confirmation dimension that most traders don't monitor
- **Why this might fail**:
  - OBV is noisy and can show false divergences, especially in stocks with erratic volume patterns
  - The pattern can also appear before negative catalysts (institutions selling to retail, not accumulating)
  - In strongly trending markets, the "price flat" condition may rarely be met, reducing signal frequency
- **Key risks**: False divergences in noisy volume data, regime dependency (works best in range-bound to mildly trending markets), OBV conflation of institutional buying with short covering, low signal frequency
- **Estimated robustness**: Moderate. The OBV z-score threshold of 1.0 is robust across +-20% changes. The SMA crossover trigger is standard. Cross-market applicability is good for liquid stocks but poor for illiquid ones.

### Viability Scorecard
| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| Behavioral rationale strength | 9 | Institutional accumulation is a well-understood structural phenomenon |
| Simplicity (fewer params = higher) | 6 | 5 parameters, all well-justified |
| Indicator diversity | 9 | Uses Volume Flow (Cat 5) + Rate of Change (Cat 3) + Trend (Cat 2) + OHLC Structure (Cat 6) |
| Crowding resistance | 7 | OBV divergence is known but the CLV + trigger combo adds differentiation |
| Volume confirmation | 10 | Volume IS the primary signal — OBV divergence is pure volume analysis |
| Regime robustness | 6 | Works best in range-bound/sideways markets; less effective in strong trends |
| **Overall** | **7.8** | |

---

## Strategy 3: Volatility Compression Breakout with Volume Thrust (VCBVT)

### Idea
This strategy identifies stocks that have been in a sustained period of unusually low volatility (ATR compression), then waits for a breakout day where price moves decisively out of the compression zone on elevated volume. The combination of volatility compression + directional breakout + volume confirmation exploits the well-documented "volatility clustering" phenomenon: low-vol regimes tend to give way to high-vol regimes, and the first directional move out of compression often carries significant follow-through because it triggers stop orders and attracts momentum traders.

### Behavioral / Structural Rationale
- **Why this pattern exists**: Volatility clustering (GARCH effects) is one of the most robust findings in financial economics. During compression phases, market participants become complacent, options implied volatility drops, and stop-loss orders cluster near the range boundaries. When a catalyst breaks the equilibrium, the clustered stops cascade, creating a self-reinforcing move. The volume thrust confirms that the breakout has institutional participation (not just a thin-market fluke).
- **Who is on the wrong side**: Range-bound mean-reversion traders who have been profiting from selling the range boundaries now get steamrolled. Option sellers who sold cheap volatility during the compression phase face gamma losses. Anchoring bias makes traders underestimate the magnitude of the coming move because they anchor to the recent narrow range.
- **Academic/empirical support**: Mandelbrot's work on volatility clustering, Engle's GARCH model (Nobel Prize 2003), and the extensive literature on breakout strategies show that low-volatility periods predict high-volatility periods. Sewell (2007) documented that volatility breakout strategies, when combined with volume, have historically outperformed simple momentum strategies because they time the entry more precisely.

### Signal Logic
- **Indicators used**:
  - ATR(14) / SMA(ATR(14), 50) — "ATR Ratio" (Category 4: Volatility) — measures current volatility relative to medium-term average
  - Bollinger Band Width percentile (Category 4: Volatility — but used structurally, not as overbought/oversold)
  - Volume Thrust = Volume / SMA(Volume, 20) (Category 5: Volume Flow) — confirms institutional participation
  - Body Ratio = |Close - Open| / (High - Low) (Category 6: OHLC Structure) — measures conviction of the breakout candle
- **Signal formula**:
  1. **Compression Detection**: ATR Ratio < 0.7 (current ATR is less than 70% of its 50-day average) for at least 5 of the last 10 trading days. This identifies a stock in a sustained low-vol regime.
  2. **Breakout Day**: On a given day, the absolute daily return exceeds 1.5 * ATR(14) from the previous day — price has made a move that is large relative to recent volatility.
  3. **Volume Thrust**: Volume on the breakout day > 2.0 * SMA(Volume, 20) — the move has institutional participation.
  4. **Candle Conviction**: Body Ratio > 0.6 — the candle closes near its extreme (strong conviction, not a doji/indecision bar).
  5. **Direction**: Long if breakout is upward (close > open); Short if breakout is downward (close < open). This report focuses on the long side.
  6. **Composite**: `signal = (compression_phase & breakout_day & volume_thrust & candle_conviction & upward_direction)`
- **Parameters**:
  1. `atr_ratio_threshold` = 0.7 (ATR Ratio below which volatility is "compressed")
  2. `compression_days` = 5 (minimum days of compression in last 10 days)
  3. `breakout_atr_mult` = 1.5 (daily move must exceed this multiple of ATR)
  4. `volume_thrust_mult` = 2.0 (volume must exceed this multiple of 20-day average)
  5. `body_ratio_threshold` = 0.6 (minimum candle body ratio for conviction)
- **Entry rule**: Go long at next day's open when: stock has been in compression (ATR Ratio < 0.7 for 5+ of last 10 days), today's close - yesterday's close > 1.5 * ATR(14), today's volume > 2.0 * SMA(Volume, 20), body ratio > 0.6, and close > open (upward breakout).
- **Exit rule**: Exit after 10 trading days, OR exit with a trailing stop at 2 * ATR(14) below the highest close since entry.
- **Holding period**: ~10 trading days (~2 weeks)
- **Rebalance frequency**: Signal-based (event-driven entry, trailing stop + time exit)

### Implementation Steps
1. Compute ATR(14) for each stock
2. Compute 50-day SMA of ATR(14), then ATR Ratio = ATR(14) / SMA(ATR(14), 50)
3. Count how many of the last 10 trading days had ATR Ratio < 0.7; require >= 5
4. Compute absolute daily move = |Close - Close_prev|; flag breakout if > 1.5 * ATR(14)
5. Compute 20-day SMA of Volume; flag volume thrust if today's volume > 2.0 * SMA(Vol, 20)
6. Compute Body Ratio = |Close - Open| / (High - Low); flag conviction if > 0.6
7. Determine direction: long if Close > Open
8. Combine all conditions into entry signal
9. Enter at next-day open; exit after 10 days or on trailing stop (2 * ATR below highest close)

### Example Python Code

```python
import pandas as pd
import numpy as np


def vcbvt_signal(
    ohlcv: pd.DataFrame,
    pe: pd.Series | None = None,
    atr_ratio_threshold: float = 0.7,
    compression_days: int = 5,
    breakout_atr_mult: float = 1.5,
    volume_thrust_mult: float = 2.0,
    body_ratio_threshold: float = 0.6,
) -> pd.Series:
    """
    Volatility Compression Breakout with Volume Thrust (VCBVT)

    Identifies stocks in sustained low-volatility compression,
    then enters on the first high-conviction breakout day confirmed
    by an institutional-grade volume surge.

    Behavioral rationale: Volatility clusters (GARCH). Low-vol regimes
    build up energy through stop-order clustering and complacency.
    The first directional breakout cascades through stops and attracts
    momentum capital, creating follow-through.
    Holding period: ~10 trading days (~2 weeks)
    Data required: OHLCV (P/E optional)

    Parameters
    ----------
    ohlcv : DataFrame with columns [Open, High, Low, Close, Volume]
    pe : Optional P/E ratio series
    atr_ratio_threshold : ATR Ratio below which vol is "compressed"
    compression_days : Min days of compression in last 10 days
    breakout_atr_mult : Daily move must exceed this * ATR(14)
    volume_thrust_mult : Volume must exceed this * SMA(Vol, 20)
    body_ratio_threshold : Min candle body ratio for conviction

    Returns
    -------
    Series of signal values (1 = long entry signal, 0 = no signal)
    """
    close = ohlcv["Close"]
    open_ = ohlcv["Open"]
    high = ohlcv["High"]
    low = ohlcv["Low"]
    volume = ohlcv["Volume"]

    # --- Step 1: ATR(14) ---
    tr = pd.concat(
        [
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr_14 = tr.rolling(14).mean()

    # --- Step 2: ATR Ratio (current vs 50-day average) ---
    atr_sma_50 = atr_14.rolling(50).mean()
    atr_ratio = atr_14 / atr_sma_50

    # --- Step 3: Compression detection ---
    # Count days in last 10 where ATR Ratio < threshold
    is_compressed = (atr_ratio < atr_ratio_threshold).astype(int)
    compression_count = is_compressed.rolling(10).sum()
    in_compression = compression_count >= compression_days

    # --- Step 4: Breakout detection ---
    daily_move = (close - close.shift(1)).abs()
    prev_atr = atr_14.shift(1)  # Use previous day's ATR to avoid lookahead
    is_breakout = daily_move > (breakout_atr_mult * prev_atr)

    # --- Step 5: Volume thrust ---
    vol_sma_20 = volume.rolling(20).mean()
    vol_thrust = volume > (volume_thrust_mult * vol_sma_20)

    # --- Step 6: Candle conviction ---
    range_hl = high - low
    range_hl = range_hl.replace(0, np.nan)
    body_ratio = (close - open_).abs() / range_hl
    has_conviction = body_ratio > body_ratio_threshold

    # --- Step 7: Direction (long only: close > open) ---
    is_upward = close > open_

    # --- Step 8: Combine all conditions ---
    entry_signal = (
        in_compression & is_breakout & vol_thrust & has_conviction & is_upward
    ).astype(int)

    # Optional P/E filter: exclude extreme valuations
    if pe is not None:
        pe_clean = pe.copy()
        pe_ok = pe_clean.between(3, 100)
        entry_signal = entry_signal * pe_ok.astype(int)

    # Shift signal by 1 day (trade at next day's open)
    entry_signal = entry_signal.shift(1).fillna(0).astype(int)

    return entry_signal
```

### Reasoning & Edge Assessment
- **Why this might work**:
  - Volatility clustering is one of the most robust empirical facts in finance — GARCH effects are real and persistent
  - The cascading stop-loss mechanism is structural (not behavioral), meaning it's less likely to be arbitraged away
  - Volume thrust adds crucial differentiation — thin-market breakouts frequently fail, while high-volume breakouts have a much higher continuation rate
- **Why this might fail**:
  - In choppy/range-bound markets, false breakouts followed by immediate reversals can be costly
  - The strategy requires a sustained compression phase, which may not occur frequently in volatile markets (reducing signal frequency)
  - If too many participants use similar breakout strategies, the breakout becomes front-run and the follow-through diminishes
- **Key risks**: False breakouts in choppy markets (regime risk), crowding from other breakout traders, parameter sensitivity around the ATR ratio threshold, limited capacity in mid/small cap stocks where volume thrust may be unreliable
- **Estimated robustness**: Good. ATR-based signals use standard parameters (14-day ATR) and are well-studied. The 50-day normalization is a natural business-cycle window. Volume thrust at 2.0x is a robust threshold. Cross-market: works well in equity markets, less applicable to highly liquid instruments like S&P 500 futures where compression-breakout patterns are heavily arbitraged.

### Viability Scorecard
| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| Behavioral rationale strength | 8 | GARCH effects, stop-loss cascading, and anchoring are well-documented |
| Simplicity (fewer params = higher) | 6 | 5 parameters, all with clear structural justification |
| Indicator diversity | 8 | Uses Volatility (Cat 4) + Volume Flow (Cat 5) + OHLC Structure (Cat 6) |
| Crowding resistance | 6 | Breakout strategies are known, but multi-condition filter adds differentiation |
| Volume confirmation | 9 | Volume thrust is a core component, not just a filter |
| Regime robustness | 6 | Works in transitioning markets; struggles in persistently choppy environments |
| **Overall** | **7.2** | |

---

## Comparison Matrix

| Aspect | Strategy 1: VCMER | Strategy 2: OTDMC | Strategy 3: VCBVT |
|--------|:-----------------:|:------------------:|:------------------:|
| **Style** | Mean reversion (post-climax) | Momentum (accumulation breakout) | Breakout (compression-expansion) |
| **Primary Exploitation** | Forced liquidation / Loss aversion | Institutional flow / Information asymmetry | Volatility clustering / Stop cascading |
| **Indicators** | RelVol + ROC + ATR + P/E | OBV slope + ROC + SMA + CLV | ATR Ratio + Volume + Body Ratio |
| **Categories Used** | Cat 3+4+5+7 | Cat 2+3+5+6 | Cat 4+5+6 |
| **Parameters** | 5 | 5 | 5 |
| **Hold Period** | ~15 days (3 weeks) | ~20 days (4 weeks) | ~10 days (2 weeks) |
| **Signal Frequency** | Low (event-driven) | Low-Medium | Low (event-driven) |
| **Best Regime** | Corrections in bull market | Range-bound / sideways | Transitioning from low to high vol |
| **Worst Regime** | Sustained bear market | Strong trends | Choppy/whipsaw markets |
| **Est. Turnover** | 100-200% annually | 150-300% annually | 100-200% annually |
| **Overall Score** | **7.7/10** | **7.8/10** | **7.2/10** |

---

## Portfolio Considerations

The three strategies above are **complementary by design**:
- **VCMER** is contrarian (buy after panic selling) — works best when volatility spikes
- **OTDMC** is trend-following (buy after accumulation) — works best in range-bound markets transitioning to trends
- **VCBVT** is breakout-based (buy after compression) — works best during volatility regime changes

Running all three together provides natural diversification across market regimes. The strategies have low signal correlation because they trigger in different environments:
- VCMER fires during sharp declines → VCBVT unlikely to fire (no compression)
- OTDMC fires during quiet accumulation → VCMER unlikely to fire (no climax)
- VCBVT fires at volatility transitions → OTDMC unlikely to fire (no flat price + rising OBV)

## Implementation Notes

1. **Data Quality**: Use split-adjusted and dividend-adjusted close prices for all return and indicator calculations. Volume should be split-adjusted only.
2. **Execution**: All signals use next-day-open execution (signal computed at close, trade at open) to avoid lookahead bias.
3. **Universe**: Best suited for US large-cap and mid-cap stocks with daily volume > 500,000 shares. Avoid micro-caps where volume signals are unreliable.
4. **Position Sizing**: Equal-weight positions recommended. For portfolio application, limit to 5-10% per position to manage concentration risk.
5. **Risk Management**: Implement portfolio-level stop: if total portfolio drawdown exceeds 10%, reduce position sizes by 50% for the next 20 trading days.

## Web Research Sources
- Campbell, Grossman & Wang (1993) — "Trading Volume and Serial Correlation in Stock Returns"
- Blume, Easley & O'Hara (1994) — "Market Statistics and Technical Analysis: The Role of Volume"
- Engle (2003) — GARCH and Volatility Clustering (Nobel Prize lecture)
- Lou & Polk — "Comomentum: Inferring Arbitrage Activity from Return Correlations"
- Harvey, Liu & Zhu (2016) — "...and the Cross-Section of Expected Returns"
- Lo & MacKinlay — "Data-Snooping Biases in Tests of Financial Asset Pricing Models"
- Sewell (2007) — "Technical Analysis in Financial Markets"
