# Academic Sources & Seminal Works

> Curated catalog of peer-reviewed papers and foundational books that underpin
> the behavioral and structural rationales used in mid-term quantitative strategy mining.
>
> **How to use**: When constructing a strategy rationale, cite relevant papers from this list.
> When a user asks "why should this work?", point them here. Papers are grouped by
> the strategy family they support.

---

## Momentum & Trend Following

| Citation | Key Finding | Strategy Application |
|----------|------------|---------------------|
| Jegadeesh & Titman (1993), "Returns to Buying Winners and Selling Losers" | Stocks with high past returns continue to outperform for 3-12 months | Cross-sectional momentum ranking strategies |
| Jegadeesh & Titman (2001), "Profitability of Momentum Strategies: An Evaluation of Alternative Explanations" | Momentum profits are not explained by risk; partially behavioral | Reinforces momentum as a behavioral anomaly |
| Asness, Moskowitz & Pedersen (2013), "Value and Momentum Everywhere" | Momentum works across asset classes and countries | Broad applicability of momentum signals |
| Moskowitz, Ooi & Pedersen (2012), "Time Series Momentum" | Past 12-month return predicts future returns for individual assets | Time-series (absolute) momentum strategies |
| George & Hwang (2004), "The 52-Week High and Momentum Investing" | Proximity to 52-week high explains momentum profits | Anchoring-based momentum signals |
| Grinblatt & Han (2005), "Prospect Theory, Mental Accounting, and Momentum" | Disposition effect (sell winners, hold losers) drives momentum | Disposition-based entry timing |

## Mean Reversion & Overreaction

| Citation | Key Finding | Strategy Application |
|----------|------------|---------------------|
| De Bondt & Thaler (1985), "Does the Stock Market Overreact?" | Past losers outperform past winners over 3-5 years | Long-term contrarian / value strategies |
| De Bondt & Thaler (1987), "Further Evidence On Investor Overreaction" | Overreaction is stronger for losers than winners | Asymmetric mean reversion signals |
| Campbell, Grossman & Wang (1993), "Trading Volume and Serial Correlation in Stock Returns" | High-volume declines reverse more than low-volume declines | Volume-confirmed mean reversion |
| Lehmann (1990), "Fads, Martingales, and Market Efficiency" | Short-term (weekly) reversals exist in stock returns | Short-term (1-4 week) mean reversion |
| Avramov, Chordia & Goyal (2006), "Liquidity and Autocorrelations in Individual Stock Returns" | Liquidity and volume interact with return predictability | Volume-conditional reversal signals |

## Volume & Liquidity Signals

| Citation | Key Finding | Strategy Application |
|----------|------------|---------------------|
| Lee & Swaminathan (2000), "Price Momentum and Trading Volume" | Volume predicts momentum lifecycle — high volume winners reverse sooner | Volume-momentum interaction strategies |
| Gervais, Kaniel & Mingelgrin (2001), "The High-Volume Return Premium" | Stocks with abnormally high volume earn excess returns over subsequent weeks | Volume-surge entry signals |
| Blume, Easley & O'Hara (1994), "Market Statistics and Technical Analysis: The Role of Volume" | Volume provides information about quality of traders' signals | Volume as signal confirmation layer |
| Llorente et al. (2002), "Dynamic Volume-Return Relation of Individual Stocks" | Volume-return correlation differentiates informed from liquidity trades | Volume-return interaction for filtering |
| Chordia & Swaminathan (2000), "Trading Volume and Cross-Autocorrelations in Stock Returns" | High-volume stocks lead low-volume stocks | Cross-asset volume-leading-price signals |

## Volatility & Risk

| Citation | Key Finding | Strategy Application |
|----------|------------|---------------------|
| Bollerslev (1986), "Generalized Autoregressive Conditional Heteroskedasticity" | Volatility clusters — low vol precedes high vol | Volatility compression/expansion strategies |
| Ang et al. (2006), "The Cross-Section of Volatility and Expected Returns" | High idiosyncratic volatility predicts low future returns | Low-vol anomaly; vol-based ranking |
| Engle (1982), "Autoregressive Conditional Heteroscedasticity" | ARCH effects in financial returns | Foundation for volatility regime models |
| Baker, Bradley & Wurgler (2011), "Benchmarks as Limits to Arbitrage" | Low-volatility stocks outperform high-volatility stocks | Low-vol anomaly strategies |

## Behavioral Finance Foundations

| Citation | Key Finding | Strategy Application |
|----------|------------|---------------------|
| Kahneman & Tversky (1979), "Prospect Theory" | Loss aversion, reference dependence, probability weighting | Foundation for disposition effect, panic selling signals |
| Tversky & Kahneman (1974), "Judgment under Uncertainty: Heuristics and Biases" | Anchoring, representativeness, availability heuristics | Anchoring to 52-week highs, round numbers |
| Barberis, Shleifer & Vishny (1998), "A Model of Investor Sentiment" | Conservatism → underreaction; representativeness → overreaction | Dual model for momentum + mean reversion |
| Daniel, Hirshleifer & Subrahmanyam (1998), "Investor Psychology and Security Market Under- and Overreactions" | Overconfidence + biased self-attribution | Momentum followed by long-term reversal |
| Hong & Stein (1999), "A Unified Theory of Underreaction, Momentum, and Overreaction" | Information diffuses slowly across heterogeneous traders | Gradual information incorporation signals |
| Shiller (2003), "From Efficient Markets Theory to Behavioral Finance" | Markets are not always efficient; sentiment drives prices | Overall justification for price-based strategies |

## Valuation (P/E) & Value Factors

| Citation | Key Finding | Strategy Application |
|----------|------------|---------------------|
| Fama & French (1992), "The Cross-Section of Expected Stock Returns" | Value (high B/M) stocks outperform growth stocks | P/E-based value ranking |
| Lakonishok, Shleifer & Vishny (1994), "Contrarian Investment, Extrapolation, and Risk" | Value strategies work because investors extrapolate past growth | P/E contrarian signals |
| Asness et al. (2015), "Fact, Fiction and Value Investing" | Value premium is robust but time-varying | P/E as long-term anchor, not timing signal |
| Novy-Marx (2013), "The Other Side of Value" | Profitability combined with value improves returns | Composite P/E + quality signals |

## Market Microstructure & Execution

| Citation | Key Finding | Strategy Application |
|----------|------------|---------------------|
| Kyle (1985), "Continuous Auctions and Insider Trading" | Informed traders hide in volume; price impact is proportional | Why large volume signals institutional activity |
| Easley & O'Hara (1987), "Price, Trade Size, and Information in Securities Markets" | Trade size carries information about informed trading | Volume-weighted signals have informational content |
| Hasbrouck (2007), "Empirical Market Microstructure" | Transaction costs, price impact, and implementation shortfall | Cost-awareness in strategy design |

## Data Mining & Statistical Pitfalls

| Citation | Key Finding | Strategy Application |
|----------|------------|---------------------|
| Harvey, Liu & Zhu (2016), "...and the Cross-Section of Expected Returns" | Most published factors are false discoveries; t > 3.0 needed | Multiple-testing correction for strategy mining |
| Lo & MacKinlay (1990), "Data-Snooping Biases in Tests of Financial Asset Pricing Models" | Data snooping inflates apparent alpha | Why hypothesis-first approach matters |
| McLean & Pontiff (2016), "Does Academic Research Destroy Stock Return Predictability?" | Published anomalies decay ~35% post-publication | Crowding and decay of known signals |
| Lopez de Prado (2018), "Advances in Financial Machine Learning" | Modern statistical techniques for avoiding overfitting | Robustness testing, combinatorial purged CV |
| Bailey et al. (2014), "Pseudo-Mathematics and Financial Charlatanism" | Sharpe ratio inflation from multiple testing | Deflated Sharpe Ratio for honest evaluation |

## Survivorship & Data Quality

| Citation | Key Finding | Strategy Application |
|----------|------------|---------------------|
| Brown et al. (1992), "Survivorship Bias in Performance Studies" | Survivorship bias inflates returns 1-3% annually | Haircuts for strategies tested on free data |
| Elton, Gruber & Blake (1996), "Survivorship Bias and Mutual Fund Performance" | Bias is ~1% per year for mutual funds | Calibration of expected bias magnitude |

---

## Key Books (Reference Shelf)

| Book | Author(s) | Relevance |
|------|-----------|-----------|
| *Expected Returns* | Antti Ilmanen | Comprehensive survey of return sources across assets |
| *Quantitative Equity Portfolio Management* | Chincarini & Kim | Practical factor model construction and implementation |
| *Active Portfolio Management* | Grinold & Kahn | Information ratio framework, alpha theory |
| *Advances in Financial Machine Learning* | Marcos Lopez de Prado | Modern ML pitfalls applied to finance |
| *Fooled by Randomness* / *The Black Swan* | Nassim Taleb | Epistemological humility in strategy development |
| *Bollinger on Bollinger Bands* | John Bollinger | Practical volatility-based signal construction |
| *A Non-Random Walk Down Wall Street* | Lo & MacKinlay | Statistical evidence for (and limits of) predictability |
| *Efficiently Inefficient* | Lasse Heje Pedersen | Why markets are "efficiently inefficient" — room for alpha |
