# US Market Configuration

All market-specific parameters for US-listed equities. Other skills read this file via `references/markets/{market}.md`. When adding a new market, copy this structure and adjust values.

---

## Market Parameters

| Parameter | Value |
|-----------|-------|
| market | US |
| exchanges | NYSE / NASDAQ / AMEX |
| ticker_format | Plain alpha (e.g., AAPL, MSFT, NVDA) — no suffix |
| currency | USD |
| accounting_standard | US GAAP |

---

## Decision Thresholds

These thresholds are shared by all skills for US equities. Modify here to adjust globally.

| Parameter | Variable | Default | Description |
|-----------|----------|---------|-------------|
| Horizon | {HORIZON} | 24 months | Expected holding period |
| Benchmark | {benchmark} | S&P 500 | Performance comparison index |
| Alpha target | {ALPHA_BPS} | +300 bps | Excess return target |
| Hurdle total return | {HURDLE_TR_%} | 30% | Minimum 24-month total return |
| Margin of safety | {MOS_%} | 25% | Required discount to fair value |
| Skew ratio | {SKEW_X} | 1.7× | Minimum E[TR] / |Bear drawdown| |
| Quality pass | {QUALITY_PASS} | 70 | Minimum quality score for Buy |
| Quality sell | {QUALITY_SELL} | 60 | Quality score triggering Sell |

---

## Rating Definitions

| Rating | Condition | Action |
|--------|-----------|--------|
| **Buy** | All 4 gates pass + Quality ≥ {QUALITY_PASS} | Initiate or add position |
| **Hold** | Already held, price is fair | Maintain current position |
| **Await Entry** | Quality strong but price too high | Wait for better entry |
| **Sell** | Quality < {QUALITY_SELL} or fundamentals deteriorating | Reduce or exit position |

---

## 4 Entry Gates

1. **Expected Return Gate**: E[TR] ≥ {HURDLE_TR_%}
2. **Margin of Safety Gate**: Current price ≤ Fair Value × (1 − {MOS_%})
3. **Skew Gate**: E[TR] ÷ |Bear Drawdown| ≥ {SKEW_X}
4. **"Why Now" Gate**: Dated catalyst exists within {HORIZON}

Any gate failure → rating cannot be Buy.

---

## Regulatory & Filing Sources

| Source | URL | Use |
|--------|-----|-----|
| SEC EDGAR | https://efts.sec.gov/LATEST/search-index?q={ticker} | 10-K, 10-Q, 8-K, DEF 14A |
| SEC Full-Text Search | https://efts.sec.gov/LATEST/search-index?q=%22{company_name}%22 | Full-text search |

---

## Macro Data Sources

| Source | URL | Key Indicators |
|--------|-----|----------------|
| FRED | https://api.stlouisfed.org/fred/series/observations | Fed Funds Rate, CPI, GDP, Unemployment |

---

## Market-Specific Risks

In §18 Risk Inventory, additionally evaluate:

- Federal interest rate policy impact on valuations
- SEC regulatory changes (e.g., AI regulation, ESG disclosure requirements)
- US-China supply chain exposure (if applicable)

---

## Ticker Validation Rules

- Must be listed on NYSE / NASDAQ / AMEX
- Reject OTC, foreign-only, or delisted tickers
- Verify via WebSearch: `"{ticker} stock NYSE OR NASDAQ"`
