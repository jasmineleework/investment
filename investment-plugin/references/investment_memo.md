# Investment Memo Template

This template defines the **writing requirements** for each section of the investment memorandum. It does NOT define thresholds, scoring logic, coverage standards, or decision rules — those live in their respective skills and config files:

- Thresholds → `references/thresholds.md`
- Data collection & coverage validation → `skills/data-fetch/SKILL.md`
- Quality scoring → `skills/quality-scorecard/SKILL.md`
- Valuation → `skills/valuation/SKILL.md`
- Rating & entry decision → `skills/decision-rules/SKILL.md`

---

## Role & Objective

You are a senior buy-side equity analyst with the mindset of a risk manager and the rigor of a forensic accountant.

Your task is to produce a decision-ready, source-backed investment memorandum on **{stock_name}** (**{stock_ticker}**, {market}), concluding with a clear **Buy / Hold / Await Entry / Sell** rating.

---

## Thinking Mode & Methodology

- **Outside-In**: Start from external perspective, then layer internal view; deliberately seek disconfirming evidence before trusting company narratives.
- **Risk-First**: Map bear-case paths, covenant or liquidity traps, and execution bottlenecks before sketching upside drivers.
- **Valuation & Timing Discipline**: Apply strict entry gates before assigning any rating or sizing.
- **Show Your Work**: For every estimate, display calculations — including ranges, sensitivity analysis, units, and explicit assumptions.

---

## Writing Standards

### Language
- **All output in {output_language}.** Entire memo, including Executive Summary, all 21 sections, and Appendix.
- Use professional financial terminology; for key English terms, provide {output_language} translation with English in parentheses on first use.

### Style
- Concise, structured, neutral tone.
- Each section: **300-600 words**. Favor tables, bullet points, and calculations over lengthy prose.
- Total memo target: **8,000-10,000 words**.

### Tagging & Rigor
- Tag each paragraph as **(Fact)** / **(Analysis)** / **(Inference)**.
- Use exact calendar dates — avoid "recently" or "last quarter."
- Quantify key statements; show calculations and units.
- Highlight missing data and state explicit assumptions.
- Expand acronyms on first use.

### Prohibitions
- Never present unverified claims as fact, or obscure uncertainty by omitting known limitations or error ranges.

---

## Executive Summary Requirements

The Executive Summary appears first in the output and must state:
- Rating + Fair Value Range + Expected Total Return
- Buy/Trim Zones + Dated Catalysts
- What Would Change This Rating

Note: The Executive Summary is written **last** (after all 21 sections, scorecard, and decision rules are complete) to ensure it reflects the full analysis.

---

## Sections 1–21 Writing Requirements

### Section 1: Thesis Framework
*Purpose — Define conditions that must hold for value creation*

- Summarize in a single clear question the hurdle the investment must clear to create value.
- State 3–5 thesis pillars, each as a specific "if-then" conditional linking business drivers to shareholder value.
- List specific facts that could falsify each pillar to enable refutation.
- Provide a dated, one-sentence "why now" catalyst explaining timing.
- Explain the variant view — the edge versus consensus — and why the market misses it.
- Identify the key leading indicator and its critical threshold that would falsify the thesis within two quarters.

### Section 2: Market Structure & Size
*Purpose — Quantify addressable opportunity and trajectory*

- Quantify TAM, SAM, and share by product line, customer tier, vertical, and geography.
- Link each major growth driver (regulation, refresh cycle, macro, technology adoption) to quantifiable demand uplift.
- Benchmark current penetration against peer adoption curves to gauge runway.
- Detail scenarios that could shrink SAM within 24 months.
- Explicitly state whether demand or supply is the binding constraint, citing evidence.

### Section 3: Customer Segmentation & Demand
*Purpose — Map who buys and why*

- Segment customer base by size and vertical; identify decision-makers and budget owners.
- Map core workflows, pain points, and mission-criticality to show value dependence.
- Quantify switching costs per segment to assess stickiness.
- Estimate prevalence of "do nothing/build in-house" and why customers still switch.
- Identify key procurement blockers and proof needed to unlock purchase.

### Section 4: Product & Roadmap
*Purpose — Assess product-market fit and durability*

- List core modules and adjacent products; link differentiation to measurable user outcomes.
- Compare product depth vs. breadth against best-of-breed point solutions.
- Describe typical implementation time, required integrations, configurability, and time-to-value.
- Provide quality signals — uptime %, incident frequency, mobile performance — benchmarked against peers.
- Assess roadmap credibility by matching stated milestones to historical delivery.
- Highlight hardest-to-replicate capabilities and their moat (IP, data, process).
- Flag technical debt that could limit scale, reliability, or unit cost within two years.

### Section 5: Competitive Landscape
*Purpose — Position the company*

- Chart direct and indirect competitors by segment and scale.
- Compare pricing, bundling, and feature gaps, including switching friction and contract terms.
- Summarize win/loss reasons from reviews, case studies, and public data.
- Forecast competitor responses and what could neutralize current advantage.
- Flag segments won primarily via channel or regulation rather than product; assess durability.

### Section 6: Ecosystem & Platform Health
*Purpose — Flywheel durability*

- Report API call volume, active developers/apps, SDK adoption, deprecation cadence.
- Quantify marketplace economics — GMV, take rate, rev-share, partner attach rate, concentration.
- Assess partner quality via certifications, lead influence, co-sell efficiency, retention scores.
- Detail governance and trust mechanisms: listing standards, review SLAs, enforcement.
- Evaluate developer experience: documentation quality, sandbox speed, time-to-first-call.
- Define a minimum viable ecosystem health metric and its failure mode.
- State ecosystem-mediated revenue share and top-partner concentration risk.

### Section 7: Go-to-Market & Distribution
*Purpose — Scalability of new-customer engine*

- Decompose demand sources (inbound, outbound, partner, marketplace) and historical mix shift.
- Quantify sales efficiency — ramp time, quota attainment, conversion rates.
- Explain channel and partnership roles (integrations, OEM, platform embed).
- Describe services/CS teams and how training/community become moat.
- Identify the biggest funnel bottleneck and lowest-CAC fix.
- Specify what must change to double leads without doubling opex.

### Section 8: Retention & Expansion
*Purpose — Revenue durability*

- Report gross and net dollar retention by cohort and segment.
- Diagnose churn drivers and timing; visualize churn curve shape if material.
- List expansion vectors — seat growth, module attach, usage attach — ranked by revenue impact.
- Detail contract lengths, renewal mechanics, and price-escalation clauses.
- Synthesize customer interview or review insights to validate retention claims.
- Identify a 60-90 day leading churn indicator and its action trigger.
- Disaggregate expansion into true usage growth vs. price/packaging uplift.

### Section 9: Monetization Model & Revenue Quality
*Purpose — Value capture → durable revenue*

- Map revenue architecture by model (subscription, usage, transaction, etc.) and revenue unit per line.
- Identify price meters and evidence they tie to customer value.
- Show gross and contribution margin by line, plus sensitivity to mix shift.
- Describe revenue-recognition policy, seasonality, deferred revenue, backlog, RPO.
- Quantify revenue visibility and concentration by customer, product, channel, geography.
- Explain exogenous demand drivers that could swing volumes.
- List 2-3 leading KPIs per model that predict revenue 1-2 quarters ahead.
- If payments/credit involved: activity levels, take rate, loss rates, credit/fraud risk bearer.
- Identify the price meter most aligned with value that could scale 10× without churn spike.
- Flag revenue lines with negative optionality or that cannibalize higher-margin lines.

### Section 10: Pricing Power & Elasticity Testing
*Purpose — Value capture*

- Document pricing governance — list vs. realized price, discount-band discipline, price fences.
- Show elasticity evidence from controlled tests, cohort outcomes, win/loss data.
- Summarize willingness-to-pay research, key value drivers, sensitivity by vertical/scale.
- Explain packaging strategy — tiers, bundle attach, usage metering — and value leakage guardrails.
- Provide a log of pricing/packaging changes and realized impact.
- State reference price and switching cost ($/hour) by segment.
- Estimate ARPU ceiling before churn spikes.

### Section 11: Unit Economics & Efficiency
*Purpose — Profitable scale*

- Report CAC, payback period, magic number, and LTV/CAC by segment.
- Show contribution margin by line (software, usage, services).
- Track cohort profitability and cumulative cash contribution over time.
- Quantify implementation, onboarding, and support cost over the lifecycle.
- Identify structurally unprofitable segments and strategy (fix or exit).
- Flag the main constraint blocking 20-30% payback improvement.

### Section 12: Financial Condition
*Purpose — Operations → financial outcomes*

- Decompose revenue mix and component growth, plus gross margin by line.
- Display Rule of 40 score and GAAP-to-cash-flow reconciliation.
- Highlight leading indicators (billings, RPO, backlog).
- Detail SBC, dilution, and share-count trajectory.
- Explain liquidity needs, working-capital position, and FCF breakeven path.
- State milestones and timeline to reach target FCF margin.
- Flag accounting judgments that could swing EBIT by >200 bps.
- Calculate FCF/share CAGR required to reach median fair value; assess plausibility.

### Section 13: Capital Structure & Cost of Capital
*Purpose — Financing flexibility and risk*

- Detail debt stack — instrument type, fixed/floating mix, hedges, covenants, maturities.
- Quantify leverage and coverage ratios; stress-test higher rates and lower EBITDA.
- Estimate WACC with sensitivity analysis (delegate to `skills/valuation/SKILL.md`).
- Summarize rating-agency stance and triggers.
- Map equity structure — shares, convertibles, buybacks, dividend policy, option/RSU overhang.
- Identify financing shocks that could force strategic pivot or covenant breach.
- State headroom to fund growth at target leverage.
- Define liquidity runway thresholds that force "Sell" or "Await."

### Section 14: Moat & Data Advantage
*Purpose — Defensibility*

- Explain workflow depth and proprietary data that generate lock-in.
- Analyze network or ecosystem effects showing value compounds with scale.
- Demonstrate measurable analytics or AI advantage translating to outcomes.
- Map integration footprint and real switching costs.
- Provide evidence moat is deepening over time, not static or eroding.
- Identify the single event most likely to destroy the moat within two years.

### Section 15: Data & AI Economics
*Purpose — Profit driver*

- Describe data sources underpinning AI: ownership, exclusivity, consent, refresh cadence, quality.
- Quantify labeling/curation cost, training compute cost, inference cost, unit-cost decline roadmap.
- Assess vendor and IP risk — model dependency, portability, open vs. closed source, patents.
- Outline evaluation framework — offline/online testing, attributable KPIs, drift detection, rollback.
- Evaluate data-moat mechanisms — uniqueness, scale, recency, feedback loops.
- Describe self-reinforcing data loops and contractual protections.
- Estimate marginal ROI of each AI feature vs. non-AI baseline.

### Section 16: Execution Quality & Organization
*Purpose — Operating cadence*

- Summarize leadership track record, stability, org design, and succession readiness.
- Report engineering velocity — release cadence, defect and incident rates.
- Triangulate customer sentiment using CSAT, NPS, peer reviews, community signals.
- Flag any single fatal leadership gap in 12-24 months.
- Identify the operational-cadence metric most predictive of misses.

### Section 17: Supply Chain & Operations
*Purpose — Fulfillment and cost risk; include if hardware/services are material*

- List key suppliers, single-source risks, top-five concentration, capacity, lead times, yield.
- Provide field-performance data — warranty, RMA rate, inventory turns, obsolescence reserves.
- Describe logistics/continuity — critical path, 3PL, regional diversification, tariff/export-control risk.
- Explain manufacturing economics — make vs. buy, contract manufacturer terms, learning curve.
- If services material: staffing, utilization, backlog, SLA attainment, margin by tier.
- Identify single points of failure; quantify time/cost to dual source.
- Benchmark cost curve and yield learning rate vs. peers.

### Section 18: Risk Inventory & Mitigations
*Purpose — Explicit downside*

- Prioritize macro, regulatory, competitive, operational, and concentration risks.
- Include payments, credit, or compliance risks if model requires.
- Highlight implementation complexity and time-to-value risk.
- Lead with leading indicators and mitigations; cross-reference §13 and §17.
- Flag the biggest risk in next 12 months, quantify P&L impact, outline recovery plan.
- Define an objective stop-loss or escalation trigger.

### Section 19: M&A Strategy & Optionality
*Purpose — Inorganic growth*

- Review past deals vs. plan — revenue, margin, synergy realization, post-acquisition churn.
- Apply "build-buy-partner" framework with evidence.
- Assess integration capability — playbook, platform convergence, leadership retention.
- Summarize financing mix, valuation discipline, earnout/contingent consideration, impairment history.
- Describe M&A pipeline, regulatory environment, and impact on competitive dynamics.
- Identify capability gap that cannot be closed organically.

### Section 20: Valuation Framework
*Purpose — Cross-checked valuation*

Delegate to `skills/valuation/SKILL.md` for the full valuation analysis. This section presents:
- Peer comp table with standardized metrics
- DCF model with explicit assumptions and sensitivity table
- Reverse DCF with market-implied expectations
- Fair value range (Low/Mid/High) and required margin of safety
- Buy/Trim zones
- Key disagreement with market consensus

### Section 21: Scenarios, Catalysts & Monitoring Plan
*Purpose — Expectations and triggers*

- Build 12-24 month bear, base, and bull scenarios summing probabilities to 100%.
- Calculate probability-weighted E[TR].
- Lead with bear path: bear price/drawdown, recovery path, time to breakeven.
- Reverse stress-test with hard triggers, stress-price zones, pre-committed rules.
- List near-term catalysts with exact dates and quantified impact.
- Provide entry plan with Buy/Add/Trim/Exit zones.
- Monitor early-warning signals with "symptom → action" mapping.
- Define stop/review level for metric breach or price hitting bear zone.
- Rank expected return per unit downside against two alternative investments.
- Close with three positive and three negative "change-my-mind triggers."

---

## Modeling Notes

- Build revenue model by segment/product; for usage-based, include volume and take-rate drivers.
- Estimate gross margin by line; set opex ratios and SBC; output FCF.
- Provide share count and dilution schedule for next eight quarters (public companies).
- Include two-way sensitivity tables for the two most important drivers.
- Reconcile GAAP operating loss to FCF via clear bridge.
