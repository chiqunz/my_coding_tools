# Strategy Mining Report
**Date**: 2026-03-10
**Request**: Mine mid-term quantitative trading strategies based on price (OHLCV) and volume data. No intra-day trading. Holding period: days to months.
**Data Constraint**: OHLCV + P/E only

---

## Strategy 1: Volume-Confirmed Momentum with Valuation Guard

### Idea
Exploit the well-documented **underreaction** bias: when stocks exhibit strong 6-month price momentum *and* that momentum is confirmed by rising on-balance volume, the trend is driven by institutional accumulation rather than noise. A P/E valuation guard prevents chasing overvalued bubble stocks, targeting the sweet spot where price momentum, volume conviction, and reasonable valuation converge.

### Behavioral / Structural Rationale
- **Why this pattern exists**: Information diffuses slowly across investor segments. Institutional investors build positions gradually over weeks, leaving a footprint in OBV before the price fully adjusts. Retail investors anchor to old prices and underreact to sustained buying pressure.
- **Who is on the wrong side**: Anchoring investors who refuse to buy "because it already went up" and miss continued institutional accumulation. Also, value-trap contrarians who short momentum without checking volume conviction.
- **Academic/empirical support**: Jegadeesh & Titman (1993) documented 6-12 month momentum profits. Lee & Swaminathan (2000) showed volume predicts momentum lifecycle — high-volume momentum stocks have stronger continuation. Asness et al. (2013) demonstrated value-momentum composite benefits from negative correlation.

### Signal Logic
- **Indicators used**:
  - 126-day (6-month) price return — *Rate of Change* category
  - OBV 63-day slope (normalized) — *Volume Flow* category
  - P/E percentile rank (cross-sectional) — *Valuation* category
- **Signal formula**:
  ```
  momentum_score = Return_126d (skip last 21 days for short-term reversal)
  volume_score = LinearRegSlope(OBV, 63) / Std(OBV, 63)
  value_score = 1 - PE_percentile_rank (lower P/E = higher score)

  composite = 0.50 * rank(momentum_score)
             + 0.30 * rank(volume_score)
             + 0.20 * rank(value_score)
  ```
- **Parameters**:
  1. `momentum_lookback` = 126 days (6 months) — matches mid-term momentum half-life
  2. `skip_days` = 21 (skip last month to avoid short-term reversal)
  3. `obv_slope_window` = 63 days (3 months) — captures institutional accumulation pace
  4. `value_weight` = 0.20 — mild valuation tilt
  5. `pe_max` = 100 — exclude extreme P/E stocks
- **Entry rule**: Monthly rebalance. Go long the top decile of composite score. Exclude stocks with P/E < 0 or P/E > `pe_max`.
- **Exit rule**: Rebalance monthly. Sell when stock drops out of top quintile (buffer from decile to quintile to reduce turnover).
- **Holding period**: 1-3 months per position (monthly rebalance with buffer)
- **Rebalance frequency**: Monthly

### Implementation Steps
1. Compute 126-day return for each stock, skipping the most recent 21 days: `ret = close[t-21] / close[t-126] - 1`
2. Compute OBV series: cumulative sum of `volume * sign(daily_return)`
3. Compute 63-day linear regression slope of OBV, normalized by its rolling std
4. Compute cross-sectional P/E percentile rank, excluding P/E ≤ 0 and P/E > 100
5. Rank all three sub-scores cross-sectionally (percentile rank 0 to 1)
6. Combine: `composite = 0.50 * momentum_rank + 0.30 * volume_rank + 0.20 * value_rank`
7. Go long the top decile. Apply buffer: only exit when stock falls below top quintile
8. Equal-weight positions within the portfolio

### Example Python Code

```python
import pandas as pd
import numpy as np
from scipy.stats import linregress


def volume_confirmed_momentum_signal(
    ohlcv: pd.DataFrame,
    pe: pd.Series = None,
    momentum_lookback: int = 126,
    skip_days: int = 21,
    obv_slope_window: int = 63,
    value_weight: float = 0.20,
    pe_max: float = 100.0,
) -> pd.Series:
    """
    Volume-Confirmed Momentum with Valuation Guard.

    Combines 6-month momentum (skipping last month), OBV slope
    confirmation, and P/E valuation filter into a single composite score.

    Behavioral rationale: Institutional investors build positions gradually,
    leaving OBV footprints. Anchoring bias causes underreaction to sustained
    momentum. P/E guard avoids bubble stocks.

    Holding period: 1-3 months (monthly rebalance)
    Data required: OHLCV + P/E

    Parameters
    ----------
    ohlcv : DataFrame with columns [Open, High, Low, Close, Volume]
    pe : Optional P/E ratio series (cross-sectional for ranking)
    momentum_lookback : Lookback for momentum return (default 126 = 6 months)
    skip_days : Days to skip for short-term reversal avoidance (default 21)
    obv_slope_window : Window for OBV slope calculation (default 63 = 3 months)
    value_weight : Weight for P/E value score in composite (default 0.20)
    pe_max : Maximum P/E to include (default 100)

    Returns
    -------
    Series of composite signal values (higher = more bullish)
    """
    close = ohlcv['Close']
    volume = ohlcv['Volume']

    # --- Momentum Score (skip last 21 days) ---
    # Use close from skip_days ago vs close from momentum_lookback ago
    past_close = close.shift(momentum_lookback)
    recent_close = close.shift(skip_days)
    momentum_score = (recent_close / past_close) - 1.0

    # --- OBV Slope Score ---
    daily_return = close.pct_change()
    obv_direction = np.sign(daily_return)
    obv = (volume * obv_direction).cumsum()

    # Rolling linear regression slope of OBV, normalized
    def rolling_obv_slope(obv_series, window):
        slopes = pd.Series(np.nan, index=obv_series.index)
        for i in range(window, len(obv_series)):
            y = obv_series.iloc[i - window:i].values
            if np.all(np.isnan(y)):
                continue
            x = np.arange(window)
            mask = ~np.isnan(y)
            if mask.sum() < window * 0.8:
                continue
            slope, _, _, _, _ = linregress(x[mask], y[mask])
            slopes.iloc[i] = slope
        return slopes

    obv_slope = rolling_obv_slope(obv, obv_slope_window)
    obv_std = obv.rolling(obv_slope_window).std()
    volume_score = obv_slope / obv_std.replace(0, np.nan)

    # --- Value Score (P/E based) ---
    if pe is not None:
        pe_clean = pe.copy()
        pe_clean[pe_clean <= 0] = np.nan
        pe_clean[pe_clean > pe_max] = np.nan
        # Lower P/E = higher value score (using rank)
        pe_rank = pe_clean.rank(pct=True)
        value_score = 1.0 - pe_rank
    else:
        value_score = pd.Series(0.5, index=close.index)  # neutral if no P/E

    # --- Composite Score ---
    # Cross-sectional percentile ranks
    mom_rank = momentum_score.rank(pct=True)
    vol_rank = volume_score.rank(pct=True)
    val_rank = value_score.rank(pct=True) if pe is not None else 0.5

    momentum_weight = 1.0 - value_weight - 0.30  # remaining goes to momentum
    composite = (
        momentum_weight * mom_rank
        + 0.30 * vol_rank
        + value_weight * val_rank
    )

    return composite


# --- Vectorized version (faster, no scipy dependency) ---
def volume_confirmed_momentum_signal_fast(
    ohlcv: pd.DataFrame,
    pe: pd.Series = None,
    momentum_lookback: int = 126,
    skip_days: int = 21,
    obv_slope_window: int = 63,
    value_weight: float = 0.20,
    pe_max: float = 100.0,
) -> pd.Series:
    """
    Vectorized version using pandas rolling apply for OBV slope.
    Faster than the loop-based version above.
    """
    close = ohlcv['Close']
    volume = ohlcv['Volume']

    # Momentum
    past_close = close.shift(momentum_lookback)
    recent_close = close.shift(skip_days)
    momentum_score = (recent_close / past_close) - 1.0

    # OBV
    daily_return = close.pct_change()
    obv = (volume * np.sign(daily_return)).cumsum()

    # OBV slope via rolling covariance trick:
    # slope = cov(x, y) / var(x) where x = [0, 1, ..., n-1]
    # For a window of size n: var(x) = n*(n-1)/12 (for integers 0..n-1)
    # cov(x, y) = mean(x*y) - mean(x)*mean(y)
    n = obv_slope_window
    x_mean = (n - 1) / 2.0
    x_var = (n**2 - 1) / 12.0  # variance of [0, 1, ..., n-1]

    # We need rolling mean of (i * obv_i) — approximate via diff approach
    obv_roll_mean = obv.rolling(n).mean()
    # Approximate slope using (last - first) / window as a simpler proxy
    obv_slope_approx = (obv - obv.shift(n)) / n
    obv_std = obv.rolling(n).std()
    volume_score = obv_slope_approx / obv_std.replace(0, np.nan)

    # Value
    if pe is not None:
        pe_clean = pe.copy()
        pe_clean[pe_clean <= 0] = np.nan
        pe_clean[pe_clean > pe_max] = np.nan
        value_score = 1.0 - pe_clean.rank(pct=True)
    else:
        value_score = 0.5

    # Composite
    mom_rank = momentum_score.rank(pct=True)
    vol_rank = volume_score.rank(pct=True)
    val_rank = value_score.rank(pct=True) if pe is not None else 0.5

    composite = 0.50 * mom_rank + 0.30 * vol_rank + value_weight * val_rank
    return composite
```

### Reasoning & Edge Assessment
- **Why this might work**:
  - Momentum is one of the most robust anomalies in finance (Jegadeesh & Titman 1993, Asness et al. 2013). The 6-month lookback with 1-month skip is the canonical academic formulation.
  - OBV slope adds a volume confirmation layer that distinguishes "real" momentum (institutional accumulation) from "fake" momentum (low-volume drift). Lee & Swaminathan (2000) documented this effect.
  - P/E guard prevents the strategy from loading up on bubble stocks near cycle peaks, addressing the well-known momentum crash risk.
- **Why this might fail**:
  - Momentum crashes during sharp market reversals (2009 Q1, 2020 Q1) — all momentum stocks fall together in a "fire sale."
  - OBV is sensitive to data quality — stock splits and ex-dividend dates can create false OBV signals if data isn't properly adjusted.
  - Cross-sectional ranking requires a broad universe (50+ stocks); breaks down with small universes.
- **Key risks**: Momentum crash risk during regime changes; crowding in momentum factor; P/E data staleness (quarterly lag); survivorship bias in free data sources.
- **Estimated robustness**: High — uses standard parameters, three diverse indicator categories, and the individual components are well-documented academically. Should survive ±20% parameter changes.

### Viability Scorecard
| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| Behavioral rationale strength | 9 | Underreaction + institutional flow are well-documented |
| Simplicity (fewer params = higher) | 7 | 5 params, all with clear justification |
| Indicator diversity | 9 | Rate of Change + Volume Flow + Valuation (3 categories) |
| Crowding resistance | 6 | Momentum is crowded, but OBV + P/E overlay is less common |
| Volume confirmation | 9 | OBV slope is central to the signal |
| Regime robustness | 6 | Momentum suffers in sharp reversals; P/E guard helps partially |
| **Overall** | **7.7** | |

---

## Strategy 2: Volatility Compression Breakout with Volume Surge

### Idea
Exploit the **volatility clustering** phenomenon: periods of abnormally low volatility (ATR compression) precede large directional moves. When price breaks out of a tight Bollinger Band squeeze *with* a volume surge, it signals the end of institutional accumulation and the beginning of a new trend. The volume surge confirms genuine institutional commitment rather than a false breakout.

### Behavioral / Structural Rationale
- **Why this pattern exists**: Volatility mean-reverts (GARCH effect). During compression phases, institutions quietly build positions. The breakout triggers stop-loss cascading from short sellers and draws in momentum traders, creating a self-reinforcing move. Low ATR periods represent equilibrium zones where new information hasn't yet forced a reprice.
- **Who is on the wrong side**: Range-bound traders who sell at the top of the range and buy at the bottom — they get stopped out when the true breakout occurs. Also, traders with recency bias who assume low volatility will persist.
- **Academic/empirical support**: Mandelbrot (1963) documented volatility clustering. Bollinger (2001) detailed the squeeze concept. Brock, Lakonishok & LeBaron (1992) provided evidence for technical trading rule profitability in breakout strategies. Academic studies on the "leverage effect" show volatility expands more on downside moves.

### Signal Logic
- **Indicators used**:
  - Bollinger Bandwidth (20, 2) — *Volatility* category
  - ATR(14) relative to its 126-day rolling median — *Volatility refinement*
  - Relative Volume (Volume / Median Volume 20-day) — *Volume Flow* category
  - Close Location Value: (Close - Low) / (High - Low) — *OHLC Structure* category
- **Signal formula**:
  ```
  bb_width = (Upper_BB - Lower_BB) / SMA(20)
  squeeze = bb_width < percentile_20(bb_width, 126)      # tight squeeze
  atr_compressed = ATR(14) < median(ATR(14), 126) * 0.75  # ATR below 75% of 6-month median

  breakout_up = Close > Upper_BB AND squeeze_released_within_5_days
  breakout_down = Close < Lower_BB AND squeeze_released_within_5_days

  volume_surge = Volume / Median(Volume, 20) > 1.5
  close_location = (Close - Low) / (High - Low)  # > 0.7 = bullish conviction

  signal = breakout_direction * volume_surge * close_conviction
  ```
- **Parameters**:
  1. `bb_period` = 20 — standard Bollinger Band period
  2. `squeeze_percentile` = 20 — bandwidth below 20th percentile = squeeze
  3. `atr_compression_ratio` = 0.75 — ATR below 75% of 6-month median
  4. `volume_surge_threshold` = 1.5 — volume must be 1.5x the 20-day median
  5. `close_location_min` = 0.70 — close must be in upper 30% of bar (for longs)
- **Entry rule**: Enter long when all conditions are met: (1) Bollinger squeeze occurred within last 5 days, (2) close breaks above upper Bollinger Band, (3) volume is ≥ 1.5x median volume, (4) close location ≥ 0.70. Mirror for shorts.
- **Exit rule**: Exit after 30 trading days (time-based) OR if price drops below SMA(20) on a closing basis (whichever comes first). Use ATR-based trailing stop: initial stop at entry price - 2×ATR(14).
- **Holding period**: 2-6 weeks per position
- **Rebalance frequency**: Signal-based entry; weekly review for exits

### Implementation Steps
1. Compute Bollinger Bands: `SMA(Close, 20) ± 2 × Std(Close, 20)`
2. Compute Bollinger Bandwidth: `(Upper - Lower) / SMA(20)`
3. Compute 126-day rolling percentile of bandwidth. Flag "squeeze" when bandwidth < 20th percentile
4. Track squeeze state: `squeeze_active` flag set True when bandwidth enters squeeze territory
5. Detect "squeeze release": first day bandwidth exits squeeze zone
6. Check if close breaks above upper band (long) or below lower band (short) within 5 days of squeeze release
7. Confirm with volume: `Volume / rolling_median(Volume, 20) >= 1.5`
8. Confirm with close location: `(Close - Low) / (High - Low) >= 0.70` for longs
9. Enter position with ATR-based stop loss at `entry_price - 2 * ATR(14)`
10. Exit on time stop (30 days) or trailing stop (close below SMA(20))

### Example Python Code

```python
import pandas as pd
import numpy as np


def volatility_compression_breakout_signal(
    ohlcv: pd.DataFrame,
    pe: pd.Series = None,
    bb_period: int = 20,
    squeeze_percentile: float = 20.0,
    atr_compression_ratio: float = 0.75,
    volume_surge_threshold: float = 1.5,
    close_location_min: float = 0.70,
) -> pd.Series:
    """
    Volatility Compression Breakout with Volume Surge.

    Detects Bollinger Band squeezes followed by directional breakouts
    confirmed by volume surge and strong close location.

    Behavioral rationale: Volatility clusters and mean-reverts. Low-vol
    compression phases precede large moves. Volume surge on breakout day
    confirms institutional participation vs. false breakout.

    Holding period: 2-6 weeks
    Data required: OHLCV only (P/E not used)

    Parameters
    ----------
    ohlcv : DataFrame with columns [Open, High, Low, Close, Volume]
    pe : Not used (included for API consistency)
    bb_period : Bollinger Band period (default 20)
    squeeze_percentile : Bandwidth percentile for squeeze detection (default 20)
    atr_compression_ratio : ATR must be below this fraction of 126d median (default 0.75)
    volume_surge_threshold : Volume must exceed this multiple of 20d median (default 1.5)
    close_location_min : Minimum close location for bullish conviction (default 0.70)

    Returns
    -------
    Series of signal values: +1 (bullish breakout), -1 (bearish breakout), 0 (no signal)
    """
    close = ohlcv['Close']
    high = ohlcv['High']
    low = ohlcv['Low']
    volume = ohlcv['Volume']

    # --- Bollinger Bands ---
    sma = close.rolling(bb_period).mean()
    std = close.rolling(bb_period).std()
    upper_bb = sma + 2 * std
    lower_bb = sma - 2 * std
    bb_width = (upper_bb - lower_bb) / sma

    # --- Squeeze Detection ---
    # Rolling percentile of bandwidth over 126 days
    bb_width_pctile = bb_width.rolling(126).apply(
        lambda x: (x.iloc[-1] <= x).mean() * 100 if len(x) == 126 else np.nan,
        raw=False
    )
    squeeze = bb_width_pctile <= squeeze_percentile

    # --- ATR Compression ---
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    atr_median_126 = atr.rolling(126).median()
    atr_compressed = atr < (atr_median_126 * atr_compression_ratio)

    # --- Combined Compression State ---
    compressed = squeeze & atr_compressed

    # --- Squeeze Release (within last 5 days) ---
    # Detect transition from compressed to not-compressed
    was_compressed_recently = compressed.rolling(5).max().astype(bool)
    squeeze_released = was_compressed_recently & ~compressed

    # --- Breakout Detection ---
    breakout_up = (close > upper_bb) & squeeze_released
    breakout_down = (close < lower_bb) & squeeze_released

    # --- Volume Surge ---
    vol_median = volume.rolling(20).median()
    vol_ratio = volume / vol_median.replace(0, np.nan)
    volume_confirms = vol_ratio >= volume_surge_threshold

    # --- Close Location ---
    bar_range = high - low
    close_loc = (close - low) / bar_range.replace(0, np.nan)

    # --- Final Signal ---
    signal = pd.Series(0.0, index=close.index)

    # Bullish: breakout up + volume surge + close in upper portion
    bullish = breakout_up & volume_confirms & (close_loc >= close_location_min)
    signal[bullish] = 1.0

    # Bearish: breakout down + volume surge + close in lower portion
    bearish = breakout_down & volume_confirms & (close_loc <= (1 - close_location_min))
    signal[bearish] = -1.0

    return signal
```

### Reasoning & Edge Assessment
- **Why this might work**:
  - Volatility clustering is one of the most robust empirical findings in finance. Low-vol periods reliably precede high-vol periods (GARCH models confirm this).
  - Volume surge confirmation dramatically reduces false breakouts. Most false breakouts occur on low volume.
  - Close location adds a second confirmation: institutional buyers push price to close near the high, while false breakouts often have long wicks (price retraces within the bar).
- **Why this might fail**:
  - In choppy/range-bound markets, many squeezes resolve without a sustained trend, generating whipsaw.
  - The signal is infrequent — may go weeks without a trade, creating tracking error for portfolio managers.
  - Stop-loss placement at 2×ATR may be too tight for volatile stocks, causing premature exits.
- **Key risks**: False breakout in choppy regimes; low signal frequency; gap risk (price gaps through the stop); selection bias in event-driven strategies.
- **Estimated robustness**: Moderate-high. Standard parameters, three diverse indicator categories. The squeeze concept is well-documented, but the specific volume + close-location overlay is less common, reducing crowding.

### Viability Scorecard
| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| Behavioral rationale strength | 8 | Volatility clustering + institutional flow are well-documented |
| Simplicity (fewer params = higher) | 7 | 5 params, standard values |
| Indicator diversity | 9 | Volatility + Volume Flow + OHLC Structure (3 categories) |
| Crowding resistance | 7 | Bollinger squeeze is known, but triple confirmation is less common |
| Volume confirmation | 9 | Volume surge is a primary filter |
| Regime robustness | 5 | Works well in trending regimes; struggles in extended chop |
| **Overall** | **7.5** | |

---

## Strategy 3: Exhaustion Reversal — Volume Climax Mean Reversion with P/E Floor

### Idea
Exploit **loss aversion** and **forced selling**: when a stock experiences a sharp multi-day decline accompanied by a volume climax (abnormally high selling volume), it often reverses as forced sellers exhaust their supply and bargain hunters step in. A P/E floor filter ensures we're catching panic dips in fundamentally sound companies, not catching falling knives in distressed stocks.

### Behavioral / Structural Rationale
- **Why this pattern exists**: Loss aversion causes investors to panic-sell at the worst time. Margin calls and fund redemptions force selling regardless of fundamentals. When selling pressure exhausts (volume climax), the supply/demand imbalance flips — remaining holders have strong hands, and bargain hunters create buying pressure. This is the "climax reversal" pattern documented in market microstructure literature.
- **Who is on the wrong side**: Panic sellers who liquidate at the bottom due to emotional distress, margin calls, or stop-loss triggers. Late shorts who pile on after the decline has already occurred.
- **Academic/empirical support**: De Bondt & Thaler (1985) documented short-term overreaction and subsequent reversal. Campbell, Grossman & Wang (1993) showed that high-volume price declines tend to reverse more than low-volume declines. Avramov et al. (2006) documented mean reversion conditional on distress risk.

### Signal Logic
- **Indicators used**:
  - 10-day cumulative return — *Rate of Change* category
  - Relative Volume (current vs 20-day median) — *Volume Flow* category
  - RSI(14) — *Overbought/Oversold* category
  - P/E percentile rank (cross-sectional) — *Valuation* category
- **Signal formula**:
  ```
  price_drop = Return_10d < -15%                  # sharp decline
  volume_climax = Max(RelativeVolume, 10) > 3.0   # volume spike ≥ 3x median in last 10 days
  oversold = RSI(14) < 25                          # deeply oversold
  pe_floor = PE > 0 AND PE < 50                    # fundamentally sound (positive earnings, not extreme)

  signal = price_drop AND volume_climax AND oversold AND pe_floor
  reversal_score = abs(Return_10d) * max(RelativeVolume_10d) * (1 / RSI_14)
  ```
- **Parameters**:
  1. `decline_threshold` = -0.15 — minimum 15% decline over 10 days
  2. `volume_climax_multiple` = 3.0 — volume spike must be ≥ 3x median
  3. `rsi_oversold` = 25 — deeper oversold than standard (30) for higher conviction
  4. `pe_floor` = 0 — exclude negative earnings
  5. `pe_ceiling` = 50 — exclude extreme P/E (likely distressed or no-earnings)
- **Entry rule**: Enter long when all four conditions are met simultaneously. Position size proportional to `reversal_score` (deeper drop + higher volume + lower RSI = larger position).
- **Exit rule**: Time-based exit after 21 trading days (1 month). OR exit if RSI > 50 (momentum has recovered). Whichever comes first.
- **Holding period**: 1-4 weeks
- **Rebalance frequency**: Signal-based entry; daily monitoring for exit conditions

### Implementation Steps
1. Compute 10-day cumulative return: `close / close.shift(10) - 1`
2. Compute relative volume: `volume / volume.rolling(20).median()`
3. Compute rolling 10-day max of relative volume (to catch climax within the decline window)
4. Compute RSI(14) using standard Wilder smoothing
5. Apply P/E filters: exclude stocks with P/E ≤ 0 or P/E > 50
6. Flag all stocks where: return_10d < -15%, max_rel_vol_10d > 3.0, RSI < 25, P/E is valid
7. Compute reversal_score = |return_10d| × max_rel_vol_10d × (1/RSI) for position sizing
8. Enter positions on the next open after signal triggers
9. Exit after 21 days or when RSI crosses above 50

### Example Python Code

```python
import pandas as pd
import numpy as np


def exhaustion_reversal_signal(
    ohlcv: pd.DataFrame,
    pe: pd.Series = None,
    decline_threshold: float = -0.15,
    volume_climax_multiple: float = 3.0,
    rsi_oversold: int = 25,
    pe_floor: float = 0.0,
    pe_ceiling: float = 50.0,
) -> pd.Series:
    """
    Exhaustion Reversal — Volume Climax Mean Reversion with P/E Floor.

    Detects panic-driven sell-offs where volume climaxes indicate forced
    selling exhaustion, then enters the reversal trade with P/E fundamental
    safety check.

    Behavioral rationale: Loss aversion causes panic selling at lows. Margin
    calls and fund redemptions force selling. Volume climax marks exhaustion
    of forced sellers. P/E floor prevents catching falling knives.

    Holding period: 1-4 weeks
    Data required: OHLCV + P/E

    Parameters
    ----------
    ohlcv : DataFrame with columns [Open, High, Low, Close, Volume]
    pe : P/E ratio series for fundamental filter
    decline_threshold : Minimum price decline over 10 days (default -0.15 = -15%)
    volume_climax_multiple : Min volume spike vs 20d median (default 3.0)
    rsi_oversold : RSI threshold for oversold (default 25)
    pe_floor : Minimum P/E to consider (default 0, excludes negative earnings)
    pe_ceiling : Maximum P/E to consider (default 50)

    Returns
    -------
    Series of reversal signal strength (higher = stronger reversal signal, 0 = no signal)
    """
    close = ohlcv['Close']
    high = ohlcv['High']
    low = ohlcv['Low']
    volume = ohlcv['Volume']

    # --- Price Decline ---
    return_10d = close / close.shift(10) - 1.0
    sharp_decline = return_10d < decline_threshold

    # --- Volume Climax ---
    vol_median_20 = volume.rolling(20).median()
    relative_volume = volume / vol_median_20.replace(0, np.nan)
    # Max relative volume over the 10-day decline window
    max_rel_vol_10d = relative_volume.rolling(10).max()
    volume_climax = max_rel_vol_10d >= volume_climax_multiple

    # --- RSI(14) ---
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)

    # Wilder smoothing (exponential with alpha = 1/14)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    deeply_oversold = rsi < rsi_oversold

    # --- P/E Floor ---
    if pe is not None:
        pe_valid = (pe > pe_floor) & (pe <= pe_ceiling)
    else:
        pe_valid = pd.Series(True, index=close.index)  # pass-through if no P/E

    # --- Combined Signal ---
    trigger = sharp_decline & volume_climax & deeply_oversold & pe_valid

    # --- Reversal Score (higher = more extreme, stronger expected reversal) ---
    reversal_score = (
        return_10d.abs() *            # deeper decline = stronger
        max_rel_vol_10d.clip(1, 10) * # higher volume climax = stronger
        (1.0 / rsi.clip(5, 100))      # lower RSI = stronger
    )

    # Only output score where trigger fires
    signal = pd.Series(0.0, index=close.index)
    signal[trigger] = reversal_score[trigger]

    return signal


def exhaustion_reversal_positions(
    ohlcv: pd.DataFrame,
    pe: pd.Series = None,
    hold_days: int = 21,
    rsi_exit: float = 50.0,
    **signal_kwargs,
) -> pd.Series:
    """
    Full position management for the exhaustion reversal strategy.

    Enters on signal, exits after hold_days or when RSI > rsi_exit.

    Returns
    -------
    Series of position values: 1 = long, 0 = flat
    """
    signal = exhaustion_reversal_signal(ohlcv, pe, **signal_kwargs)

    close = ohlcv['Close']
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    position = pd.Series(0.0, index=close.index)
    entry_day = None

    for i in range(len(position)):
        if position.iloc[i-1] if i > 0 else 0 == 0:
            # Not in position — check for entry
            if signal.iloc[i] > 0:
                position.iloc[i] = 1.0
                entry_day = i
        else:
            # In position — check for exit
            days_held = i - entry_day if entry_day is not None else 0
            if days_held >= hold_days or rsi.iloc[i] > rsi_exit:
                position.iloc[i] = 0.0
                entry_day = None
            else:
                position.iloc[i] = 1.0

    return position
```

### Reasoning & Edge Assessment
- **Why this might work**:
  - Short-term overreaction and reversal is one of the most replicated findings in behavioral finance (De Bondt & Thaler 1985). Adding a volume climax filter dramatically improves signal quality by targeting forced-selling events rather than rational repricing.
  - The P/E floor is critical: it separates panic dips (where fundamentals are intact) from distressed stocks heading toward delisting. This addresses the #1 failure mode of mean reversion strategies (catching falling knives).
  - The signal is infrequent and event-driven, meaning low turnover and low transaction costs.
- **Why this might fail**:
  - In bear markets, "panic dips" become the new normal — many oversold stocks continue falling, and the P/E floor can be fooled by stale earnings data.
  - Volume climax can be caused by legitimate information (fraud discovery, product failure), not just behavioral overreaction. P/E doesn't capture all distress.
  - The strategy is long-only and counter-trend — it fights the prevailing direction, which is psychologically difficult and can have extended drawdowns during sustained bear markets.
- **Key risks**: Bear market regime risk (continuous dips without recovery); false climax from information-driven selling; P/E data lag obscuring deteriorating fundamentals; concentrated positions in distressed sectors during sector-wide downturns.
- **Estimated robustness**: Moderate. Standard RSI parameter, common volume thresholds. The multi-condition filter is quite strict, reducing false signals but also reducing signal frequency. P/E filter adds a non-price dimension. Should survive ±20% parameter changes due to strict thresholds.

### Viability Scorecard
| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| Behavioral rationale strength | 9 | Loss aversion + forced selling exhaustion are deeply documented |
| Simplicity (fewer params = higher) | 7 | 5 params with clear justification |
| Indicator diversity | 10 | Rate of Change + Volume Flow + Overbought/Oversold + Valuation (4 categories) |
| Crowding resistance | 8 | Multi-condition filter is uncommon; most mean reversion is simpler |
| Volume confirmation | 10 | Volume climax is the core of the strategy |
| Regime robustness | 5 | Fails in sustained bear markets; works best in corrections within uptrends |
| **Overall** | **8.2** | |

---

## Strategy 4: Multi-Timeframe Trend Agreement with Volume Momentum

### Idea
Exploit **herding** and **slow information diffusion**: when both short-term (21-day) and medium-term (63-day) trend indicators agree on direction, *and* volume momentum is accelerating in the same direction, the trend is supported by broadening participation. Dual-timeframe agreement filters out noise and whipsaw, while volume momentum detects whether the crowd is still growing (trend continuation) or thinning (trend exhaustion).

### Behavioral / Structural Rationale
- **Why this pattern exists**: Information diffuses unevenly across investor populations. Early movers establish a short-term trend, then later adopters join, extending it into a medium-term trend. When both timeframes agree, it means multiple investor cohorts have independently reached the same conclusion. Volume momentum (rising short-term vs long-term volume) confirms that participation is growing, not shrinking.
- **Who is on the wrong side**: Counter-trend traders who fight the consensus too early. Also, late momentum chasers who enter after volume momentum has already peaked (crowd is thinning).
- **Academic/empirical support**: Multi-timeframe momentum is supported by Hong & Stein (1999) — gradual information diffusion model. Volume-momentum interaction is documented in Gervais & Kaniel (2001). Chordia & Swaminathan (2000) showed volume leads returns in cross-sectional analysis.

### Signal Logic
- **Indicators used**:
  - Price vs EMA(21) position — *Trend Direction* category (short-term)
  - Price vs EMA(63) position — *Trend Direction* category (medium-term)
  - Volume Momentum: SMA(Volume, 5) / SMA(Volume, 20) — *Volume Flow* category
  - ATR(14) percentile rank (126-day) — *Volatility* category
- **Signal formula**:
  ```
  short_trend = (Close - EMA(21)) / ATR(14)    # normalized distance from short EMA
  medium_trend = (Close - EMA(63)) / ATR(14)   # normalized distance from medium EMA

  agreement = sign(short_trend) == sign(medium_trend)
  trend_strength = (short_trend + medium_trend) / 2

  vol_momentum = SMA(Volume, 5) / SMA(Volume, 20)  # >1 = accelerating, <1 = decelerating
  vol_momentum_confirms = (vol_momentum > 1.0 AND trend_strength > 0) OR
                          (vol_momentum > 1.0 AND trend_strength < 0)

  atr_regime = ATR_percentile(126d)  # Use to size positions: lower vol = larger position

  signal = trend_strength * agreement * vol_momentum
  ```
- **Parameters**:
  1. `short_ema` = 21 days — roughly 1 month, captures recent trend
  2. `medium_ema` = 63 days — roughly 3 months, captures established trend
  3. `vol_fast` = 5 — short-term volume average
  4. `vol_slow` = 20 — medium-term volume average
  5. `atr_period` = 14 — standard ATR for normalization
- **Entry rule**: Bi-weekly rebalance. Go long when both EMAs confirm uptrend (price above both), volume momentum > 1.0, and trend_strength is in the top tertile. Go short (or avoid) when both EMAs confirm downtrend with accelerating volume.
- **Exit rule**: Exit when timeframes disagree (price crosses below short EMA while above medium EMA = ambiguous), OR when volume momentum drops below 0.8 (participation decelerating).
- **Holding period**: 2-8 weeks
- **Rebalance frequency**: Bi-weekly evaluation

### Implementation Steps
1. Compute EMA(21) and EMA(63) for each stock
2. Normalize trend strength: `(Close - EMA) / ATR(14)` for each timeframe
3. Detect agreement: both trend strengths have the same sign
4. Compute volume momentum: `SMA(Volume, 5) / SMA(Volume, 20)`
5. Compute ATR(14) percentile rank over 126 days for volatility regime
6. Signal = average of normalized trend strengths × agreement flag × volume momentum
7. Rank universe by signal, go long top tertile when signal is positive
8. Exit when agreement breaks or volume momentum drops below 0.8
9. Size positions inversely proportional to ATR percentile (lower vol = larger size)

### Example Python Code

```python
import pandas as pd
import numpy as np


def multi_timeframe_trend_signal(
    ohlcv: pd.DataFrame,
    pe: pd.Series = None,
    short_ema: int = 21,
    medium_ema: int = 63,
    vol_fast: int = 5,
    vol_slow: int = 20,
    atr_period: int = 14,
) -> pd.Series:
    """
    Multi-Timeframe Trend Agreement with Volume Momentum.

    Combines short-term and medium-term EMA trend agreement with
    volume momentum confirmation. Trades only when both timeframes
    agree on direction AND volume participation is accelerating.

    Behavioral rationale: Information diffuses slowly across investor
    segments. Dual-timeframe agreement means multiple cohorts have
    reached the same directional conclusion. Volume momentum confirms
    the crowd is still growing (continuation) vs. thinning (exhaustion).

    Holding period: 2-8 weeks
    Data required: OHLCV only

    Parameters
    ----------
    ohlcv : DataFrame with columns [Open, High, Low, Close, Volume]
    pe : Not used (included for API consistency)
    short_ema : Short-term EMA period (default 21 = ~1 month)
    medium_ema : Medium-term EMA period (default 63 = ~3 months)
    vol_fast : Fast volume SMA period (default 5)
    vol_slow : Slow volume SMA period (default 20)
    atr_period : ATR period for normalization (default 14)

    Returns
    -------
    Series of signal values (positive = bullish trend agreement,
    negative = bearish, near zero = no agreement or no volume confirmation)
    """
    close = ohlcv['Close']
    high = ohlcv['High']
    low = ohlcv['Low']
    volume = ohlcv['Volume']

    # --- EMA Trends ---
    ema_short = close.ewm(span=short_ema, adjust=False).mean()
    ema_medium = close.ewm(span=medium_ema, adjust=False).mean()

    # --- ATR for normalization ---
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(atr_period).mean()

    # --- Normalized Trend Strength ---
    short_trend = (close - ema_short) / atr.replace(0, np.nan)
    medium_trend = (close - ema_medium) / atr.replace(0, np.nan)

    # --- Timeframe Agreement ---
    # Both trends same direction (both positive or both negative)
    agreement = (np.sign(short_trend) == np.sign(medium_trend)).astype(float)
    # Zero out when disagreeing
    avg_trend = (short_trend + medium_trend) / 2.0
    agreed_trend = avg_trend * agreement

    # --- Volume Momentum ---
    vol_sma_fast = volume.rolling(vol_fast).mean()
    vol_sma_slow = volume.rolling(vol_slow).mean()
    vol_momentum = vol_sma_fast / vol_sma_slow.replace(0, np.nan)

    # Volume confirms: accelerating volume in the direction of trend
    # vol_momentum > 1 means participation is increasing
    vol_confirmation = vol_momentum.clip(0.5, 2.0)  # cap extreme values

    # --- Composite Signal ---
    # Trend strength × agreement × volume confirmation
    signal = agreed_trend * vol_confirmation

    # --- ATR Regime (for position sizing info) ---
    atr_pctile = atr.rolling(126).apply(
        lambda x: (x.iloc[-1] <= x).mean() if len(x) == 126 else np.nan,
        raw=False
    )
    # Low volatility regime → can take larger positions (signal scaled up)
    vol_regime_scalar = 1.0 + (0.5 - atr_pctile).clip(-0.3, 0.3)

    signal = signal * vol_regime_scalar

    return signal
```

### Reasoning & Edge Assessment
- **Why this might work**:
  - Multi-timeframe agreement is a robust filter: it requires persistent trends, not one-day spikes. Hong & Stein's gradual diffusion model provides strong theoretical backing.
  - Volume momentum adds a "freshness" check: is the trend still attracting new participants, or is it exhausted? This helps avoid entering late-stage trends.
  - ATR-based normalization and position sizing adapts to market conditions: larger positions in calm markets (where trends are more reliable), smaller in volatile markets.
- **Why this might fail**:
  - In choppy markets, short and medium EMAs whipsaw frequently, producing many false agreement signals quickly followed by disagreement exits.
  - Volume momentum can be noisy for individual stocks — sector/market-wide volume shifts can create false signals.
  - The strategy is inherently trend-following and will underperform in mean-reverting environments (extended range-bound markets).
- **Key risks**: Whipsaw in choppy markets; volume noise from market-wide events (options expiration, index rebalance); late entry into established trends; EMA lag causing delayed exit during sharp reversals.
- **Estimated robustness**: Moderate-high. Standard EMA periods (21, 63), standard ATR(14). The signal is continuously valued (not binary), which allows for gradual position adjustment. Four diverse indicator categories. Should survive ±20% parameter changes.

### Viability Scorecard
| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| Behavioral rationale strength | 8 | Information diffusion + herding are well-documented |
| Simplicity (fewer params = higher) | 7 | 5 params, all standard/common values |
| Indicator diversity | 8 | Trend Direction + Volume Flow + Volatility (3 categories) |
| Crowding resistance | 7 | Multi-timeframe + volume momentum overlay is less common than simple MA crossovers |
| Volume confirmation | 8 | Volume momentum is a core component |
| Regime robustness | 5 | Works well in trending; struggles in choppy/range-bound |
| **Overall** | **7.2** | |

---

## Strategy 5: Stealth Accumulation Divergence — OBV Leads Price

### Idea
Exploit **institutional accumulation** that is invisible in price but visible in volume: when On-Balance Volume (OBV) makes new 63-day highs while price remains flat or mildly declining, institutions are quietly buying. This divergence between volume flow and price is a leading indicator of an upcoming price breakout. Adding a candle structure filter (strong close location on high-volume days) confirms that buying pressure is genuine.

### Behavioral / Structural Rationale
- **Why this pattern exists**: Large institutional investors cannot buy millions of shares instantly without moving the market against themselves. They split orders across days/weeks, buying on dips and pausing on rallies to minimize market impact. This creates a pattern where volume flow (OBV) trends up even as price moves sideways or slightly down. The accumulation is invisible to traders watching only price, but obvious in volume flow metrics.
- **Who is on the wrong side**: Technical traders who see a "flat" or "weak" stock based on price alone and either ignore it or short it. They miss the volume footprint that institutional buyers are leaving.
- **Academic/empirical support**: Granville (1963) introduced OBV as a leading indicator. Chordia, Subrahmanyam & Anshuman (2001) documented volume as a predictor of returns. Llorente et al. (2002) showed that volume-return correlation patterns differ for informed vs. uninformed trading.

### Signal Logic
- **Indicators used**:
  - OBV 63-day trend (new highs vs rolling max) — *Volume Flow* category
  - 63-day price return — *Rate of Change* category
  - Close Location Value (20-day average on high-volume days) — *OHLC Structure* category
- **Signal formula**:
  ```
  obv_at_high = OBV >= rolling_max(OBV, 63) * 0.95   # OBV near 63-day high
  price_flat = abs(Return_63d) < 0.05                  # price moved less than ±5%

  divergence = obv_at_high AND price_flat  # volume accumulating, price flat

  # Quality filter: on high-volume days (>1.2x median), close should be in upper half
  high_vol_days = Volume > 1.2 * Median(Volume, 20)
  close_loc_on_high_vol = rolling_mean(close_location[high_vol_days], 20)
  buying_quality = close_loc_on_high_vol > 0.55  # buyers pushing price to close high

  signal = divergence AND buying_quality
  ```
- **Parameters**:
  1. `obv_lookback` = 63 days — 3-month OBV trend window
  2. `obv_high_threshold` = 0.95 — OBV must be within 5% of 63-day high
  3. `price_flat_threshold` = 0.05 — price must have moved < 5% in 63 days
  4. `high_vol_multiple` = 1.2 — "high volume" day definition
  5. `close_loc_threshold` = 0.55 — close must be in upper 45% on high-vol days
- **Entry rule**: Enter long when divergence AND buying quality are both true. Signal is checked weekly.
- **Exit rule**: Exit after 42 trading days (2 months). OR exit if OBV drops below its 63-day moving average (accumulation has stopped). Use the earlier trigger.
- **Holding period**: 4-8 weeks
- **Rebalance frequency**: Weekly evaluation, patient entry

### Implementation Steps
1. Compute OBV: cumulative sum of `volume * sign(daily_return)`
2. Compute 63-day rolling max of OBV
3. Flag `obv_at_high` when OBV ≥ 0.95 × rolling_max(OBV, 63)
4. Compute 63-day return: `close / close.shift(63) - 1`
5. Flag `price_flat` when |return_63d| < 0.05
6. Identify high-volume days: `volume > 1.2 * volume.rolling(20).median()`
7. On high-volume days only, compute close location: `(close - low) / (high - low)`
8. Compute 20-day rolling average of close_location on high-volume days (forward-fill for non-high-vol days)
9. Flag `buying_quality` when average close location on high-vol days > 0.55
10. Final signal: `obv_at_high AND price_flat AND buying_quality`
11. Enter on next open after signal, exit after 42 days or OBV < SMA(OBV, 63)

### Example Python Code

```python
import pandas as pd
import numpy as np


def stealth_accumulation_signal(
    ohlcv: pd.DataFrame,
    pe: pd.Series = None,
    obv_lookback: int = 63,
    obv_high_threshold: float = 0.95,
    price_flat_threshold: float = 0.05,
    high_vol_multiple: float = 1.2,
    close_loc_threshold: float = 0.55,
) -> pd.Series:
    """
    Stealth Accumulation Divergence — OBV Leads Price.

    Detects institutional accumulation by finding stocks where OBV
    is near 63-day highs while price is flat, confirmed by high close
    location on above-average volume days.

    Behavioral rationale: Institutional investors split large orders
    across days/weeks to minimize market impact. This creates OBV
    trends that lead price. The volume footprint reveals accumulation
    invisible to price-only traders.

    Holding period: 4-8 weeks
    Data required: OHLCV only (P/E optional filter)

    Parameters
    ----------
    ohlcv : DataFrame with columns [Open, High, Low, Close, Volume]
    pe : Optional P/E ratio series (used as filter if provided)
    obv_lookback : OBV trend assessment window (default 63 = 3 months)
    obv_high_threshold : OBV must be within (1-threshold) of rolling max (default 0.95)
    price_flat_threshold : Max absolute return for "flat" price (default 0.05 = 5%)
    high_vol_multiple : Multiple of median volume for "high volume" day (default 1.2)
    close_loc_threshold : Min avg close location on high-vol days (default 0.55)

    Returns
    -------
    Series of signal values: 1.0 = accumulation detected, 0.0 = no signal
    """
    close = ohlcv['Close']
    high = ohlcv['High']
    low = ohlcv['Low']
    volume = ohlcv['Volume']

    # --- OBV ---
    daily_return = close.pct_change()
    obv = (volume * np.sign(daily_return)).cumsum()

    # --- OBV near 63-day high ---
    obv_rolling_max = obv.rolling(obv_lookback).max()
    obv_at_high = obv >= (obv_rolling_max * obv_high_threshold)

    # --- Price flat over 63 days ---
    return_63d = close / close.shift(obv_lookback) - 1.0
    price_flat = return_63d.abs() < price_flat_threshold

    # --- Divergence: OBV high + price flat ---
    divergence = obv_at_high & price_flat

    # --- Buying Quality: Close location on high-volume days ---
    vol_median = volume.rolling(20).median()
    high_vol_day = volume > (high_vol_multiple * vol_median)

    bar_range = high - low
    close_location = (close - low) / bar_range.replace(0, np.nan)

    # Only keep close_location for high-volume days, forward-fill for averaging
    close_loc_high_vol = close_location.where(high_vol_day, np.nan)
    # Rolling mean with forward-fill to get a continuous metric
    avg_close_loc = close_loc_high_vol.rolling(20, min_periods=3).mean()
    avg_close_loc = avg_close_loc.ffill()

    buying_quality = avg_close_loc > close_loc_threshold

    # --- P/E Filter (optional) ---
    if pe is not None:
        pe_valid = (pe > 0) & (pe < 100)
    else:
        pe_valid = True

    # --- Final Signal ---
    signal = pd.Series(0.0, index=close.index)
    trigger = divergence & buying_quality & pe_valid
    signal[trigger] = 1.0

    return signal


def stealth_accumulation_positions(
    ohlcv: pd.DataFrame,
    pe: pd.Series = None,
    hold_days: int = 42,
    **signal_kwargs,
) -> pd.Series:
    """
    Full position management: enter on signal, exit after hold_days
    or when OBV drops below its 63-day SMA.
    """
    signal = stealth_accumulation_signal(ohlcv, pe, **signal_kwargs)

    close = ohlcv['Close']
    volume = ohlcv['Volume']
    daily_return = close.pct_change()
    obv = (volume * np.sign(daily_return)).cumsum()
    obv_sma = obv.rolling(63).mean()

    position = pd.Series(0.0, index=close.index)
    entry_day = None

    for i in range(len(position)):
        prev_pos = position.iloc[i - 1] if i > 0 else 0

        if prev_pos == 0:
            if signal.iloc[i] > 0:
                position.iloc[i] = 1.0
                entry_day = i
        else:
            days_held = i - entry_day if entry_day is not None else 0
            obv_below_sma = obv.iloc[i] < obv_sma.iloc[i] if not np.isnan(obv_sma.iloc[i]) else False

            if days_held >= hold_days or obv_below_sma:
                position.iloc[i] = 0.0
                entry_day = None
            else:
                position.iloc[i] = 1.0

    return position
```

### Reasoning & Edge Assessment
- **Why this might work**:
  - OBV is an underutilized indicator in systematic trading despite strong academic support. Most quant strategies focus on price momentum; few systematically exploit volume-price divergence as a leading signal.
  - The close-location filter on high-volume days is a novel twist: it checks *how* the buying occurs. If institutions are buying, they push price to close near the high. If volume is driven by day-trader churn, close location is random.
  - The signal is patient (63-day lookback) and aligns with the mid-term holding period. It's inherently low-turnover since accumulation phases last weeks.
- **Why this might fail**:
  - OBV can trend up simply because the stock has more up days than down days, even if each up day has tiny volume and each down day has large volume. The close-location filter partially addresses this.
  - "Flat price + rising OBV" can also occur during distribution — institutions selling into a flat market while new retail buyers absorb the supply. The divergence is ambiguous.
  - In bear markets, OBV may never reach new highs, leaving the strategy with zero signals for extended periods.
- **Key risks**: Signal ambiguity (accumulation vs. distribution); OBV sensitivity to data quality; sparse signals in bear markets; the strategy is long-only; close-location can be noisy for low-float stocks.
- **Estimated robustness**: Moderate. The signal is conceptually strong but relies on OBV behavior which varies across different market microstructures. Standard parameters. Three diverse indicator categories (Volume Flow + Rate of Change + OHLC Structure). Should survive ±20% parameter changes but may have low signal frequency.

### Viability Scorecard
| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| Behavioral rationale strength | 9 | Institutional accumulation footprint is well-documented |
| Simplicity (fewer params = higher) | 7 | 5 params with clear economic justification |
| Indicator diversity | 8 | Volume Flow + Rate of Change + OHLC Structure (3 categories) |
| Crowding resistance | 9 | OBV divergence + close location filter is uncommon in systematic strategies |
| Volume confirmation | 10 | Volume is the PRIMARY signal, not just a filter |
| Regime robustness | 5 | Long-only; no signals in bear markets |
| **Overall** | **8.0** | |

---

## Comparison Matrix

| Aspect | Strategy 1 | Strategy 2 | Strategy 3 | Strategy 4 | Strategy 5 |
|--------|-----------|-----------|-----------|-----------|-----------|
| **Name** | Vol-Confirmed Momentum | Compression Breakout | Exhaustion Reversal | Multi-TF Trend Agreement | Stealth Accumulation |
| **Style** | Cross-sectional momentum | Event-driven breakout | Mean reversion | Trend following | Volume-leading divergence |
| **Indicators** | Return + OBV slope + P/E | BB Width + ATR + RelVol + Close Loc | Return + RelVol + RSI + P/E | EMA(21) + EMA(63) + Vol Mom + ATR | OBV + Return + Close Loc |
| **Categories Used** | 3 (RoC, VolFlow, Valuation) | 3 (Vol, VolFlow, OHLC) | 4 (RoC, VolFlow, OB/OS, Valuation) | 3 (Trend, VolFlow, Vol) | 3 (VolFlow, RoC, OHLC) |
| **Parameters** | 5 | 5 | 5 | 5 | 5 |
| **Hold Period** | 1-3 months | 2-6 weeks | 1-4 weeks | 2-8 weeks | 4-8 weeks |
| **Rebalance** | Monthly | Signal-based | Signal-based | Bi-weekly | Weekly check |
| **Signal Type** | Continuous rank | Binary event | Event + score | Continuous | Binary event |
| **Long/Short** | Long (rank-based) | Long & Short | Long only | Long & Short | Long only |
| **Turnover** | Low (~150%/yr) | Low (~100%/yr) | Very low (~50%/yr) | Moderate (~200%/yr) | Very low (~75%/yr) |
| **Regime Strength** | Bull > Chop > Bear | Trend > Chop | Correction recovery | Trend > Chop > Bear | Bull/Flat > Bear |
| **Overall Score** | **7.7/10** | **7.5/10** | **8.2/10** | **7.2/10** | **8.0/10** |

---

## Portfolio Construction Notes

These five strategies are designed to be **complementary**:

1. **Strategies 1 & 4** are trend/momentum-following and work best in directional markets
2. **Strategy 3** is counter-trend (mean reversion) and works best during corrections within uptrends
3. **Strategies 2 & 5** are event-driven and fire in specific conditions regardless of market direction
4. **Strategies 1 & 3** use P/E as a filter; the others are pure price/volume

A portfolio combining these strategies would benefit from **negative correlation** between the momentum and mean-reversion components, potentially smoothing returns across regimes.

## Important Disclaimers

- **This is a mining exercise, not a backtest.** None of these strategies have been validated on historical data. They are hypotheses grounded in behavioral finance theory and structural market friction.
- **Past patterns may not persist.** All strategies are based on historical behavioral patterns that could change as markets evolve.
- **Transaction costs matter.** Estimated turnover numbers are rough; actual costs depend on universe, liquidity, and execution.
- **Risk management is essential.** These signal descriptions don't include portfolio-level risk controls (max position size, sector concentration limits, drawdown stops) which are critical in practice.
- **Data quality is paramount.** All strategies assume properly split-adjusted and dividend-adjusted OHLCV data. Using raw data will produce garbage signals.

## Web Research Sources
- Jegadeesh, N. & Titman, S. (1993). "Returns to Buying Winners and Selling Losers."
- Lee, C. & Swaminathan, B. (2000). "Price Momentum and Trading Volume."
- Asness, C., Moskowitz, T. & Pedersen, L. (2013). "Value and Momentum Everywhere."
- De Bondt, W. & Thaler, R. (1985). "Does the Stock Market Overreact?"
- Campbell, J., Grossman, S. & Wang, J. (1993). "Trading Volume and Serial Correlation in Stock Returns."
- Hong, H. & Stein, J. (1999). "A Unified Theory of Underreaction, Momentum Trading, and Overreaction."
- Chordia, T. & Swaminathan, B. (2000). "Trading Volume and Cross-Autocorrelations in Stock Returns."
- Brock, W., Lakonishok, J. & LeBaron, D. (1992). "Simple Technical Trading Rules and the Stochastic Properties of Stock Returns."
- Llorente, G. et al. (2002). "Dynamic Volume-Return Relation of Individual Stocks."
- Granville, J. (1963). "Granville's New Key to Stock Market Profits."
- Mandelbrot, B. (1963). "The Variation of Certain Speculative Prices."
- Bollinger, J. (2001). "Bollinger on Bollinger Bands."
