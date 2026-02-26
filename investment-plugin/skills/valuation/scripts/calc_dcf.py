#!/usr/bin/env python3
"""
DCF (Discounted Cash Flow) Calculator

Usage: python3 calc_dcf.py [options]
Options:
  --fcf=<amount>            Base year FCF (e.g., 5000000000 for $5B)
  --growth=<rates>          Comma-separated growth rates for Y1-Y5 (e.g., 0.20,0.18,0.15,0.12,0.10)
  --wacc=<rate>             WACC (decimal, e.g., 0.10)
  --terminal-growth=<rate>  Terminal growth rate (decimal, default: 0.03)
  --net-debt=<amount>       Net debt (positive = debt, negative = net cash)
  --shares=<count>          Diluted shares outstanding

Output: JSON with projected FCFs, terminal value, enterprise value,
        equity value, per-share value, and sensitivity table.
"""

import argparse
import json
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="DCF Calculator")
    parser.add_argument("--fcf", type=float, required=True, help="Base year FCF")
    parser.add_argument("--growth", type=str, required=True, help="Comma-separated growth rates")
    parser.add_argument("--wacc", type=float, required=True, help="WACC (decimal)")
    parser.add_argument("--terminal-growth", type=float, default=0.03, help="Terminal growth rate")
    parser.add_argument("--net-debt", type=float, default=0, help="Net debt")
    parser.add_argument("--shares", type=float, required=True, help="Diluted shares outstanding")
    args = parser.parse_args()
    args.growth_rates = [float(x) for x in args.growth.split(",")]
    return args


def run_dcf(base_fcf, growth_rates, wacc, terminal_growth, net_debt, shares):
    # Project FCFs
    projected_fcf = []
    current_fcf = base_fcf
    for i, g in enumerate(growth_rates):
        current_fcf = current_fcf * (1 + g)
        pv_fcf = current_fcf / ((1 + wacc) ** (i + 1))
        projected_fcf.append({"year": i + 1, "fcf": current_fcf, "pvFcf": pv_fcf})

    # Terminal value
    last_fcf = projected_fcf[-1]["fcf"]
    terminal_value = (last_fcf * (1 + terminal_growth)) / (wacc - terminal_growth)
    pv_terminal_value = terminal_value / ((1 + wacc) ** len(growth_rates))

    # Enterprise & equity value
    sum_pv_fcf = sum(p["pvFcf"] for p in projected_fcf)
    enterprise_value = sum_pv_fcf + pv_terminal_value
    equity_value = enterprise_value - net_debt
    per_share_value = equity_value / shares

    # Implied terminal EV/EBITDA (approximate: assume EBITDA ~ FCF x 1.3)
    implied_terminal_multiple = terminal_value / (last_fcf * 1.3)

    # Sensitivity table: WACC +/-1%, Growth +/-2%
    sensitivity = []
    for w_delta in [-0.01, 0, 0.01]:
        for g_delta in [-0.02, 0, 0.02]:
            adj_wacc = wacc + w_delta
            adj_growth = [g + g_delta for g in growth_rates]
            fcf = base_fcf
            sum_pv = 0
            last_y = 0
            for i, g in enumerate(adj_growth):
                fcf = fcf * (1 + g)
                sum_pv += fcf / ((1 + adj_wacc) ** (i + 1))
                last_y = fcf
            tv = (last_y * (1 + terminal_growth)) / (adj_wacc - terminal_growth)
            pv_tv = tv / ((1 + adj_wacc) ** len(adj_growth))
            ev = sum_pv + pv_tv
            eq = ev - net_debt
            sensitivity.append({
                "waccDelta": w_delta,
                "growthDelta": g_delta,
                "perShareValue": eq / shares,
            })

    return {
        "inputs": {
            "baseFcf": base_fcf,
            "growthRates": growth_rates,
            "wacc": wacc,
            "terminalGrowth": terminal_growth,
            "netDebt": net_debt,
            "shares": shares,
        },
        "projectedFcf": projected_fcf,
        "terminalValue": terminal_value,
        "pvTerminalValue": pv_terminal_value,
        "enterpriseValue": enterprise_value,
        "equityValue": equity_value,
        "perShareValue": per_share_value,
        "impliedTerminalMultiple": implied_terminal_multiple,
        "sensitivity": sensitivity,
    }


def main():
    args = parse_args()
    result = run_dcf(
        base_fcf=args.fcf,
        growth_rates=args.growth_rates,
        wacc=args.wacc,
        terminal_growth=args.terminal_growth,
        net_debt=args.net_debt,
        shares=args.shares,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
