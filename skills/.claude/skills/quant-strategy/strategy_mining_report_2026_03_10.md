# Strategy Mining Report
**Date**: 2026-03-10
**Request**: Mine useful mid-term quant trading strategies based on price and volume data; holding period of several days minimum, no intra-day trading.
**Data Constraint**: OHLCV + P/E only

---

## Strategy 1: Volatility Compression Breakout with Volume Ignition & P/E Floor

### Idea
Markets alternate between compression (low volatility) and expansion (high volatility). When ATR contracts to an abnormally low level, it signals a coiling market where a large directional move is imminent. This strategy detects tight-range compression periods, then enters when a high-volume expansion bar fires in a clear direction — but only for stocks with reasonable valuations (P/E filter), avoiding breakouts in hyper-speculative names.

### Behavioral / Structural Rationale
- **Why this pattern exists**: Volatility clustering (GARCH effect) is one of the strongest empirical regularities in finance. Low-vol periods precede high-vol periods because uncertainty accumulates during quiet periods — information arrives but price doesn't adjust, creating a coiled spring. When a catalyst finally moves price, the pent-up positioning unwinds rapidly.
- **Who is on the wrong side**: Mean-reversion traders who sell the breakout expecting price to return to the recent range. Also, short-volatility sellers who have been collecting premium during the compression and get squeezed when vol explodes.
- **Academic/empirical support**: Mandelbrot's volatility clustering; GARCH models (Bollerslev 1986); "Squeeze" concept from John Carter's work; empirical evidence that Bollinger Band width minima precede large moves (Bollinger 2002).

### Signal Logic
- **Indicators used**:
  - ATR(14) / Close — normalized volatility (Category 4: Volatility)
  - Volume Ratio = Volume / SMA(Volume, 20) — relative activity (Category 5: Volume Flow)
  - Close Location Value = (Close - Low) / (High - Low) — directional conviction (Category 6: OHLC Structure)
  - P/E percentile rank — valuation floor (Category 7: Valuation)

- **Signal formula**:
  1. **Compression Detection**: ATR(14)/Close falls below its 20th percentile of its own trailing 126-day distribution (6-month lookback).
  2. **Expansion Trigger**: On the first day where True Range > 1.5× ATR(14) AND Volume Ratio > 2.0, a breakout is confirmed.
  3. **Direction**: If Close Location Value > 0.7 on the expansion day → Long. If CLV < 0.3 → Short.
  4. **P/E Filter**: Only enter Long if P/E rank < 0.7 (not in the most expensive 30%). Only enter Short if P/E rank > 0.3 (not in the cheapest 30%).

- **Parameters** (4 total):
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `atr_lookback` | 14 | ATR computation window |
  | `compression_pct` | 20 | Percentile threshold for compression detection |
  | `expansion_mult` | 1.5 | True Range must exceed this × ATR to trigger |
  | `volume_mult` | 2.0 | Volume must exceed this × 20-day SMA to confirm |

- **Entry rule**: Enter long (short) on the close of the expansion day when compression + expansion trigger + directional CLV + P/E filter all align.
- **Exit rule**: Time-based exit after 15 trading days, OR trailing stop at 2× ATR(14) from entry price, whichever comes first.
- **Holding period**: 5–20 trading days (1–4 weeks)
- **Rebalance frequency**: Signal-based (event-driven); check daily for new compression-expansion setups.

### Implementation Steps
1. Compute ATR(14) for each stock; normalize by dividing by Close price to get percentage ATR.
2. Compute the rolling 126-day percentile of the normalized ATR. Identify days where this percentile drops below the 20th percentile — mark stock as "compressed."
3. While a stock is compressed, monitor daily for an expansion trigger: True Range > 1.5 × ATR(14) AND Volume / SMA(Volume, 20) > 2.0.
4. On the expansion day, compute Close Location Value = (Close − Low) / (High − Low). If CLV > 0.7 → bullish direction; CLV < 0.3 → bearish direction.
5. Apply P/E filter: for longs, require P/E percentile < 0.7; for shorts, require P/E percentile > 0.3.
6. Enter position at the close of the expansion day.
7. Exit after 15 trading days or when price hits trailing stop of 2× ATR from the highest close since entry (for longs) or lowest close since entry (for shorts).

### Example Python Code

```python
import pandas as pd
import numpy as np

def volatility_compression_breakout_signal(
    ohlcv: pd.DataFrame,
    pe: pd.Series | None = None,
    atr_lookback: int = 14,
    compression_pct: int = 20,
    expansion_mult: float = 1.5,
    volume_mult: float = 2.0,
) -> pd.Series:
    """
    Volatility Compression Breakout with Volume Ignition & P/E Floor.

    Detects stocks in abnormally low-volatility compression, then triggers
    on high-volume expansion days with directional conviction.

    Behavioral rationale: Volatility clusters — low-vol periods precede
    explosive moves as pent-up uncertainty unwinds.
    Holding period: 5-20 trading days.
    Data required: OHLCV + P/E only.

    Parameters
    ----------
    ohlcv : DataFrame with columns [Open, High, Low, Close, Volume]
    pe : Optional P/E ratio series
    atr_lookback : ATR computation window (default 14)
    compression_pct : Percentile threshold for low-vol detection (default 20)
    expansion_mult : TR must exceed this × ATR to trigger (default 1.5)
    volume_mult : Volume must exceed this × 20d SMA (default 2.0)

    Returns
    -------
    Series of signal values: +1 (long), -1 (short), 0 (no signal)
    """
    high = ohlcv['High']
    low = ohlcv['Low']
    close = ohlcv['Close']
    volume = ohlcv['Volume']
    open_ = ohlcv['Open']

    # --- Step 1: Compute ATR(14), normalized by close ---
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)

    atr = tr.rolling(atr_lookback).mean()
    norm_atr = atr / close  # Percentage ATR

    # --- Step 2: Rolling percentile of normalized ATR (126-day window) ---
    def rolling_percentile(series, window=126):
        return series.rolling(window).apply(
            lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
        )

    atr_pct = rolling_percentile(norm_atr, window=126)
    is_compressed = atr_pct < (compression_pct / 100.0)

    # --- Step 3: Expansion trigger ---
    is_expansion = (tr > expansion_mult * atr)

    # --- Step 4: Volume confirmation ---
    vol_sma = volume.rolling(20).mean()
    vol_ratio = volume / vol_sma
    high_volume = vol_ratio > volume_mult

    # --- Step 5: Close Location Value for direction ---
    clv = (close - low) / (high - low + 1e-10)

    # --- Step 6: Combine into signal ---
    trigger = is_compressed.shift(1) & is_expansion & high_volume

    signal = pd.Series(0.0, index=ohlcv.index)
    signal[trigger & (clv > 0.7)] = 1.0   # Bullish expansion
    signal[trigger & (clv < 0.3)] = -1.0  # Bearish expansion

    # --- Step 7: P/E filter (if available) ---
    if pe is not None:
        pe_clean = pe.copy()
        pe_clean[pe_clean <= 0] = np.nan
        pe_clean[pe_clean > 200] = np.nan
        pe_rank = pe_clean.rank(pct=True)

        # For longs: reject most expensive 30%
        signal[(signal > 0) & (pe_rank > 0.7)] = 0.0
        # For shorts: reject cheapest 30%
        signal[(signal < 0) & (pe_rank < 0.3)] = 0.0

    return signal
```

### Reasoning & Edge Assessment
- **Why this might work**:
  - Volatility clustering is one of the most robust empirical facts in finance — low vol reliably precedes high vol.
  - Volume confirmation filters out false breakouts (price-only breakouts from compression fail ~50% of the time; volume-confirmed breakouts have higher continuation rates).
  - P/E filter prevents buying into bubble breakouts where upside is already priced in.

- **Why this might fail**:
  - In persistently low-volatility environments (e.g., 2017), the compression signal fires constantly but expansions are weak and mean-revert quickly.
  - High-volume expansion days in bear markets may be dead-cat bounces rather than genuine breakouts.
  - The 15-day time exit is arbitrary — some breakouts need more time to play out; others exhaust faster.

- **Key risks**: Regime dependency (fails in sustained low-vol grind-up markets); parameter sensitivity on expansion_mult threshold; crowding risk if too many quant funds use ATR-based compression signals.
- **Estimated robustness**: Moderate — ATR compression is a structural property, not a fit artifact. Should survive ±20% parameter perturbation on the ATR lookback and compression percentile. Volume multiplier is the most sensitive parameter.

### Viability Scorecard
| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| Behavioral rationale strength | 8 | Volatility clustering is empirically very strong |
| Simplicity (fewer params = higher) | 7 | 4 parameters, all with economic justification |
| Indicator diversity | 9 | Volatility + Volume + OHLC Structure + Valuation = 4 categories |
| Crowding resistance | 6 | ATR squeeze is known but the CLV direction + P/E filter is novel |
| Volume confirmation | 9 | Volume is central to the signal |
| Regime robustness | 5 | Struggles in very low-vol grind-up regimes |
| **Overall** | **7.3** | |

---

## Strategy 2: Multi-Timeframe Momentum Deceleration with Accumulation Divergence

### Idea
Classical momentum buys winners and shorts losers based on past returns. This strategy adds a twist: instead of buying the strongest momentum, it looks for stocks where medium-term momentum (63-day) is strong BUT short-term momentum (21-day) is decelerating — suggesting the trend is pausing for breath, not reversing — AND On-Balance Volume is still rising (smart money accumulating despite the price pause). The thesis is that momentum pauses followed by continued accumulation tend to resolve in trend continuation, offering better entry points than chasing peak momentum.

### Behavioral / Structural Rationale
- **Why this pattern exists**: The disposition effect causes retail investors to sell winning positions prematurely ("lock in gains"). This creates temporary price pauses in genuinely strong trends. Meanwhile, institutional investors who have longer horizons continue accumulating during the pause, visible through rising OBV even as price flatlines.
- **Who is on the wrong side**: Retail traders who sold too early (disposition effect) and contrarian traders who interpret the pause as a reversal signal.
- **Academic/empirical support**: Jegadeesh & Titman (1993) momentum effect; George & Hwang (2004) 52-week high momentum; Grinblatt & Han (2005) disposition effect and momentum. The deceleration-then-continuation pattern is related to the "momentum life cycle" concept from Lee & Swaminathan (2000) who showed volume can predict momentum profitability.

### Signal Logic
- **Indicators used**:
  - 63-day log return — medium-term momentum (Category 3: Rate of Change)
  - 21-day log return — short-term momentum (Category 3, but used as a ratio to medium-term; the combination creates a *deceleration* metric which is conceptually different)
  - OBV slope (21-day linear regression slope of OBV) — accumulation direction (Category 5: Volume Flow)
  - P/E z-score (trailing 252-day) — valuation reality check (Category 7: Valuation)

- **Signal formula**:
  1. **Momentum Score**: Log return over 63 trading days (skip the most recent 5 days to avoid short-term reversal noise — the "skip month" convention adapted).
  2. **Deceleration Ratio**: 21-day log return / 63-day log return. A ratio between 0.0 and 0.4 indicates that short-term momentum has slowed while medium-term remains strong.
  3. **OBV Accumulation**: Compute OBV, then take the linear regression slope of OBV over the last 21 days. Positive slope = accumulation continuing.
  4. **Composite Signal** = Momentum Score × (1 if Deceleration Ratio is in [0.0, 0.4] else 0) × (1 if OBV slope > 0 else 0).
  5. **P/E gate**: Exclude stocks with P/E z-score > 2.0 (extremely expensive relative to own history).
  6. **Cross-sectional ranking**: Rank all stocks by composite signal. Go long top decile.

- **Parameters** (4 total):
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `mom_window` | 63 | Medium-term momentum lookback (trading days) |
  | `short_window` | 21 | Short-term momentum / OBV slope window |
  | `skip_days` | 5 | Recent days to skip in momentum calc |
  | `decel_max` | 0.4 | Maximum deceleration ratio for entry |

- **Entry rule**: At monthly rebalance, go long the top decile of stocks ranked by composite signal where all conditions are met.
- **Exit rule**: Rebalance monthly; exit positions that fall out of the top decile or where momentum turns negative.
- **Holding period**: 1–3 months
- **Rebalance frequency**: Monthly (21 trading days)

### Implementation Steps
1. For each stock, compute the 63-day log return, skipping the most recent 5 days: `log(Close[t-5] / Close[t-68])`.
2. Compute the 21-day log return: `log(Close[t] / Close[t-21])`.
3. Compute deceleration ratio: `21d_return / 63d_return`. Keep only stocks where this ratio is between 0.0 and 0.4 (positive medium-term momentum but slowing short-term).
4. Compute OBV: cumulative sum of `Volume × sign(daily return)`. Fit a linear regression to the last 21 days of OBV. Extract the slope. Positive slope = accumulation.
5. Create composite score: `63d_return × decel_flag × obv_slope_flag`.
6. If P/E data available, exclude stocks with P/E z-score > 2.0 (computed over trailing 252 days).
7. Rank all eligible stocks by composite score. Go long the top decile.
8. Hold for one month; repeat at next rebalance.

### Example Python Code

```python
import pandas as pd
import numpy as np
from scipy import stats as scipy_stats

def momentum_deceleration_accumulation_signal(
    ohlcv: pd.DataFrame,
    pe: pd.Series | None = None,
    mom_window: int = 63,
    short_window: int = 21,
    skip_days: int = 5,
    decel_max: float = 0.4,
) -> pd.Series:
    """
    Multi-Timeframe Momentum Deceleration with Accumulation Divergence.

    Finds stocks with strong medium-term momentum that is decelerating
    (pause, not reversal) while OBV shows continued accumulation.

    Behavioral rationale: Disposition effect causes premature selling by
    retail; institutions continue accumulating during the pause.
    Holding period: 1-3 months (monthly rebalance).
    Data required: OHLCV + P/E only.

    Parameters
    ----------
    ohlcv : DataFrame with columns [Open, High, Low, Close, Volume]
    pe : Optional P/E ratio series
    mom_window : Medium-term momentum lookback in days (default 63)
    short_window : Short-term lookback for deceleration / OBV slope (default 21)
    skip_days : Recent days to skip in momentum calc (default 5)
    decel_max : Maximum deceleration ratio to qualify (default 0.4)

    Returns
    -------
    Series of signal scores (higher = more bullish). Use cross-sectional
    ranking to select top decile for the long portfolio.
    """
    close = ohlcv['Close']
    volume = ohlcv['Volume']

    # --- Step 1: Medium-term momentum (skip recent days) ---
    mom_63 = np.log(close.shift(skip_days) / close.shift(mom_window + skip_days))

    # --- Step 2: Short-term momentum ---
    mom_21 = np.log(close / close.shift(short_window))

    # --- Step 3: Deceleration ratio ---
    # Avoid division by zero; only valid when mom_63 > 0
    decel_ratio = np.where(mom_63 > 0.01, mom_21 / mom_63, np.nan)
    decel_ratio = pd.Series(decel_ratio, index=ohlcv.index)

    # Deceleration flag: positive medium-term momentum, but short-term is slowing
    decel_flag = (decel_ratio >= 0.0) & (decel_ratio <= decel_max) & (mom_63 > 0.01)

    # --- Step 4: OBV and its slope ---
    daily_ret_sign = np.sign(close.pct_change())
    obv = (volume * daily_ret_sign).cumsum()

    # 21-day rolling linear regression slope of OBV
    def rolling_slope(series, window):
        slopes = series.rolling(window).apply(
            lambda y: scipy_stats.linregress(np.arange(len(y)), y).slope
            if len(y) == window else np.nan,
            raw=True
        )
        return slopes

    obv_slope = rolling_slope(obv, short_window)
    obv_accumulating = obv_slope > 0

    # --- Step 5: Composite signal ---
    # Start with momentum score, gated by deceleration + accumulation
    signal = pd.Series(0.0, index=ohlcv.index)
    valid = decel_flag & obv_accumulating
    signal[valid] = mom_63[valid]

    # --- Step 6: P/E filter (if available) ---
    if pe is not None:
        pe_clean = pe.copy()
        pe_clean[pe_clean <= 0] = np.nan
        pe_clean[pe_clean > 200] = np.nan

        # Time-series z-score over trailing 252 days
        pe_mean = pe_clean.rolling(252, min_periods=63).mean()
        pe_std = pe_clean.rolling(252, min_periods=63).std()
        pe_z = (pe_clean - pe_mean) / (pe_std + 1e-10)

        # Exclude extremely overvalued (z > 2.0)
        signal[pe_z > 2.0] = 0.0

    return signal
```

### Reasoning & Edge Assessment
- **Why this might work**:
  - Momentum is one of the most documented anomalies in finance (Jegadeesh & Titman 1993). Adding a deceleration filter improves entry timing versus naive momentum.
  - OBV divergence (rising OBV during price pause) has a structural basis: institutional accumulation creates footprints in volume data that retail ignores.
  - The skip-day convention reduces short-term reversal contamination, which is well-documented to erode naive momentum returns.

- **Why this might fail**:
  - In sharp bear markets, all momentum strategies fail as winners become losers rapidly. The deceleration filter won't protect if the broader trend reverses.
  - OBV is a noisy indicator on individual stocks; the slope computation adds some smoothing but can still give false accumulation signals.
  - Monthly rebalance introduces timing risk — the signal may decay within the month if conditions change rapidly.

- **Key risks**: Regime dependency (momentum crashes in sharp reversals, e.g., March 2009, March 2020); crowding in momentum factor; OBV slope sensitivity to outlier volume days; survivorship bias in momentum (losers get delisted).
- **Estimated robustness**: Good — the core momentum factor is robust across decades and markets. The deceleration and OBV filters are additive refinements, not load-bearing. Should survive ±20% perturbation on mom_window (50–75 days) and short_window (17–25 days).

### Viability Scorecard
| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| Behavioral rationale strength | 9 | Momentum + disposition effect are academically well-supported |
| Simplicity (fewer params = higher) | 7 | 4 parameters, all with standard justifications |
| Indicator diversity | 8 | Rate of Change + Volume Flow + Valuation = 3 categories |
| Crowding resistance | 7 | Plain momentum is crowded; deceleration + OBV twist is novel |
| Volume confirmation | 8 | OBV slope is central to the signal construction |
| Regime robustness | 5 | Momentum crashes in sharp reversals |
| **Overall** | **7.3** | |

---

## Strategy 3: Volume-Exhaustion Mean Reversion with Valuation Anchor

### Idea
After a multi-week decline, if volume spikes to an extreme (climax selling) and then immediately contracts over the next 2–3 days while price stabilizes near the lows, it signals that forced/panic sellers have been exhausted. This strategy buys the post-climax quiet period — but ONLY when the stock's P/E is below its own historical median (ensuring you're buying a temporary panic in a fundamentally acceptable name, not catching a falling knife on an overvalued stock).

### Behavioral / Structural Rationale
- **Why this pattern exists**: Loss aversion and forced selling (margin calls, fund redemptions, stop-loss cascades) create climax volume events. These selling cascades are self-reinforcing in the short term but self-exhausting — once forced sellers are done, the selling pressure evaporates and price stabilizes. The volume contraction after the spike is the observable footprint of this exhaustion.
- **Who is on the wrong side**: Panic sellers at the bottom who sold due to loss aversion or margin pressure. Also, trend followers who short the breakdown and get squeezed when forced selling ends.
- **Academic/empirical support**: Campbell, Grossman & Wang (1993) showed that high-volume price declines tend to reverse more than low-volume declines, consistent with the theory that volume captures forced/noisy trading. Avramov, Chordia & Goyal (2006) documented the volume-return relationship in cross-section. The "climax reversal" concept is well-documented in market microstructure literature.

### Signal Logic
- **Indicators used**:
  - 21-day return — decline detection (Category 3: Rate of Change)
  - Relative Volume = Volume / Median(Volume, 20) — climax detection (Category 5: Volume Flow)
  - Volume Momentum = SMA(Volume, 3) / SMA(Volume, 10) — exhaustion detection (Category 5, but a *derivative* of volume, measuring volume acceleration vs. volume level)
  - ATR(14) / Close — volatility context (Category 4: Volatility)
  - P/E percentile vs own 252-day history — valuation anchor (Category 7: Valuation)

- **Signal formula**:
  1. **Decline Condition**: 21-day return < −10% (stock has dropped meaningfully).
  2. **Climax Day**: Within the last 5 trading days, at least one day had Relative Volume > 3.0 (volume spike above 3× its 20-day median).
  3. **Exhaustion Confirmation**: Current 3-day average volume / 10-day average volume < 0.6 (volume has contracted sharply after the spike — sellers exhausted).
  4. **Volatility Context**: ATR(14)/Close is above its own 80th percentile over the trailing 126 days (elevated volatility environment — not a low-vol drift down).
  5. **Valuation Anchor**: P/E is below its own trailing 252-day median AND P/E > 0 (stock is cheaper than its own recent history and not losing money).
  6. **Signal Score**: When all conditions are met, the score = |21-day return| × (1 / Volume Momentum Ratio). Bigger decline with faster volume exhaustion = stronger signal.

- **Parameters** (4 total):
  | Parameter | Default | Description |
  |-----------|---------|-------------|
  | `decline_threshold` | -0.10 | Minimum 21-day decline to qualify |
  | `climax_vol_mult` | 3.0 | Relative volume threshold for climax |
  | `exhaustion_ratio` | 0.6 | Volume momentum ratio below which sellers are exhausted |
  | `vol_context_pct` | 80 | ATR percentile threshold for elevated volatility |

- **Entry rule**: Enter long at the close when all 5 conditions align. Size inversely proportional to ATR (risk parity within the strategy).
- **Exit rule**: Time-based exit after 15 trading days, OR profit target of 1.5× ATR from entry, OR stop-loss at 2× ATR below entry — whichever comes first.
- **Holding period**: 5–20 trading days (1–4 weeks)
- **Rebalance frequency**: Signal-based (event-driven); check daily for new setups.

### Implementation Steps
1. Compute 21-day return for each stock. Flag stocks where 21d return < −10%.
2. Compute Relative Volume = Volume / rolling Median(Volume, 20). For flagged stocks, check if any day in the last 5 trading days had Relative Volume > 3.0.
3. Compute Volume Momentum = SMA(Volume, 3) / SMA(Volume, 10). Check if current ratio < 0.6 (volume exhaustion).
4. Compute ATR(14) / Close. Compute its trailing 126-day percentile. Check if current value > 80th percentile (elevated vol context).
5. If P/E data available: compute trailing 252-day median of P/E. Check if current P/E < median AND P/E > 0.
6. When all conditions align, compute signal score = |21d return| × (1 / Volume Momentum Ratio).
7. Enter long at the close. Set profit target at 1.5× ATR above entry and stop-loss at 2× ATR below entry. Time exit at 15 trading days.

### Example Python Code

```python
import pandas as pd
import numpy as np

def volume_exhaustion_mean_reversion_signal(
    ohlcv: pd.DataFrame,
    pe: pd.Series | None = None,
    decline_threshold: float = -0.10,
    climax_vol_mult: float = 3.0,
    exhaustion_ratio: float = 0.6,
    vol_context_pct: int = 80,
) -> pd.Series:
    """
    Volume-Exhaustion Mean Reversion with Valuation Anchor.

    Buys stocks after forced/panic selling exhaustion: a multi-week decline
    with a volume climax followed by rapid volume contraction, in a stock
    with below-median P/E.

    Behavioral rationale: Loss aversion and forced selling create climax
    events that are self-exhausting. Volume contraction = sellers done.
    Holding period: 5-20 trading days.
    Data required: OHLCV + P/E only.

    Parameters
    ----------
    ohlcv : DataFrame with columns [Open, High, Low, Close, Volume]
    pe : Optional P/E ratio series
    decline_threshold : Min 21-day return to qualify (default -0.10)
    climax_vol_mult : Relative volume threshold for climax (default 3.0)
    exhaustion_ratio : Volume momentum ceiling for exhaustion (default 0.6)
    vol_context_pct : ATR percentile threshold (default 80)

    Returns
    -------
    Series of signal scores (higher = stronger mean reversion signal).
    Positive values = buy signal; zero = no signal.
    """
    high = ohlcv['High']
    low = ohlcv['Low']
    close = ohlcv['Close']
    volume = ohlcv['Volume']

    # --- Step 1: Decline detection ---
    ret_21 = close / close.shift(21) - 1
    has_decline = ret_21 < decline_threshold

    # --- Step 2: Climax volume within last 5 days ---
    vol_median_20 = volume.rolling(20).median()
    relative_vol = volume / (vol_median_20 + 1e-10)

    # Check if any of the last 5 days had relative volume > climax threshold
    recent_climax = relative_vol.rolling(5).max() > climax_vol_mult

    # --- Step 3: Volume exhaustion (current volume contracting) ---
    vol_sma_3 = volume.rolling(3).mean()
    vol_sma_10 = volume.rolling(10).mean()
    vol_momentum = vol_sma_3 / (vol_sma_10 + 1e-10)
    is_exhausted = vol_momentum < exhaustion_ratio

    # --- Step 4: Elevated volatility context ---
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    norm_atr = atr / close

    def rolling_percentile(series, window=126):
        return series.rolling(window).apply(
            lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
        )

    atr_pct = rolling_percentile(norm_atr, window=126)
    high_vol_context = atr_pct > (vol_context_pct / 100.0)

    # --- Step 5: All conditions combined ---
    all_conditions = has_decline & recent_climax & is_exhausted & high_vol_context

    # --- Step 6: Signal score ---
    signal = pd.Series(0.0, index=ohlcv.index)
    signal[all_conditions] = ret_21[all_conditions].abs() * (1.0 / (vol_momentum[all_conditions] + 0.01))

    # --- Step 7: P/E valuation anchor ---
    if pe is not None:
        pe_clean = pe.copy()
        pe_clean[pe_clean <= 0] = np.nan
        pe_clean[pe_clean > 200] = np.nan

        # Below own trailing 252-day median = historically cheap
        pe_median_252 = pe_clean.rolling(252, min_periods=63).median()
        is_cheap = (pe_clean < pe_median_252) & (pe_clean > 0)

        # Zero out signals for stocks that aren't cheap
        signal[~is_cheap] = 0.0

    return signal
```

### Reasoning & Edge Assessment
- **Why this might work**:
  - The volume climax → exhaustion pattern has a strong structural basis: forced sellers (margin calls, redemptions) create temporary but powerful price dislocations that reverse when selling pressure ends.
  - Volume contraction after a spike is an observable, falsifiable condition — not a subjective chart pattern.
  - The P/E anchor prevents catching falling knives on fundamentally impaired companies (the classic mean-reversion failure mode).

- **Why this might fail**:
  - In bear markets or credit crises, "climax selling" can be followed by MORE selling as fundamentals deteriorate. The P/E filter helps but doesn't fully protect (P/E can be low at peak earnings before a cyclical downturn).
  - The 21-day decline threshold is a line in the sand — a 9% decline is very similar to a 10% decline but gets entirely different treatment.
  - Survivorship bias is a major concern for mean reversion strategies on individual stocks: some "panics" are justified because the company is going bankrupt. These delisted stocks disappear from most datasets but would be real losses.

- **Key risks**: Regime dependency (bear market mean reversion is a losing strategy); survivorship bias inflates historical returns by 200–300 bps for mean reversion; the P/E filter helps but can't fully distinguish distressed from unfairly punished stocks; capacity constraints if too many positions trigger simultaneously during a market-wide selloff.
- **Estimated robustness**: Moderate — the volume climax/exhaustion pattern is structural and should survive ±20% parameter changes. However, the strategy's profitability is highly regime-dependent. Works best in bull markets with periodic scares.

### Viability Scorecard
| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| Behavioral rationale strength | 9 | Loss aversion + forced selling well-documented |
| Simplicity (fewer params = higher) | 7 | 4 parameters, all interpretable |
| Indicator diversity | 9 | Rate of Change + Volume Flow + Volatility + Valuation = 4 categories |
| Crowding resistance | 7 | Volume-exhaustion concept is known but the specific formulation is less common |
| Volume confirmation | 10 | Volume IS the signal (climax + exhaustion) |
| Regime robustness | 4 | Mean reversion fails in sustained bear markets |
| **Overall** | **7.7** | |

---

## Comparison Matrix

| Aspect | Strategy 1: Vol Compression Breakout | Strategy 2: Momentum Deceleration | Strategy 3: Volume Exhaustion MR |
|--------|--------------------------------------|-----------------------------------|----------------------------------|
| Style | Breakout / Volatility expansion | Momentum continuation | Mean reversion |
| Exploitation | Volatility clustering | Disposition effect / underreaction | Loss aversion / forced selling |
| Indicators | ATR + Volume Ratio + CLV + P/E | Momentum + OBV slope + P/E z-score | 21d Return + RelVol + VolMomentum + ATR + P/E |
| Categories used | Volatility + Volume + OHLC + Valuation | Rate of Change + Volume + Valuation | ROC + Volume + Volatility + Valuation |
| Parameters | 4 | 4 | 4 |
| Hold period | 1–4 weeks | 1–3 months | 1–4 weeks |
| Rebalance | Signal-based (event) | Monthly | Signal-based (event) |
| Direction | Long or Short | Long-only (cross-sectional) | Long-only |
| Best regime | Transitional vol (compression→expansion) | Bull/trending markets | Bull markets with periodic scares |
| Worst regime | Sustained low-vol grind | Sharp reversals / bear | Sustained bear market |
| Turnover | ~200–300% | ~100–200% | ~100–200% |
| Overall score | 7.3/10 | 7.3/10 | 7.7/10 |

---

## Portfolio Diversification Note

These three strategies are intentionally designed to have **low correlation** with each other:

1. **Strategy 1 (Breakout)** profits from volatility expansion — it performs best when quiet markets suddenly move.
2. **Strategy 2 (Momentum)** profits from continued trends — it performs best in sustained directional markets.
3. **Strategy 3 (Mean Reversion)** profits from over-reaction — it performs best when extreme moves reverse.

Running all three in parallel provides natural hedging: when momentum crashes (sharp reversal), the mean reversion strategy captures the bounce. When markets are range-bound (bad for momentum), the compression breakout strategy waits for the next expansion.

---

## Web Research Sources
- Jegadeesh & Titman (1993), "Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency"
- Lee & Swaminathan (2000), "Price Momentum and Trading Volume"
- Campbell, Grossman & Wang (1993), "Trading Volume and Serial Correlation in Stock Returns"
- George & Hwang (2004), "The 52-Week High and Momentum Investing"
- Grinblatt & Han (2005), "Prospect Theory, Mental Accounting, and Momentum"
- Bollerslev (1986), "Generalized Autoregressive Conditional Heteroskedasticity"
- Bollinger (2002), "Bollinger on Bollinger Bands"
- Harvey, Liu & Zhu (2016), "...and the Cross-Section of Expected Returns"
- Avramov, Chordia & Goyal (2006), "Liquidity and Autocorrelations in Individual Stock Returns"
- Lou & Polk, "Comomentum: Inferring Arbitrage Activity from Return Correlations"
