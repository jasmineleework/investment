# 美股市场配置

## 市场参数

| 参数 | 值 |
|------|-----|
| market | US |
| 交易所 | NYSE / NASDAQ / AMEX |
| Ticker 格式 | AAPL, MSFT, NVDA（纯字母，无后缀） |
| 货币 | USD |
| 会计准则 | US GAAP |
| 基准指数 | S&P 500 |

## 监管披露源

| 来源 | URL | 用途 |
|------|-----|------|
| SEC EDGAR | https://efts.sec.gov/LATEST/search-index?q={ticker} | 10-K, 10-Q, 8-K, DEF 14A |
| SEC Full-Text Search API | https://efts.sec.gov/LATEST/search-index?q=%22{company_name}%22 | 全文检索 |

## 宏观数据源

| 来源 | URL | 关键指标 |
|------|-----|----------|
| FRED | https://api.stlouisfed.org/fred/series/observations | Fed Funds Rate, CPI, GDP, Unemployment |

## 市场特有风险项

在 §18 Risk Inventory 中需额外评估：
- 联邦利率政策对估值的影响
- SEC 监管变化（如 AI 监管、ESG 披露要求）
- 中美关系对供应链的影响（如适用）

## Ticker 验证规则

- 必须为 NYSE / NASDAQ / AMEX 上市
- 拒绝 OTC、仅外国上市、已退市的标的
- 用 WebSearch 验证："{ticker} stock NYSE OR NASDAQ"
