# Smart Money Signals Scoring Reference

Three-layer signal system for evaluating institutional and insider positioning. Used in Phase 3 (quick version) and Phase 4 (deep version) of the narrative screener.

---

## Formula

```
Smart Money Score (0-100) = Analyst Signal × 0.30 + Insider Signal × 0.40 + Institutional Signal × 0.30
```

**Insider transactions carry the highest weight (0.40)** — insiders have more information advantage than external analysts or institutions. Insider buying is an asymmetric signal: there are many legitimate reasons to sell, but buying with personal capital typically signals genuine conviction.

---

## Layer 1: Analyst Signal (Weight: 30%)

### Data Sources

**Phase 3 (Quick)**:
```
yfinance: get_recommendations(symbol="{ticker}")
```

**Phase 4 (Deep)**: Same as Phase 3 — analyst data is already comprehensive from yfinance.

### Scoring Rubric

| Sub-signal | Weight | Positive (score 80-100) | Neutral (score 40-60) | Negative (score 0-40) |
|-----------|--------|------------------------|----------------------|----------------------|
| Rating Distribution | 40% | >60% Buy+StrongBuy | 40-60% Buy+StrongBuy | <40% Buy+StrongBuy |
| Target Price Upside | 35% | >20% upside to consensus target | 10-20% upside | <10% upside or downside |
| Recent Trend (3mo) | 25% | Net upgrades | Flat | Net downgrades |

```
Analyst Signal = RatingDist×0.40 + TargetUpside×0.35 + RecentTrend×0.25
```

### Detailed Scoring Table

**Rating Distribution**:
| % Buy+StrongBuy | Score |
|-----------------|-------|
| >80% | 100 |
| 60-80% | 80 |
| 40-60% | 55 |
| 20-40% | 30 |
| <20% | 10 |

**Target Price Upside** (consensus target vs current price):
| Upside | Score |
|--------|-------|
| >30% | 100 |
| 20-30% | 80 |
| 10-20% | 55 |
| 0-10% | 35 |
| Negative (downside) | 10 |

**Recent Trend** (net upgrades minus downgrades, last 3 months):
| Trend | Score |
|-------|-------|
| Net upgrades ≥ 3 | 100 |
| Net upgrades 1-2 | 75 |
| Flat (no changes) | 50 |
| Net downgrades 1-2 | 25 |
| Net downgrades ≥ 3 | 10 |

---

## Layer 2: Insider Signal (Weight: 40%)

### Data Sources

**Phase 3 (Quick)**:
```
SEC: get_insider_summary(identifier="{ticker}", days=180)
```

**Phase 4 (Deep)**:
```
SEC: analyze_form4_transactions(identifier="{ticker}", days=90)
SEC: analyze_insider_sentiment(identifier="{ticker}", months=6)
```

### Scoring Rubric

| Sub-signal | Weight | Positive (80-100) | Neutral (40-60) | Negative (0-40) |
|-----------|--------|-------------------|-----------------|-----------------|
| 90-day Net Activity | 40% | Net buying | No transactions | Net selling |
| Key Person Trades | 35% | CEO/CFO buying | No key person activity | CEO/CFO selling (non-plan) |
| Transaction Scale | 25% | >$1M concentrated buy | Routine small amounts | Large unplanned disposals |

```
Insider Signal = NetActivity×0.40 + KeyPerson×0.35 + Scale×0.25
```

### Detailed Scoring Table

**90-day Net Activity**:
| Activity | Score |
|----------|-------|
| Multiple insiders buying, net buy | 100 |
| Single insider buying, net buy | 80 |
| No transactions | 50 |
| Minor selling (options exercise only) | 45 |
| Net selling (small, routine) | 30 |
| Heavy net selling (multiple insiders) | 10 |

**Key Person Trades** (CEO, CFO, COO, President):
| Activity | Score |
|----------|-------|
| CEO or CFO open-market purchase | 100 |
| Director open-market purchase | 75 |
| No key person activity | 50 |
| Director routine selling | 35 |
| CEO/CFO selling (10b5-1 plan) | 30 |
| CEO/CFO selling (non-plan, large) | 5 |

**Transaction Scale**:
| Scale | Score |
|-------|-------|
| >$1M concentrated purchase | 100 |
| $100K-$1M purchase | 80 |
| <$100K or routine amounts | 50 |
| $100K-$1M sale (non-plan) | 25 |
| >$1M sale (non-plan) | 10 |

### Important Context Rules

- **10b5-1 Plans**: Pre-scheduled sales under Rule 10b5-1 are less informative. Discount selling signals by 50% if plan-based.
- **Options Exercise + Sell**: Routine for compensation management. Score as neutral (50) unless scale is extreme.
- **Cluster Buying**: Multiple insiders buying within 30 days is a much stronger signal than one person buying. Boost score by +15.
- **Post-Earnings Buying**: Insiders buying within window after earnings release carries extra conviction (they have latest data). Boost by +10.

---

## Layer 3: Institutional Signal (Weight: 30%)

### Data Sources

**Phase 3 (Quick)**:
```
WebSearch: "{ticker} institutional ownership changes {current_year}"
```

**Phase 4 (Deep)**:
```
WebSearch: "{ticker} institutional ownership 13F changes {current_quarter} {current_year}"
WebSearch: "{ticker} hedge fund positions top holders {current_year}"
SEC: get_recent_filings(identifier="{ticker}", form_type="13F-HR", days=90)  # may return limited data
```

### Scoring Rubric

| Sub-signal | Weight | Positive (80-100) | Neutral (40-60) | Negative (0-40) |
|-----------|--------|-------------------|-----------------|-----------------|
| Ownership Level | 30% | 40-80% (healthy) | 20-40% or 80-90% | <20% (ignored) or >90% (crowded) |
| Q-o-Q Change | 40% | Notable fund new positions or adds | Stable | Multiple funds reducing |
| Holder Quality | 30% | Known value/growth funds with track record | Mostly index funds | Only passive holders, no active conviction |

```
Institutional Signal = OwnershipLevel×0.30 + QoQChange×0.40 + HolderQuality×0.30
```

### Detailed Scoring Table

**Ownership Level**:
| % Institutional | Score | Interpretation |
|----------------|-------|----------------|
| 50-75% | 80 | Healthy — institutional validation without crowding |
| 40-50% or 75-85% | 60 | Acceptable |
| 20-40% | 50 | Under-institutionalized — may be under-discovered or have known issues |
| 85-95% | 40 | Crowded — limited marginal buyers |
| >95% | 20 | Extremely crowded — rebalancing risk |
| <20% | 35 | Under-owned — investigate why (could be opportunity or red flag) |

**Q-o-Q Change**:
| Change | Score |
|--------|-------|
| Notable fund initiates large new position | 100 |
| Net increase, multiple funds adding | 80 |
| Stable, minor changes | 50 |
| Net decrease, some funds trimming | 30 |
| Multiple major funds exiting | 10 |

**Holder Quality**:
| Holder Profile | Score |
|---------------|-------|
| Known value/growth investors (e.g., Berkshire, Tiger Global, Coatue) | 90 |
| Mix of active and passive holders | 60 |
| Primarily index funds / ETFs (passive only) | 35 |
| Mostly short-term / momentum traders | 25 |

---

## Red Flag Rules

**Any single red flag triggers elimination in Phase 3 or a warning label in Phase 4.**

| # | Red Flag | Trigger Condition | Action |
|---|----------|-------------------|--------|
| 1 | CEO/CFO Non-Plan Selling | CEO or CFO sells >$500K outside 10b5-1 plan in last 90 days | Phase 3: Eliminate. Phase 4: Flag as "Insider Red Flag" |
| 2 | Analyst Mass Downgrade | ≥3 analysts downgrade AND consensus target drops >20% in 60 days | Phase 3: Eliminate. Phase 4: Flag as "Analyst Red Flag" |
| 3 | Multi-Fund Exodus | ≥3 notable institutions reduce position by >25% in same quarter | Phase 3: Eliminate. Phase 4: Flag as "Institutional Red Flag" |

---

## Composite Score Interpretation

| Score Range | Label | Implication |
|------------|-------|-------------|
| 80-100 | Strong Positive | Smart money aligned with narrative thesis |
| 65-79 | Positive | Favorable signals, minor concerns |
| 50-64 | Neutral | Mixed or insufficient signals |
| 35-49 | Cautious | Negative signals present, proceed with care |
| 0-34 | Negative | Smart money contra-indicating, strong scrutiny needed |

---

## Phase 3 vs Phase 4 Comparison

| Aspect | Phase 3 (Quick) | Phase 4 (Deep) |
|--------|----------------|----------------|
| Analyst | `get_recommendations` | Same |
| Insider | `get_insider_summary(days=180)` | + `analyze_form4_transactions(days=90)` + `analyze_insider_sentiment(months=6)` |
| Institutional | 1 WebSearch | 2 WebSearch + SEC 13F filing check |
| Red flag check | Yes (eliminate) | Yes (flag + detailed context) |
| Output | Score only | Score + detailed narrative per layer |
