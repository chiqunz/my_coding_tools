# Data Sources for OHLCV + P/E

> Guidance on where to obtain daily OHLCV and P/E data, quality considerations,
> and known pitfalls for each source. This skill only uses **daily** data —
> no intra-day, tick, or sub-daily sources.

---

## Free / Open Sources

### Yahoo Finance (via `yfinance`)
- **Data**: Daily OHLCV, adjusted close (+dividends, splits). Limited fundamentals.
- **P/E**: Available via `.info["trailingPE"]` for current snapshot; no historical P/E time series.
- **Quality**: Split/dividend-adjusted. Generally reliable for large/mid caps post-2000.
- **Key Pitfalls**:
  - **Survivorship bias**: Only currently listed stocks. Delisted stocks disappear.
  - **Volume**: Split-adjusted volume can look anomalous on old dates.
  - **Adjusted close recalculations**: Historical adjusted close can change retroactively.
  - **Rate limits**: Aggressive scraping may get throttled.
- **Best for**: Quick prototyping on liquid US equities.
- **NOT suitable for**: Rigorous historical studies requiring delisted stocks.

```python
# Example: daily OHLCV via yfinance
import yfinance as yf
df = yf.download("AAPL", start="2015-01-01", end="2025-12-31")
# Columns: Open, High, Low, Close, Adj Close, Volume
```

### FRED (Federal Reserve Economic Data)
- **Data**: No individual stock OHLCV — macro/market indices only.
- **Useful for**: Market-level regime detection (VIX, term spread, credit spread) if
  extending beyond the strict OHLCV+P/E scope in the future.

### Kaggle Datasets
- **Data**: Various historical OHLCV datasets (e.g., "Huge Stock Market Dataset").
- **Quality**: Varies widely. Always run `data_quality.py` checks.
- **Key Pitfalls**: Often survivorship-biased. May be outdated. No guaranteed P/E.

---

## Paid / Professional Sources

### CRSP (Center for Research in Security Prices)
- **Data**: Daily OHLCV for all US-listed stocks since 1925. Includes delisted returns.
- **P/E**: Not directly; combine with Compustat for fundamentals.
- **Quality**: Gold standard for academic research. Survivorship-bias-free.
- **Key Pitfalls**: Expensive. Requires institutional access.
- **Best for**: Serious research with delisted stocks and long history.

### Compustat / Capital IQ
- **Data**: Fundamental data including EPS (for P/E construction). Not OHLCV.
- **P/E**: Constructible from price (CRSP) + EPS (Compustat). Point-in-time data available.
- **Key Pitfalls**: Point-in-time vs. restated data matters hugely for P/E signals.

### Sharadar (via Nasdaq Data Link / Quandl)
- **Data**: Daily OHLCV + fundamentals including P/E for US equities.
- **Quality**: Good. Includes delisted stocks. Point-in-time fundamentals available.
- **Price**: ~$20-50/month for personal use.
- **Best for**: Mid-budget researchers who need P/E history and delisted stocks.

### Polygon.io
- **Data**: Daily OHLCV for US stocks. Historical going back ~20 years.
- **P/E**: Not directly available; financials endpoints for EPS exist on paid plans.
- **Quality**: Good for price data. API-friendly.
- **Key Pitfalls**: Free tier has significant limitations.

### Alpha Vantage
- **Data**: Daily OHLCV + some fundamentals. JSON API.
- **P/E**: Available via fundamentals endpoint for current/quarterly.
- **Quality**: Acceptable for prototyping. Rate-limited on free tier.
- **Key Pitfalls**: Free tier = 25 API calls/day.

### EOD Historical Data
- **Data**: Daily OHLCV + fundamentals including P/E for global equities.
- **Quality**: Good coverage. Includes delisted tickers.
- **Price**: ~$20-80/month depending on tier.

### Norgate Data
- **Data**: Daily OHLCV for US, Australia, futures. Includes delisted stocks.
- **Quality**: Excellent. Survivorship-bias-free. Clean adjustments.
- **Price**: ~$30-55/month.
- **Best for**: Serious individual researchers on a budget.

---

## Data Quality Checklist

Before using ANY data source for strategy research, verify:

| Check | Tool | Why |
|-------|------|-----|
| OHLC consistency (H ≥ max(O,C), L ≤ min(O,C)) | `data_quality.check_ohlc_consistency()` | Corrupt data breaks all indicators |
| No extreme returns (>50% daily) without known cause | `data_quality.check_extreme_returns()` | Likely unadjusted splits |
| Volume not anomalous (>10× median) | `data_quality.check_volume_anomalies()` | May indicate split or data error |
| No zero/negative prices | `data_quality.check_zero_or_negative_prices()` | Data corruption |
| Not too many zero-volume days | `data_quality.check_zero_volume_days()` | Illiquid or delisted stock |
| No stale prices (5+ identical closes) | `data_quality.check_stale_prices()` | Frozen/stale data feed |
| No large date gaps | `data_quality.check_date_gaps()` | Missing trading days |
| P/E values cleaned (no negative, no >200) | `signal_utils.clean_pe()` | Garbage P/E → garbage signals |

---

## Survivorship Bias Haircuts

When using free data that only covers currently listed stocks (Yahoo Finance, etc.),
apply these return haircuts to your expected alpha:

| Strategy Type | Annual Haircut | Why |
|---------------|---------------|-----|
| Momentum (long winners) | −100 bps | Winners stay in the index; bias is moderate |
| Mean reversion (buy dips) | −200 to −300 bps | Stocks that dip and delist are invisible |
| Value / low P/E | −200 bps | Cheap stocks fail more often |
| Breakout | −50 to −100 bps | Breakout stocks less likely to delist soon |
| Volume signals | −100 to −150 bps | Unusual volume before delisting is missed |

---

## P/E Data Construction Notes

If your data source provides EPS but not P/E directly:

```python
def construct_pe(close: pd.Series, eps_ttm: pd.Series) -> pd.Series:
    """
    Construct trailing P/E from close price and trailing-twelve-month EPS.

    CRITICAL: Use point-in-time EPS — the EPS known at each date,
    not the restated/final EPS. Using restated EPS is lookahead bias.
    """
    pe = close / eps_ttm
    # Clean: remove negative and extreme values
    pe[pe <= 0] = float("nan")
    pe[pe > 200] = float("nan")
    return pe
```

**Point-in-time vs. Restated Data**:
- P/E computed from restated EPS is lookahead bias — the final EPS may differ
  from what was known when the trade decision was made.
- Use point-in-time EPS (as-reported on earnings date, lagged by filing delay).
- Filing delay: assume data available ~2 days after earnings announcement for
  large caps, ~5-10 days for small caps.
