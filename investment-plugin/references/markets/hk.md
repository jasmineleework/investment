# HK Market Configuration

All market-specific parameters for Hong Kong-listed equities (HKEX). Other skills read this file via `references/markets/{market}.md`. Structure mirrors `us.md`.

---

## Market Parameters

| Parameter | Value |
|-----------|-------|
| market | HK |
| exchanges | HKEX (Main Board / GEM) |
| ticker_format | See "Ticker Formats & Conversion" below — canonical form is `XXXX.HK` |
| currency | HKD (trading currency) |
| reporting_currency | Varies by company — many mainland-China issuers report in RMB. The Data Contract MUST record both trading currency (HKD) and reporting currency, and state the FX rate used for any conversion. |
| accounting_standard | IFRS / HKFRS |

### Ticker Formats & Conversion

The same stock has three representations across data sources. Always normalize user input to the canonical form, then convert per source:

| Context | Format | Example (Tencent) |
|---------|--------|-------------------|
| Canonical (memo, Data Contract, `Research/{ticker}/`) | `XXXX.HK` (no leading-zero padding beyond 4 digits) | `0700.HK` |
| yfinance MCP / yahoo_fetch.py | `XXXX.HK` | `0700.HK` |
| moomoo OpenAPI scripts | `HK.XXXXX` (5-digit, zero-padded) | `HK.00700` |
| AkShare (akshare_hk_fetch.py) | 5-digit numeric string | `00700` |

Conversion rule: strip prefixes/suffixes to bare digits, zero-pad to 5 for moomoo/AkShare; strip leading zero to 4 digits + `.HK` for canonical/yfinance (5-digit codes ≥ 10000, e.g. GEM `8xxx` stays 4-digit).

---

## ADR Bridge (US filings for dual-listed companies)

Many HK-listed companies also trade in the US. Whether US filings exist depends on the ADR level:

| ADR type | Example | SEC filings | Action |
|----------|---------|-------------|--------|
| Level 2/3 — dual primary or secondary listing on NYSE/NASDAQ | BABA (9988.HK), JD (9618.HK), BIDU (9888.HK), NTES (9999.HK) | 20-F annual, 6-K interim | **Enable SEC EDGAR MCP** with the ADR ticker for filings full-text, segment data, and risk factors |
| Level 1 / unsponsored OTC | TCEHY (0700.HK) | None | Skip SEC EDGAR — use HKEXnews sources only |

**Detection rule** (Step 3 of data-fetch, HK branch): WebSearch `"{company_name} ADR NYSE OR NASDAQ 20-F"`. If a NYSE/NASDAQ listing with 20-F filings is confirmed, record `ADR Ticker` in the Data Contract Company Profile and route SEC EDGAR calls through it. Otherwise record `ADR Ticker: N/A (OTC or none)`.

---

## Decision Thresholds

Shared by all skills for HK equities. Values intentionally match `us.md` — the hurdle discipline is portfolio-wide, not market-specific.

| Parameter | Variable | Default | Description |
|-----------|----------|---------|-------------|
| Horizon | {HORIZON} | 24 months | Expected holding period |
| Benchmark | {benchmark} | Hang Seng Index (HSI); for tech names also report vs Hang Seng TECH (HSTECH) | Performance comparison index |
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

## WACC Inputs (HK-specific rules)

**Risk-free rate — determined by the currency of the company's cash flows, not the listing venue:**

| Cash flow currency | Risk-free rate | Source |
|--------------------|----------------|--------|
| RMB (mainland-China revenue base, e.g. Tencent, Meituan) | China 10Y government bond yield | `akshare_hk_fetch.py` (`bond_zh_us_rate`) |
| HKD / USD (HK-local or international revenue base) | US 10Y Treasury (HKD is USD-pegged) | `fred_fetch.py` |

- **ERP**: mature-market ERP plus a country risk premium appropriate to the revenue base. State both components explicitly in the Data Contract.
- **Beta**: raw beta only (no subjective adjustment — same guardrail as US). Use yfinance-provided beta when available; otherwise regress 2Y weekly returns against HSI.
- Terminal growth guardrail unchanged: g ≤ 3.0%.

---

## Regulatory & Filing Sources

| Source | URL | Use |
|--------|-----|-----|
| HKEXnews Title Search | https://www1.hkexnews.hk/search/titlesearch.xhtml | Annual/interim reports, results announcements, circulars |
| HKEXnews Disclosure of Interests (DI) | https://www2.hkexnews.hk/Shareholding-Disclosures/Disclosure-of-Interests | Substantial shareholder & director dealings (SEC Form 4 equivalent) |
| SEC EDGAR (via ADR bridge only) | https://efts.sec.gov/LATEST/search-index?q={adr_ticker} | 20-F, 6-K for dual-listed companies |
| Company IR page | (per company) | Results PDF, earnings call transcripts |

No free official API exists for HKEXnews — access via WebSearch/WebFetch (Tier 3).

---

## Macro Data Sources

| Source | URL | Key Indicators |
|--------|-----|----------------|
| HKMA | https://www.hkma.gov.hk/eng/data-publications-and-research/ | HKD rates, aggregate balance |
| FRED | https://api.stlouisfed.org/fred/series/observations | US 10Y (HKD peg), Fed Funds Rate |
| AkShare `bond_zh_us_rate` | (Python interface) | China 10Y government bond yield |

---

## Market-Specific Risks

In §18 Risk Inventory, additionally evaluate:

- Mainland-China regulatory exposure (antitrust, data security, industry-specific licensing e.g. game approvals)
- US-China geopolitical risk: ADR delisting (HFCAA/PCAOB), export controls (AI chips), sanctions
- VIE structure risk where applicable (contractual control vs equity ownership)
- HKD-USD peg stability and RMB FX translation for mainland revenue bases
- Southbound (港股通) flow dependence — liquidity and marginal-buyer concentration
- Lower disclosure frequency vs US (semi-annual full statements; Q1/Q3 often abbreviated)

---

## Insider & Ownership Data Rules

HKEX has no free programmatic equivalent of SEC Form 4 feeds. In the Data Contract:

- Insider Activity: search HKEXnews DI for the past 180 days (Tier 3). If no reportable activity is found, record `N/A (DI checked YYYY-MM-DD, no reportable activity)` — this does **not** count as a coverage FAIL.
- Institutional Ownership: use yfinance holder data when available; otherwise DI substantial-shareholder filings; otherwise `N/A` with the same evidence convention.

---

## Ticker Validation Rules

- Must be listed on HKEX Main Board or GEM
- Reject delisted or suspended-pending-delisting tickers
- Verify via WebSearch: `"{ticker} stock HKEX"`
- Normalize to canonical `XXXX.HK` before creating `Research/{ticker}/`
