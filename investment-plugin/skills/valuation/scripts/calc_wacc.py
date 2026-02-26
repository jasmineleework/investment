#!/usr/bin/env python3
"""
WACC Calculator

Usage: python3 calc_wacc.py <TICKER> [options]
Options:
  --risk-free=<rate>    Risk-free rate (decimal, e.g., 0.043)
  --beta=<beta>         Equity beta (e.g., 1.2)
  --erp=<rate>          Equity risk premium (decimal, default: 0.055)
  --debt-rate=<rate>    Pre-tax cost of debt (decimal, default: 0.05)
  --tax-rate=<rate>     Effective tax rate (decimal, default: 0.21)
  --debt-ratio=<ratio>  D/(D+E) ratio (decimal, default: 0.2)

Output: JSON with WACC components and final WACC
"""

import argparse
import json
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="WACC Calculator")
    parser.add_argument("ticker", type=str, help="Stock ticker symbol")
    parser.add_argument("--risk-free", type=float, required=True, help="Risk-free rate (decimal)")
    parser.add_argument("--beta", type=float, required=True, help="Equity beta")
    parser.add_argument("--erp", type=float, default=0.055, help="Equity risk premium")
    parser.add_argument("--debt-rate", type=float, default=0.05, help="Pre-tax cost of debt")
    parser.add_argument("--tax-rate", type=float, default=0.21, help="Effective tax rate")
    parser.add_argument("--debt-ratio", type=float, default=0.2, help="D/(D+E) ratio")
    return parser.parse_args()


def calculate_wacc(ticker, risk_free, beta, erp, debt_rate, tax_rate, debt_ratio):
    cost_of_equity = risk_free + beta * erp
    after_tax_cost_of_debt = debt_rate * (1 - tax_rate)
    equity_weight = 1 - debt_ratio
    debt_weight = debt_ratio
    wacc = equity_weight * cost_of_equity + debt_weight * after_tax_cost_of_debt

    return {
        "inputs": {
            "ticker": ticker,
            "riskFreeRate": risk_free,
            "beta": beta,
            "equityRiskPremium": erp,
            "debtRate": debt_rate,
            "taxRate": tax_rate,
            "debtRatio": debt_ratio,
        },
        "costOfEquity": cost_of_equity,
        "afterTaxCostOfDebt": after_tax_cost_of_debt,
        "equityWeight": equity_weight,
        "debtWeight": debt_weight,
        "wacc": wacc,
    }


def main():
    args = parse_args()
    result = calculate_wacc(
        ticker=args.ticker.upper(),
        risk_free=args.risk_free,
        beta=args.beta,
        erp=args.erp,
        debt_rate=args.debt_rate,
        tax_rate=args.tax_rate,
        debt_ratio=args.debt_ratio,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
