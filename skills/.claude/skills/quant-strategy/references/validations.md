# Strategy Mining - Validations (OHLCV + P/E Only)

## Minimum viability gates for price-based technical indicator strategy ideas.

> **When to consult this file**: Before including a strategy idea in your report,
> run it through these gates. A strategy that fails a gate marked "error" should be
> rejected or reworked. Gates marked "warning" or "info" are yellow flags to note.
> These are ideation-phase checks — they assess whether an idea is *worth specifying*,
> not whether it's been proven profitable.

---

## Data Constraint Enforcement

### **Id**
check-data-constraint
### **Description**
Every strategy MUST use ONLY Open, High, Low, Close, Volume, and P/E ratio data. No exceptions.
### **Pattern**
signal|strategy|indicator|data|input
### **File Glob**
**/*.{py,md,ipynb}
### **Match**
present
### **Message**
Strategy must use ONLY OHLCV + P/E data. No fundamental data beyond P/E, no alternative data, no macro data, no sentiment data.
### **Severity**
error
### **Gate Criteria**
  ALLOWED inputs:
  - Open price (daily)
  - High price (daily)
  - Low price (daily)
  - Close price (daily, split/dividend adjusted)
  - Volume (daily, split-adjusted)
  - P/E ratio (trailing or forward)

  REJECTED inputs (redirect user):
  - Revenue, earnings, balance sheet items (except via P/E)
  - Interest rates, yield curves, macro indicators
  - Sentiment, news, social media data
  - Options data (implied vol, put/call ratio)
  - Order book, tick data, intraday bars
  - Analyst estimates, insider transactions
  - Alternative data (satellite, web traffic, etc.)

---

## Mid-Term Holding Period Compliance

### **Id**
check-holding-period
### **Description**
Strategies must target mid-term holding periods (5 trading days to 6 months)
### **Pattern**
holding.*period|rebalance|frequency|horizon|hold
### **File Glob**
**/*.{py,md,ipynb}
### **Match**
present
### **Message**
Holding period must be between 1 week and 6 months. No intra-day. No multi-year buy-and-hold.
### **Severity**
error
### **Gate Criteria**
  - Minimum holding period: 5 trading days (~1 week)
  - Maximum holding period: ~126 trading days (~6 months)
  - Rebalance frequency: weekly to quarterly
  - REJECT: anything requiring intra-day execution
  - REJECT: buy-and-hold strategies (>1 year hold)
  - REJECT: strategies requiring tick data or sub-daily bars

---

## Behavioral/Structural Rationale Required

### **Id**
check-behavioral-rationale
### **Description**
Every price pattern must have an explanation for WHY it exists based on behavioral bias or market structure
### **Pattern**
strategy|signal|pattern|indicator
### **File Glob**
**/*.{py,md}
### **Match**
present
### **Context Pattern**
behavioral|bias|structural|friction|why.*work|rationale|anchoring|herding|overreaction
### **Message**
Price pattern must have a behavioral or structural explanation. "It works in backtest" is not a rationale.
### **Severity**
error
### **Gate Criteria**
  Must answer at least ONE of:
  1. What behavioral bias creates this price pattern? (anchoring, herding, loss aversion, overreaction, etc.)
  2. What structural friction causes the inefficiency? (forced selling, index rebalancing, margin calls, etc.)
  3. What information asymmetry does volume/price reveal? (institutional accumulation, smart money flow, etc.)

  NOT acceptable rationales:
  - "The indicator crossed a level" (that's what happened, not why it works)
  - "It has a high Sharpe ratio in backtest" (that's the result, not the cause)
  - "RSI works because it measures overbought conditions" (circular reasoning)

---

## Parameter Count Limit

### **Id**
check-parameter-count
### **Description**
Strategies must use 5 or fewer tunable parameters to prevent overfitting
### **Pattern**
param|threshold|window|lookback|period|multiplier
### **File Glob**
**/*.{py,md,ipynb}
### **Match**
present
### **Message**
Maximum 5 tunable parameters per strategy. Each must have economic justification and survive +-20% perturbation.
### **Severity**
warning
### **Gate Criteria**
  Parameter count rules:
  - 1-2 parameters: Excellent (most robust)
  - 3-4 parameters: Good (acceptable for composite signals)
  - 5 parameters: Maximum (each must be justified)
  - 6+ parameters: REJECT (overfitting risk too high)

  What counts as a parameter:
  - Lookback windows (RSI period, MA length)
  - Thresholds (RSI level, volume ratio cutoff)
  - Weights (value vs momentum blend)
  - Multipliers (Bollinger std multiplier, ATR multiplier)

  What does NOT count:
  - Fixed structural choices (using close vs open)
  - Universe filters (minimum price, minimum volume)
  - Standard values that are NOT tuned (RSI=14, BB=20)

---

## Indicator Diversity Check

### **Id**
check-indicator-diversity
### **Description**
Composite signals must use indicators from different categories, not redundant ones
### **Pattern**
composite|combine|multi.*indicator|blend|signal.*combination
### **File Glob**
**/*.{py,md,ipynb}
### **Match**
present
### **Message**
Combined signals must use indicators from different categories (e.g., trend + volume + volatility). Don't combine RSI + Stochastic + Williams %R.
### **Severity**
warning
### **Gate Criteria**
  Indicator categories (use at most ONE from each):
  1. Overbought/Oversold: RSI, Stochastic, Williams %R, CCI
  2. Trend Direction: SMA, EMA, MACD signal, price vs MA
  3. Rate of Change: ROC, Momentum, MACD histogram
  4. Volatility: ATR, Bollinger Width, Standard Deviation
  5. Volume Flow: OBV, A/D Line, MFI, Volume-Price Trend
  6. OHLC Structure: Body ratio, shadow ratios, range
  7. Valuation: P/E rank, P/E z-score, earnings yield

  GOOD combinations:
  - Category 1 + Category 5 + Category 7 (RSI + OBV + P/E)
  - Category 2 + Category 4 + Category 5 (SMA trend + ATR + Volume)
  - Category 1 + Category 2 + Category 7 (RSI + MA trend + P/E)

  BAD combinations:
  - Category 1 + Category 1 + Category 1 (RSI + Stochastic + CCI)
  - Category 2 + Category 2 (SMA + EMA)

---

## Standard Parameter Preference

### **Id**
check-standard-parameters
### **Description**
Strategies should use standard/common parameter values unless there's strong justification for custom values
### **Pattern**
rsi|sma|ema|bollinger|macd|atr|stochastic|cci
### **File Glob**
**/*.{py,md,ipynb}
### **Match**
present
### **Message**
Prefer standard parameter values (RSI=14, BB=20/2, SMA=50/200, ATR=14/20). Custom values need justification and are a yellow flag for overfitting.
### **Severity**
info
### **Gate Criteria**
  Standard parameter values (prefer these):
  - RSI: 14 period
  - Bollinger Bands: 20 period, 2 standard deviations
  - SMA: 20, 50, 100, 200
  - EMA: 12, 26 (MACD default)
  - ATR: 14 or 20
  - Stochastic: 14 period
  - MACD: 12, 26, 9

  If using non-standard values, must answer:
  1. Why does this value better match the holding period?
  2. Does the signal still work at standard values?
  3. Is the performance difference > 20% vs standard? (If not, use standard)

---

## Transaction Cost Viability

### **Id**
check-transaction-cost-viability
### **Description**
Expected alpha must be at least 3x estimated transaction costs based on turnover and universe
### **Pattern**
alpha|return|performance|turnover|trade
### **File Glob**
**/*.{py,md,ipynb}
### **Match**
present
### **Message**
Alpha must be >= 3x transaction costs. Specify: estimated turnover, cost per trade, and net alpha.
### **Severity**
warning
### **Gate Criteria**
  Required calculation:
  1. Estimate annual portfolio turnover (one-way)
  2. Estimate cost per trade (based on universe):
     - Large cap: 5 bps
     - Mid cap: 15 bps
     - Small cap: 30 bps
     - Micro cap: 50+ bps
  3. Annual cost = Turnover * 2 * cost_per_trade
  4. Net alpha = Gross alpha - Annual cost
  5. Alpha/Cost ratio must be >= 3.0

  Quick reference for mid-term strategies:
  | Turnover | Large Cap Cost | Mid Cap Cost | Small Cap Cost |
  |----------|---------------|-------------|---------------|
  | 100% | 10 bps | 30 bps | 60 bps |
  | 200% | 20 bps | 60 bps | 120 bps |
  | 400% | 40 bps | 120 bps | 240 bps |

---

## Volume Confirmation Encouraged

### **Id**
check-volume-component
### **Description**
Price-only signals are weaker than price+volume signals; volume confirmation should be included when possible
### **Pattern**
signal|strategy|entry|buy|sell
### **File Glob**
**/*.{py,md,ipynb}
### **Match**
present
### **Context Pattern**
volume|obv|mfi|accumulation|vol_ratio
### **Message**
Consider adding volume confirmation to price signals. Volume validates conviction behind price moves.
### **Severity**
info
### **Gate Criteria**
  Volume adds value to these signal types:
  - Breakout signals: volume surge confirms genuine breakout vs false breakout
  - Momentum signals: rising volume confirms institutional flow
  - Mean reversion: declining volume at lows suggests selling exhaustion
  - Gap signals: high-volume gaps are more likely to continue

  When volume may NOT add value:
  - Cross-sectional ranking signals (momentum rank doesn't need volume)
  - P/E-based signals (valuation is price-based by definition)
  - Very liquid instruments (SPY, QQQ) where volume is always adequate

---

## Risk Identification Required

### **Id**
check-risk-identification
### **Description**
Every strategy must identify at least 3 specific risks including regime dependency
### **Pattern**
strategy|signal|approach
### **File Glob**
**/*.{md}
### **Match**
present
### **Context Pattern**
risk|fail|drawdown|regime|whipsaw|false.*signal
### **Message**
Identify at least 3 risks. Must include regime dependency (does this fail in bear/bull/choppy markets?).
### **Severity**
warning
### **Gate Criteria**
  Must identify at least 3 risks, including:

  1. **Regime risk** (REQUIRED): In which market regime does this strategy fail?
     - Momentum → fails in bear markets and reversals
     - Mean reversion → fails in trending markets and during capitulation
     - Breakout → fails in choppy/range-bound markets
     - Volume signals → unreliable in low-liquidity environments

  2. **At least 2 additional risks from:**
     - Whipsaw risk (false signals around thresholds)
     - Crowding risk (too many people trading the same pattern)
     - Data quality risk (splits, adjustments, errors in OHLCV)
     - Turnover risk (transaction costs exceeding alpha)
     - Parameter sensitivity (signal breaks with small param changes)
     - Capacity risk (strategy doesn't work at larger sizes)

---

## Signal Decay Match

### **Id**
check-signal-decay-match
### **Description**
The signal's natural decay rate must match the intended holding period
### **Pattern**
signal|holding.*period|decay|half.*life|rebalance
### **File Glob**
**/*.{py,md}
### **Match**
present
### **Message**
Signal decay must match holding period. A signal that decays in 3 days can't support a 3-month hold.
### **Severity**
info
### **Gate Criteria**
  Signal decay guidelines by indicator type:

  | Indicator Type | Typical Signal Half-Life | Suitable Hold Period |
  |---------------|------------------------|---------------------|
  | RSI extreme (< 20 or > 80) | 3-10 days | 1-3 weeks |
  | RSI moderate (< 30 or > 70) | 5-15 days | 1-4 weeks |
  | MA crossover (50/200) | 30-90 days | 1-6 months |
  | Bollinger breakout | 10-30 days | 2-8 weeks |
  | MACD crossover | 15-40 days | 2-8 weeks |
  | Volume divergence | 10-30 days | 2-6 weeks |
  | Momentum (6-month) | 30-90 days | 1-3 months |
  | P/E rank | 60-180 days | 1-6 months |
  | Gap signal | 5-15 days | 1-3 weeks |
  | Candle structure | 3-10 days | 1-3 weeks |

  MISMATCH examples (bad):
  - RSI < 30 signal with 3-month hold → signal decays in 1-2 weeks
  - 200-day MA crossover with 1-week hold → signal moves too slowly
  - Volume spike with 6-month hold → spike effect fades in days

---

## Quick Validation Checklist

Use this condensed checklist as a final gate before including a strategy in your report:

| # | Gate | Pass? | Severity |
|---|------|-------|----------|
| 1 | Uses ONLY OHLCV + P/E data? | ☐ | error |
| 2 | Holding period is 1 week to 6 months? | ☐ | error |
| 3 | Has behavioral or structural "why"? | ☐ | error |
| 4 | ≤ 5 tunable parameters? | ☐ | warning |
| 5 | Indicators from different categories? | ☐ | warning |
| 6 | Uses standard parameter values (or justifies custom)? | ☐ | info |
| 7 | Estimated alpha ≥ 3× transaction costs? | ☐ | warning |
| 8 | Includes volume confirmation (where applicable)? | ☐ | info |
| 9 | Identifies ≥ 3 risks including regime dependency? | ☐ | warning |
| 10 | Signal decay matches holding period? | ☐ | info |

**If any "error" gate fails → reject or rework the idea.**
**If 2+ "warning" gates fail → add a disclaimer in the report and lower viability score.**
