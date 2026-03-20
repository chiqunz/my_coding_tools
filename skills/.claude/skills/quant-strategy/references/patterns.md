# Strategy Mining — Methodology & Building Blocks (OHLCV + P/E Only)

## This file contains frameworks, thinking tools, and compositional patterns for DISCOVERING new strategies. It does NOT contain pre-built strategies — those are YOUR job to mine fresh each time.

> **Purpose**: Equip you with *how to think* about strategy construction, not *what to build*.
> Every strategy you generate should be novel to the user's request, not copied from a template.

---

## Strategy Discovery Dimensions

When mining for new strategies, explore along these independent dimensions.
A good strategy idea usually combines 2-3 dimensions in a novel way.

### Dimension 1: Exploitation Type
What behavioral bias or structural friction are you exploiting?

| Exploitation Type | What's Happening | Who's Wrong | Typical Signal Shape |
|-------------------|-----------------|-------------|---------------------|
| **Underreaction** | Information arrives but price adjusts slowly | Anchoring investors who stick to old valuation | Trending signal, slow decay |
| **Overreaction** | Price moves too far too fast (panic/euphoria) | Emotional traders, forced liquidators | Mean-reverting signal, fast decay |
| **Herding** | Everyone piles into the same trade | Late followers who buy at the top | Momentum then reversal |
| **Forced selling** | Margin calls, fund redemptions, index deletions | Sellers who MUST sell regardless of price | Sharp dip + recovery |
| **Institutional flow** | Large funds build/unwind positions over weeks | Small traders who don't see the footprint | Gradual volume trend + price follows |
| **Anchoring** | Traders fixate on round numbers, 52-week highs/lows | Those who sell "because it's at the high" | Breakout from reference level |
| **Volatility clustering** | Low vol → high vol, high vol → low vol (GARCH) | Traders who assume current vol persists | Regime-change signal |
| **Disposition effect** | Investors sell winners too early, hold losers too long | Those who lock in small gains and ride big losses | Value + momentum combination |

### Dimension 2: Signal Timing
How quickly does the signal decay? This MUST match the holding period.

| Signal Category | Typical Half-Life | Suitable Hold Period | Rebalance |
|----------------|-------------------|---------------------|-----------|
| Extreme overbought/oversold | 3-10 days | 1-3 weeks | Weekly |
| Volume anomaly / spike | 5-15 days | 1-3 weeks | Weekly |
| Overnight gap | 5-15 days | 1-3 weeks | Signal-based |
| Range breakout / compression | 10-30 days | 2-8 weeks | Bi-weekly |
| MACD / oscillator crossover | 15-40 days | 2-8 weeks | Bi-weekly |
| Divergence (price vs volume) | 10-30 days | 2-6 weeks | Bi-weekly |
| Medium-term momentum | 30-90 days | 1-3 months | Monthly |
| Moving average crossover | 30-90 days | 1-6 months | Monthly |
| Cross-sectional ranking | 30-90 days | 1-3 months | Monthly |
| Valuation (P/E based) | 60-180 days | 1-6 months | Monthly/Quarterly |

### Dimension 3: Signal Construction Method
How do you turn raw OHLCV + P/E into a tradable signal?

| Method | Description | When to Use |
|--------|-------------|-------------|
| **Threshold crossing** | Signal fires when indicator crosses a level (e.g., RSI < 30) | Simple binary signals, event-driven |
| **Cross-sectional ranking** | Rank all stocks by a metric, trade the extremes | Portfolio strategies, reduces market exposure |
| **Time-series z-score** | Normalize indicator by its own rolling mean/std | Detecting "unusual" readings for a given stock |
| **Regime conditional** | Apply different logic depending on volatility/trend regime | Adaptive strategies that switch modes |
| **Multi-indicator composite** | Weighted combination of 2-3 indicators from different categories | Robust signals with multiple confirmation |
| **Divergence detection** | Compare two related series (price vs OBV, short vs long momentum) | Early warning / reversal signals |
| **Breakout from range** | Detect tight ranges, trade the first directional move out | Compression → expansion patterns |
| **Slope / trend measurement** | Linear regression slope or rolling return of an indicator | Detecting acceleration or deceleration |

---

## Indicator Category System

**CRITICAL RULE**: When combining indicators, you MUST use indicators from DIFFERENT categories.
Combining two indicators from the same category adds noise, not information.

### The 7 Categories

| # | Category | Members | What They All Measure |
|---|----------|---------|----------------------|
| 1 | **Overbought/Oversold** | RSI, Stochastic %K, Williams %R, CCI | Position of price in recent range |
| 2 | **Trend Direction** | SMA, EMA, MACD signal line, price vs MA | Average price direction |
| 3 | **Rate of Change** | ROC, Momentum (raw), MACD histogram | Speed of price change |
| 4 | **Volatility** | ATR, Bollinger Width, Std Dev, True Range ratio | Price dispersion / uncertainty |
| 5 | **Volume Flow** | OBV, A/D Line, MFI, Volume-Price Trend, Relative Volume | Buying/selling pressure via volume |
| 6 | **OHLC Structure** | Body ratio, shadow ratios, gap, close location, range | Intra-bar dynamics and conviction |
| 7 | **Valuation** | P/E rank, P/E z-score, P/E change, earnings yield | Price relative to earnings |

### Combination Quality Levels

| Combination | Quality | Example |
|-------------|---------|---------|
| Cat 1 + Cat 5 + Cat 7 | Excellent | Oversold + volume confirmation + valuation floor |
| Cat 2 + Cat 4 + Cat 5 | Excellent | Trend + volatility regime + volume confirmation |
| Cat 1 + Cat 2 + Cat 7 | Good | Oversold + trend alignment + valuation |
| Cat 3 + Cat 5 + Cat 6 | Good | Rate of change + volume flow + bar structure |
| Cat 4 + Cat 6 | Good | Volatility compression + directional candle |
| Cat 1 + Cat 1 | Bad | RSI + Stochastic (same information twice) |
| Cat 2 + Cat 2 | Bad | SMA + EMA (redundant) |
| Cat 1 + Cat 3 | Marginal | RSI + ROC (somewhat correlated) |

---

## Behavioral Finance Toolkit

Every strategy you mine MUST cite at least one behavioral or structural reason.
Use this reference to connect price patterns to human psychology.

### Behavioral Biases Exploitable with OHLCV + P/E

| Bias | What Happens | Observable in OHLCV/P/E | Strategy Family |
|------|-------------|------------------------|-----------------|
| **Anchoring** | Traders fixate on reference prices (52-week high, round numbers) | Price near historical highs/lows; volume at round numbers | Breakout, proximity strategies |
| **Loss aversion** | Pain of loss > pleasure of gain → panic selling | Volume spikes on down days; RSI extremes | Mean reversion after panic |
| **Herding** | Investors follow the crowd | Rising volume + rising price over weeks | Momentum (early phase) |
| **Overconfidence** | Traders over-weight their own analysis | Low volume rallies; weak conviction bars | Fade signals (contrarian) |
| **Disposition effect** | Sell winners too early, hold losers too long | Volume patterns around breakeven levels | Value + momentum composite |
| **Recency bias** | Over-weight recent events | Price overreaction to recent vol spikes | Volatility mean reversion |
| **Representativeness** | Small samples treated as meaningful patterns | Short-term reversals after 1-day spikes | Noise-fade strategies |
| **Slow diffusion** | Information takes time to spread across investors | Gradual OBV trend changes ahead of price | Divergence strategies |

### Structural Frictions Exploitable with OHLCV + P/E

| Friction | What Happens | Observable in OHLCV/P/E | Strategy Family |
|----------|-------------|------------------------|-----------------|
| **Index rebalancing** | Forced buying/selling on add/delete dates | Volume spikes + price moves on known dates | Event-driven with volume |
| **Margin calls** | Forced selling regardless of fundamentals | Volume spike + extreme price drop + quick recovery | Climax reversal |
| **Fund redemptions** | Funds sell liquid positions to meet outflows | Declining volume over weeks + price decline | Volume-price divergence |
| **Institutional accumulation** | Large orders split over weeks | Rising OBV before price moves | Volume-leading-price signals |
| **Stop-loss cascading** | Clusters of stops create self-reinforcing moves | Sudden volume burst at technical levels | Breakout continuation |
| **Seasonal/window dressing** | End-of-quarter positioning by fund managers | Volume and price patterns around quarter-ends | Calendar-based signals |

---

## Signal Composition Patterns

These are abstract patterns for HOW to combine indicators. They are NOT strategies —
you must instantiate them with specific indicators and parameters for each new strategy.

### Pattern A: Primary Signal + Confirmation Filter
- Pick ONE primary signal (the edge)
- Add 1-2 filters from DIFFERENT categories to reduce false positives
- The primary signal drives the direction; filters gate the entry
- Keep total parameters ≤ 5

### Pattern B: Cross-Sectional Ranking
- Compute a score for every stock in the universe
- Rank all stocks by the score
- Go long the top decile, short (or avoid) the bottom decile
- The ranking itself is the signal — no threshold needed
- Works best with monthly rebalance

### Pattern C: Regime-Conditional Logic
- Detect the current market regime (high/low vol, trending/range-bound)
- Apply different signal logic depending on the regime
- Low vol regime → one type of signal; High vol regime → another
- Regime detection should use a DIFFERENT indicator than the signal itself

### Pattern D: Divergence + Trigger
- Detect a divergence between two related series (price vs OBV, short-term vs long-term momentum)
- Wait for a trigger event (volume spike, breakout, RSI extreme) to time the entry
- Divergence gives direction; trigger gives timing

### Pattern E: Compression → Expansion
- Detect a period of abnormally low volatility/range
- Wait for the first expansion day with directional commitment
- Direction determined by where price closes within the expansion bar
- Volume confirms institutional participation

### Pattern F: Event + Mean Reversion
- Detect an extreme event (volume climax, gap, sharp multi-day decline)
- Filter by regime (is this panic or rational repricing?)
- Enter in the reversal direction with time-based exit
- P/E acts as a sanity check (don't buy collapsing fundamentals)

### Pattern G: Multi-Timeframe Agreement
- Compute the same type of signal at two different timeframes (e.g., 5-day vs 20-day)
- Trade only when both timeframes agree on direction
- Disagreement = stay flat or reduce position
- Reduces whipsaw compared to single-timeframe signals

---

## Strategy Novelty Checklist

Before including a strategy in your report, verify it's genuinely NEW for this user:

- [ ] Is this strategy substantially different from the other strategies in this report?
- [ ] Does it exploit a different behavioral bias or structural friction?
- [ ] Does it use at least one indicator or combination that's not in the other strategies?
- [ ] Would it behave differently in different market regimes?
- [ ] Is it NOT a simple textbook strategy (golden cross, RSI < 30, MACD crossover) without a novel twist?
- [ ] Can you explain what makes it different from the most similar well-known strategy?

---

## P/E Integration Patterns

P/E is the only non-price/volume data available. Use it wisely:

### As a Safety Filter (most common)
- Reject signals where P/E is negative, extreme (>200), or undefined
- Only act on price signals where P/E < sector median (avoid overvalued)
- Prevents pure momentum from chasing bubble stocks

### As a Ranking Dimension
- Combine P/E percentile rank with a price-based rank (e.g., momentum)
- Create composite: `alpha * price_score + (1 - alpha) * value_score`
- Negative correlation between value and momentum improves composite stability

### As a Regime Indicator
- Aggregate P/E (market-wide) indicates expensive vs cheap markets
- Adjust strategy aggressiveness based on market-level valuation
- High market P/E → reduce momentum exposure; Low market P/E → increase value exposure

### P/E Pitfalls to Remember
- Negative earnings → exclude (don't treat as "cheap")
- Cyclical peaks → low P/E at peak earnings is NOT cheap
- Cross-sector comparison → always rank within sector, not across
- Stale data → P/E updates quarterly; acknowledge the lag

---

## Turnover & Cost Awareness

Even though this skill doesn't backtest, your strategy ideas should be PLAUSIBLE
from a cost perspective. Use these rules of thumb:

| Strategy Type | Typical Turnover | Large Cap Cost | Is This Plausible? |
|---------------|-----------------|---------------|-------------------|
| Monthly momentum rebalance | 100-200% | 10-20 bps | Yes, if alpha > 60 bps |
| Weekly mean reversion | 300-500% | 30-50 bps | Only for large caps |
| Event-driven (gaps, climaxes) | 100-300% | 10-30 bps | Yes, selective entry |
| Daily indicator crossing | 600-1000% | 60-100 bps | Likely NOT viable |
| Quarterly value rotation | 50-100% | 5-10 bps | Yes, highly viable |

**Rule of thumb**: If estimated turnover × cost per trade × 2 exceeds 200 bps annually,
the strategy needs very strong alpha to survive. Note this in the report.
