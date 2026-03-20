# Strategy Mining - Sharp Edges (OHLCV + P/E Only)

## Common pitfalls specific to DISCOVERING and DESIGNING mid-term strategies from price, volume, and P/E data.

> **When to consult this file**: Before finalizing any strategy idea in your report,
> scan this list. Each pitfall is a reason your "great idea" might be worthless.
> Be honest — if a pitfall applies, note it in the "Why This Might Fail" section.

---

## Your Indicator "Edge" Is Just Noise in Disguise

### **Id**
indicator-noise-trap
### **Severity**
CRITICAL
### **Description**
Most technical indicator signals on daily data have signal-to-noise ratios near zero. A signal that "works" in backtest is usually noise you've accidentally fit to.
### **Symptoms**
  - RSI threshold of exactly 28.7 works but 30 doesn't
  - Moving average crossover works at 47/193 but not 50/200
  - Indicator only works on a specific sector or time period
  - Removing one condition from a multi-condition signal breaks everything
### **Detection Pattern**
indicator|rsi|macd|moving.*average|bollinger|stochastic
### **Solution**

**The Signal-to-Noise Reality of Price Data:**
Daily stock price returns have a signal-to-noise ratio of approximately 0.05.
This means 95% of what you see in price data is noise.

**Implications for strategy mining:**
1. Any single indicator on daily data has very weak predictive power
2. If your signal requires precise parameter values, it's fitting noise
3. If your signal doesn't work with rounded/common parameter values (14, 20, 50, 200), be suspicious

**The Robustness Test Every Indicator Must Pass:**
```python
def indicator_robustness_test(
    compute_signal_func: callable,
    ohlcv: pd.DataFrame,
    base_params: dict,
    perturbation: float = 0.2
) -> dict:
    """
    Test if signal survives +-20% parameter changes.
    If it doesn't, the signal is fitting noise.
    """
    base_result = compute_signal_func(ohlcv, **base_params)
    base_metric = calculate_sharpe(base_result)

    results = {'base': base_metric}

    for param, value in base_params.items():
        if not isinstance(value, (int, float)):
            continue
        for direction in ['low', 'high']:
            mult = (1 - perturbation) if direction == 'low' else (1 + perturbation)
            test_params = base_params.copy()
            test_params[param] = type(value)(value * mult)

            test_result = compute_signal_func(ohlcv, **test_params)
            test_metric = calculate_sharpe(test_result)
            results[f'{param}_{direction}'] = test_metric

    # Check: all variants should be within 30% of base
    all_metrics = list(results.values())
    spread = (max(all_metrics) - min(all_metrics)) / max(abs(base_metric), 0.01)

    return {
        'results': results,
        'spread': spread,
        'is_robust': spread < 0.3,
        'verdict': 'ROBUST' if spread < 0.3 else 'FRAGILE - likely noise'
    }
```

### **References**
  - Lo & MacKinlay, "Data-Snooping Biases in Tests of Financial Asset Pricing Models"

---

## You're Combining Redundant Indicators (Triple Counting)

### **Id**
indicator-redundancy
### **Severity**
CRITICAL
### **Description**
Many "multi-indicator" strategies just use the same information three times. RSI, Stochastic, and Williams %R all measure the same thing: where price is relative to its recent range.
### **Symptoms**
  - Strategy uses RSI + Stochastic + Williams %R (all overbought/oversold)
  - Strategy uses SMA(50) + SMA(100) + SMA(200) (all trend direction)
  - Strategy uses MACD + ROC + momentum (all rate of change)
  - More indicators doesn't improve out-of-sample results
### **Detection Pattern**
rsi.*stochastic|sma.*ema.*ma|multiple.*indicator|combine.*signal
### **Solution**

**Indicator Correlation Groups (DO NOT mix within a group):**

| Group | Members | What They All Measure |
|-------|---------|----------------------|
| **Overbought/Oversold** | RSI, Stochastic %K, Williams %R, CCI | Position in recent range |
| **Trend Direction** | SMA, EMA, MACD signal, price vs MA | Average price direction |
| **Rate of Change** | ROC, Momentum, MACD histogram | Speed of price change |
| **Volatility** | ATR, Bollinger Width, Standard Dev | Price dispersion |
| **Volume Flow** | OBV, A/D Line, MFI, Volume-Price Trend | Buying/selling pressure |

**The Diversity Rule:**
A good composite signal uses ONE indicator from each of 2-3 DIFFERENT groups:
- GOOD: RSI (overbought/oversold) + OBV trend (volume flow) + ATR percentile (volatility)
- BAD: RSI + Stochastic + Williams %R (all overbought/oversold)
- BAD: SMA(20) + SMA(50) + EMA(100) (all trend direction)

**How to check for redundancy:**
```python
def check_indicator_correlation(indicators: pd.DataFrame) -> pd.DataFrame:
    """
    Compute correlation matrix between indicators.
    Correlation > 0.7 means they're measuring the same thing.
    """
    corr = indicators.corr()

    redundant_pairs = []
    for i in range(len(corr)):
        for j in range(i+1, len(corr)):
            if abs(corr.iloc[i, j]) > 0.7:
                redundant_pairs.append(
                    (corr.index[i], corr.columns[j], round(corr.iloc[i, j], 2))
                )

    return {
        'correlation_matrix': corr,
        'redundant_pairs': redundant_pairs,
        'has_redundancy': len(redundant_pairs) > 0,
        'action': 'Remove one indicator from each redundant pair'
    }
```

### **References**
  - Technical analysis indicator categorization literature

---

## The Data Mining Trap: You Tested 100 Indicator Combinations

### **Id**
indicator-mining-bias
### **Severity**
CRITICAL
### **Description**
When you try many indicator combinations, you WILL find ones that "work" by pure chance. Each combination tested increases the probability of false discovery.
### **Symptoms**
  - "I tested RSI at every threshold from 10 to 90 and found 27 works best"
  - "I tried all MA crossover pairs and found 47/193 is optimal"
  - "After trying 50 indicator combinations, I found 3 that work"
  - Strategy was found by scanning, not by hypothesis
### **Detection Pattern**
test.*combination|try.*indicator|optimize|scan|search.*pattern
### **Solution**

**The Right Way to Mine Strategies from OHLCV + P/E:**

1. **Start with a behavioral hypothesis** (not a screen)
   - BAD: "Let me test every RSI threshold"
   - GOOD: "Panic selling creates RSI oversold bounces in stocks with earnings support (low P/E)"

2. **Pre-specify your signal BEFORE looking at results**
   - Write down: indicator, threshold, holding period, universe
   - THEN compute. Don't iterate on parameters.

3. **Use standard parameter values**
   - RSI: 14 (not 11 or 17)
   - Bollinger: 20 period, 2 std (not 18 period, 1.8 std)
   - SMA: 20, 50, 100, 200 (not 47, 193)
   - ATR: 14 or 20
   - If non-standard parameters are needed, the edge is fragile.

4. **Apply the Bonferroni haircut**
```python
def adjusted_sharpe_after_mining(
    observed_sharpe: float,
    n_combinations_tested: int,
    backtest_years: float
) -> dict:
    """
    Adjust Sharpe ratio for multiple testing.
    """
    import scipy.stats as stats

    # Convert Sharpe to t-statistic
    t_stat = observed_sharpe * np.sqrt(backtest_years)

    # Bonferroni-adjusted p-value
    raw_p = 2 * (1 - stats.norm.cdf(abs(t_stat)))
    adjusted_p = min(raw_p * n_combinations_tested, 1.0)

    return {
        'observed_sharpe': observed_sharpe,
        'raw_t_stat': round(t_stat, 2),
        'raw_p_value': round(raw_p, 4),
        'adjusted_p_value': round(adjusted_p, 4),
        'still_significant': adjusted_p < 0.05,
        'warning': (
            'Signal remains significant after correction'
            if adjusted_p < 0.05
            else f'NOT significant after testing {n_combinations_tested} combinations'
        )
    }
```

### **References**
  - Harvey, Liu & Zhu, "...and the Cross-Section of Expected Returns" (2016)

---

## Your Backtest Period Is One Regime

### **Id**
single-regime-backtest
### **Severity**
CRITICAL
### **Description**
A strategy backtested on 2010-2024 mostly tested a bull market. Technical indicators behave completely differently in bear markets and choppy markets.
### **Symptoms**
  - Strategy only backtested during bull market
  - Momentum signal in a 14-year uptrend
  - RSI never reaches oversold in a bull market
  - "Works great since 2010" (= no meaningful drawdowns tested)
### **Detection Pattern**
2010.*202|since.*2009|bull.*market|recent.*history
### **Solution**

**How Technical Indicators Behave By Regime:**

| Indicator Signal | Bull Market | Bear Market | Choppy/Range |
|-----------------|-------------|-------------|-------------|
| RSI < 30 (buy) | Rare, very profitable | Frequent, often fails | Moderate, mixed |
| RSI > 70 (sell) | Frequent, often wrong | Rare, very profitable | Moderate, mixed |
| MA crossover (buy) | Frequent, profitable | Frequent, whipsaw losses | Frequent, whipsaw |
| Bollinger breakout up | Works well | False breakouts common | False breakouts |
| Volume surge + price up | Strong continuation | Short squeeze, reverses | Noise |
| New 52-week high | Continuation | N/A | Mixed |

**Minimum regime coverage for OHLCV-based strategies:**
- Must include 2008 (bear) or 2022 (bear) at minimum
- Must include 2011, 2015, 2018 (corrections)
- Must include 2020 Q1 (crash) AND 2020 Q2-Q4 (recovery)
- Must include at least 2 years of range-bound market

**Regime-Specific Testing Protocol:**
```python
def regime_stress_test(strategy_returns: pd.Series) -> dict:
    """Test strategy across known market regimes."""
    regimes = {
        'Bull_2013_2015': ('2013-01', '2015-07'),
        'China_shock_2015': ('2015-08', '2015-10'),
        'Bull_2016_2018': ('2016-03', '2018-09'),
        'Q4_2018_selloff': ('2018-10', '2018-12'),
        'Recovery_2019': ('2019-01', '2019-12'),
        'Covid_crash': ('2020-02', '2020-03'),
        'Covid_recovery': ('2020-04', '2020-12'),
        'Bull_2021': ('2021-01', '2021-12'),
        'Bear_2022': ('2022-01', '2022-10'),
        'Recovery_2023': ('2023-01', '2023-12'),
    }

    results = {}
    for name, (start, end) in regimes.items():
        period = strategy_returns[start:end]
        if len(period) > 0:
            ann_return = period.mean() * 252
            ann_vol = period.std() * np.sqrt(252)
            results[name] = {
                'return': round(ann_return, 3),
                'volatility': round(ann_vol, 3),
                'sharpe': round(ann_return / max(ann_vol, 0.01), 2),
                'max_drawdown': round((period.cumsum().cummax() - period.cumsum()).max(), 3)
            }

    # Strategy should be profitable in at least 60% of regimes
    profitable = sum(1 for r in results.values() if r['return'] > 0)
    return {
        'regime_results': results,
        'profitable_regimes': f'{profitable}/{len(results)}',
        'regime_robust': profitable >= len(results) * 0.6
    }
```

### **References**
  - Market regime analysis literature

---

## The Adjusted Price Trap: Your Signal Is Computing on Wrong Data

### **Id**
price-adjustment-errors
### **Severity**
HIGH
### **Description**
Stock splits, dividends, and corporate actions create discontinuities in OHLCV data that break technical indicator calculations
### **Symptoms**
  - Enormous one-day "returns" on split days
  - Volume spikes of 10-100x on split-adjusted data
  - RSI/MACD giving extreme signals on adjustment days
  - Moving averages with unexplained jumps
### **Detection Pattern**
split|adjust|dividend|corporate.*action|spike|outlier
### **Solution**

**The Adjustment Problem for OHLCV Strategies:**

| Data Type | Use Adjusted? | Why |
|-----------|--------------|-----|
| Close (for returns, MA, RSI) | YES - split & dividend adjusted | Returns must be continuous |
| Volume | CAREFUL - split-adjusted but dividend-unadjusted | Splits change share count, not activity |
| Open, High, Low | DEPENDS on indicator | Candle patterns need consistent OHLC |
| P/E | Use point-in-time | Adjusted for splits automatically |

**Common Mistakes:**
1. **Mixing adjusted and unadjusted prices** in the same indicator
2. **Volume not adjusted for splits** → a 2:1 split doubles volume artificially
3. **Computing indicators on raw data then comparing to adjusted prices**
4. **Gap signals triggered by ex-dividend adjustments** (not real gaps)

**Data Hygiene Checks:**
```python
def check_ohlcv_quality(ohlcv: pd.DataFrame) -> dict:
    """Run before any signal computation."""
    issues = []

    close = ohlcv['Close']
    volume = ohlcv['Volume']
    high = ohlcv['High']
    low = ohlcv['Low']

    # 1. Impossible returns (>50% daily move → likely data error or split)
    daily_returns = close.pct_change().abs()
    extreme = daily_returns > 0.5
    if extreme.any():
        issues.append(f'Extreme returns detected: {extreme.sum()} days with >50% move')

    # 2. Volume anomalies (>10x average → likely split or error)
    vol_ratio = volume / volume.rolling(20).median()
    vol_extreme = vol_ratio > 10
    if vol_extreme.any():
        issues.append(f'Volume anomalies: {vol_extreme.sum()} days with >10x median volume')

    # 3. OHLC consistency: High >= max(Open, Close), Low <= min(Open, Close)
    high_ok = (high >= ohlcv[['Open', 'Close']].max(axis=1)).all()
    low_ok = (low <= ohlcv[['Open', 'Close']].min(axis=1)).all()
    if not high_ok or not low_ok:
        issues.append('OHLC consistency violated: High < max(O,C) or Low > min(O,C)')

    # 4. Zero or negative prices
    if (close <= 0).any():
        issues.append(f'Zero/negative prices: {(close <= 0).sum()} occurrences')

    return {
        'issues': issues,
        'is_clean': len(issues) == 0,
        'recommendation': 'Fix issues before computing any indicators'
    }
```

### **References**
  - CRSP data adjustment methodology

---

## The Survivorship Bias: Your Technical Screen Only Tests Winners

### **Id**
survivorship-in-technical-screening
### **Severity**
HIGH
### **Description**
Testing technical strategies on current index members inflates returns because stocks that were delisted (often after big drops) are excluded
### **Symptoms**
  - Testing "S&P 500 stocks" using today's membership list historically
  - Mean reversion strategy shows amazing returns (delisted stocks that went to zero are excluded)
  - Free data from Yahoo Finance (usually survivors only)
  - Strategy "works" on current large caps
### **Detection Pattern**
sp500|current.*member|yahoo|yfinance|index.*constituent
### **Solution**

**Impact on Technical Strategy Types:**

| Strategy | Survivorship Bias Impact | Why |
|----------|-------------------------|-----|
| Momentum (long winners) | MODERATE: inflates top decile returns | Winners stay in index |
| Mean reversion (buy dips) | SEVERE: hides permanent losers | Dip buyers on delisted stocks lose 100% |
| Breakout (buy new highs) | LOW to MODERATE | New highs usually aren't near delisting |
| Value (low P/E) | SEVERE: low P/E stocks delist at higher rates | Cheap stocks go bankrupt more often |
| Volume signals | MODERATE: delisted stocks had unusual volume before delisting | Missing the bad volume signals |

**The Practical Haircut for Free Data:**
If using Yahoo Finance / free data with survivorship bias:
- Momentum strategies: subtract 1% annual return
- Mean reversion strategies: subtract 2-3% annual return
- Value-price strategies: subtract 2% annual return
- Breakout strategies: subtract 0.5-1% annual return

### **References**
  - Brown et al., "Survivorship Bias in Performance Studies"

---

## The Turnover Illusion: Your Technical Signal Trades Too Much

### **Id**
technical-signal-overtrades
### **Severity**
HIGH
### **Description**
Technical indicators change frequently; naive implementation creates enormous turnover that eats all alpha
### **Symptoms**
  - Signal changes every day/week based on indicator crossings
  - Portfolio turnover > 500% annually
  - High estimated alpha but even higher transaction costs
  - RSI bounces around 30/70 boundaries causing rapid entry/exit
### **Detection Pattern**
turnover|rebalance|trade.*frequency|transaction.*cost|whipsaw
### **Solution**

**Turnover by Indicator Type (without buffering):**

| Indicator Signal | Naive Turnover | With Buffer | Mid-Term Target |
|-----------------|---------------|-------------|-----------------|
| RSI cross 30/70 | 1000%+ annually | 200-400% | Use 25/75 entry, 40/60 exit |
| SMA crossover | 400-800% | 100-200% | Use dead zone (+-2% around MA) |
| Bollinger breakout | 300-600% | 100-200% | Add holding period minimum |
| MACD crossover | 600-1000% | 200-300% | Add histogram threshold |

**Turnover Reduction Techniques for Mid-Term Strategies:**

```python
def apply_buffer_rules(
    signal: pd.Series,
    entry_threshold: float,
    exit_threshold: float,
    min_hold_days: int = 5
) -> pd.Series:
    """
    Reduce turnover with asymmetric entry/exit thresholds
    and minimum holding period.
    """
    position = pd.Series(0.0, index=signal.index)
    current_position = 0
    days_in_position = 0

    for i in range(len(signal)):
        days_in_position += 1

        if current_position == 0:
            # Entry: stricter threshold
            if signal.iloc[i] > entry_threshold:
                current_position = 1
                days_in_position = 0
            elif signal.iloc[i] < -entry_threshold:
                current_position = -1
                days_in_position = 0
        else:
            # Exit: looser threshold + minimum hold
            if days_in_position >= min_hold_days:
                if current_position > 0 and signal.iloc[i] < -exit_threshold:
                    current_position = 0
                elif current_position < 0 and signal.iloc[i] > exit_threshold:
                    current_position = 0

        position.iloc[i] = current_position

    return position
```

**The 3x Cost Rule:**
Annual gross alpha must be >= 3x estimated annual transaction costs.
If a strategy generates 300 bps alpha but has 400% turnover at 10 bps/trade:
- Cost = 400% * 2 * 10 bps = 80 bps
- Alpha/Cost = 300/80 = 3.75x → Viable
- But at 30 bps/trade (small caps): Cost = 240 bps → Alpha/Cost = 1.25x → NOT viable

### **References**
  - Transaction cost analysis for systematic strategies

---

## The Lookback Bias: Your Indicator Uses Future Information

### **Id**
indicator-lookahead-bias
### **Severity**
HIGH
### **Description**
Some indicator calculations accidentally use future data through normalization, rolling max/min computed on full series, or adjusted prices not available at trade time
### **Symptoms**
  - Normalizing indicators by full-period statistics instead of expanding window
  - Using scipy/sklearn functions that normalize on full dataset
  - Bollinger Bands computed with pandas rolling that includes current bar
  - P/E data available only after quarterly filing, used on quarter-end date
### **Detection Pattern**
normalize|zscore|percentile|rolling.*max|full.*period
### **Solution**

**Common Lookahead Errors in OHLCV Strategies:**

1. **Full-period normalization**
   - BAD: `signal_z = (signal - signal.mean()) / signal.std()`
   - GOOD: `signal_z = (signal - signal.expanding().mean()) / signal.expanding().std()`

2. **P/E availability timing**
   - BAD: Using P/E data on earnings date
   - GOOD: Lag P/E by 1-2 days after earnings announcement

3. **Rolling window includes today**
   - BAD: Trade at close based on indicator computed using today's close
   - GOOD: Compute indicator at close, trade at next open (`shift(1)`)

4. **Global max/min**
   - BAD: `(price - price.min()) / (price.max() - price.min())`
   - GOOD: `(price - price.expanding().min()) / (price.expanding().max() - price.expanding().min())`

```python
def check_for_lookahead(signal_code: str) -> list:
    """Scan signal code for common lookahead patterns."""
    red_flags = []

    patterns = {
        '.mean()': 'Full-period mean → use .expanding().mean() or .rolling(N).mean()',
        '.std()': 'Full-period std → use .expanding().std() or .rolling(N).std()',
        '.max()': 'Full-period max → use .expanding().max() or .rolling(N).max()',
        '.min()': 'Full-period min → use .expanding().min() or .rolling(N).min()',
        'normalize': 'Check normalization window → must be expanding or rolling, not full',
        'shift(-': 'Negative shift → this IS future data',
        'sklearn': 'sklearn transforms often fit on full data → use incremental fit',
    }

    for pattern, warning in patterns.items():
        if pattern in signal_code:
            red_flags.append(f'POTENTIAL LOOKAHEAD: "{pattern}" found → {warning}')

    return red_flags
```

### **References**
  - Lopez de Prado, "Advances in Financial Machine Learning"

---

## The P/E Mirage: Trailing P/E Can Be Extremely Misleading

### **Id**
pe-ratio-traps
### **Severity**
MEDIUM
### **Description**
P/E ratio is the only fundamental data in our toolkit - use it carefully. Trailing P/E has many pitfalls that can generate false signals.
### **Symptoms**
  - Extremely low P/E stocks (< 5) that are actually distressed
  - Negative P/E (losses) treated as "cheap"
  - Cyclical stocks with low P/E at earnings peaks
  - P/E comparisons across sectors (tech vs utilities)
### **Detection Pattern**
pe.*ratio|earnings.*yield|cheap.*stock|valuation|price.*earn
### **Solution**

**P/E Pitfalls and Defenses:**

| Pitfall | Problem | Defense |
|---------|---------|---------|
| Negative earnings | P/E undefined or negative | Exclude stocks with PE < 0 or > 200 |
| Cyclical peaks | Low P/E at earnings peak = expensive | Use sector-relative P/E, not absolute |
| One-time items | Distorted EPS | Use median/average P/E over 4 quarters |
| Cross-sector comparison | Tech P/E 30 vs Bank P/E 10 ≠ comparable | Always rank within sector or use z-score |
| Stale data | P/E based on last quarter's earnings | Acknowledge 1-3 month lag |

**Safe P/E Signal Construction Rules:**
```python
def safe_pe_signal(pe: pd.Series) -> pd.Series:
    """Construct P/E-based signal with proper handling of edge cases."""

    # 1. Remove nonsensical P/E values
    pe_clean = pe.copy()
    pe_clean[pe_clean <= 0] = np.nan      # Negative earnings
    pe_clean[pe_clean > 200] = np.nan     # Extreme outliers

    # 2. Rank within cross-section (sector-neutral if possible)
    pe_rank = pe_clean.rank(pct=True)

    # 3. Value score: lower P/E = higher score
    value_score = 1 - pe_rank

    # 4. Sanity: require at least 20 stocks with valid P/E
    valid_count = pe_clean.notna().sum()
    if valid_count < 20:
        return pd.Series(np.nan, index=pe.index)

    return value_score
```

### **References**
  - Shiller, Campbell & Vuolteenaho on earnings-based predictors

---

## The Crowding Problem: Everyone Read the Same Textbook

### **Id**
crowded-signal-trap
### **Severity**
HIGH
### **Description**
The most well-known price-based strategies (RSI < 30 buy, golden cross, Bollinger breakout) are taught in every trading course. When millions of traders use the same signal, it gets arbitraged away or, worse, creates predictable stop-loss clusters that large players exploit.
### **Symptoms**
  - Strategy uses only textbook-standard signals with no novel twist
  - Signal is the first example in any technical analysis tutorial
  - Strategy description sounds like it was copied from Investopedia
  - No explanation of why the edge hasn't been arbitraged away
### **Detection Pattern**
golden.*cross|death.*cross|rsi.*30|rsi.*70|macd.*cross|basic.*strategy
### **Solution**

**How to Add a Non-Crowded Edge to a Known Signal:**

1. **Add a confirming dimension from a different category**: RSI < 30 alone is crowded. RSI < 30 + volume climax + P/E < median is not.
2. **Use non-obvious parameter windows**: Instead of SMA(50)/SMA(200), try SMA(63)/SMA(252) — same concept, different trigger timing.
3. **Add a conditional filter**: "RSI < 30 ONLY when ATR is in the top quartile" is much less crowded than "RSI < 30."
4. **Cross-sectional ranking**: "Buy the 10 stocks with the lowest RSI" is less crowded than "buy any stock with RSI < 30."
5. **Explain why it persists**: If you can't explain why this edge hasn't been arbitraged, it probably has been.

**The Crowding Test:**
- Can you describe this strategy in one sentence that any retail trader would recognize?
- If yes → the signal is crowded and needs a differentiating filter.
- If no → you may have something less crowded.

### **References**
  - Lou & Polk, "Comomentum" (crowding in momentum strategies)
  - Stein, "Sophisticated Investors and Market Efficiency"

---

## The Narrative Fallacy: Compelling Story ≠ Profitable Strategy

### **Id**
narrative-over-evidence
### **Severity**
MEDIUM
### **Description**
Human brains are wired to find narratives. "Institutions accumulate over weeks, creating OBV divergence" sounds compelling, but sounding logical doesn't mean it works. Many plausible-sounding strategies have zero predictive power.
### **Symptoms**
  - Strategy idea is built entirely around a story without considering if the effect size is meaningful
  - "It makes sense that..." is the primary justification
  - No consideration of effect magnitude (is the edge 10 bps or 200 bps?)
  - Narrative could equally justify the opposite trade
### **Detection Pattern**
makes.*sense|logical|intuitive|obviously|clearly|must.*work
### **Solution**

**The Counter-Narrative Test:**
For every strategy idea, construct the opposite narrative and see if it's equally compelling:

- Original: "RSI < 30 means panic selling, so price will bounce"
- Counter: "RSI < 30 means smart money is selling ahead of bad news, so price will continue falling"
- If both narratives are equally plausible, the story alone doesn't create an edge.

**What to Do Instead:**
1. Narrative is necessary but not sufficient — you need behavioral rationale AND structural mechanism
2. Ask: "Who is systematically wrong?" — if you can't identify the loser, you might be the loser
3. Ask: "What would need to change for this to stop working?" — if the answer is vague, the edge is vague
4. Prefer signals with known academic documentation over "it just makes sense"

**Red Flag Phrases in Your Own Reasoning:**
- "Obviously this would work because..."
- "It makes intuitive sense that..."
- "The market clearly overreacts to..."
- "Everyone knows that..." (if everyone knows, it's priced in)

### **References**
  - Taleb, "Fooled by Randomness"
  - Kahneman & Tversky, "Judgment under Uncertainty: Heuristics and Biases"
