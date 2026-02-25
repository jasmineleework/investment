/**
 * WACC Calculator
 *
 * Usage: npx tsx calc-wacc.ts <TICKER> [options]
 * Options:
 *   --risk-free=<rate>    Risk-free rate (decimal, e.g., 0.043)
 *   --beta=<beta>         Equity beta (e.g., 1.2)
 *   --erp=<rate>          Equity risk premium (decimal, default: 0.055)
 *   --debt-rate=<rate>    Pre-tax cost of debt (decimal)
 *   --tax-rate=<rate>     Effective tax rate (decimal)
 *   --debt-ratio=<ratio>  D/(D+E) ratio (decimal)
 *
 * Output: JSON with WACC components and final WACC
 */

interface WaccInputs {
  ticker: string;
  riskFreeRate: number;
  beta: number;
  equityRiskPremium: number;
  debtRate: number;
  taxRate: number;
  debtRatio: number; // D / (D + E)
}

interface WaccOutput {
  inputs: WaccInputs;
  costOfEquity: number;
  afterTaxCostOfDebt: number;
  equityWeight: number;
  debtWeight: number;
  wacc: number;
}

function parseArgs(args: string[]): WaccInputs {
  const ticker = args[0];
  if (!ticker || ticker.startsWith("--")) {
    console.error(
      "Usage: npx tsx calc-wacc.ts <TICKER> --risk-free=0.043 --beta=1.2 ..."
    );
    process.exit(1);
  }

  const getFlag = (name: string, fallback?: number): number => {
    const arg = args.find((a) => a.startsWith(`--${name}=`));
    if (arg) return parseFloat(arg.split("=")[1]);
    if (fallback !== undefined) return fallback;
    console.error(`Missing required flag: --${name}`);
    process.exit(1);
  };

  return {
    ticker,
    riskFreeRate: getFlag("risk-free"),
    beta: getFlag("beta"),
    equityRiskPremium: getFlag("erp", 0.055),
    debtRate: getFlag("debt-rate", 0.05),
    taxRate: getFlag("tax-rate", 0.21),
    debtRatio: getFlag("debt-ratio", 0.2),
  };
}

function calculateWacc(inputs: WaccInputs): WaccOutput {
  const costOfEquity =
    inputs.riskFreeRate + inputs.beta * inputs.equityRiskPremium;
  const afterTaxCostOfDebt = inputs.debtRate * (1 - inputs.taxRate);
  const equityWeight = 1 - inputs.debtRatio;
  const debtWeight = inputs.debtRatio;
  const wacc = equityWeight * costOfEquity + debtWeight * afterTaxCostOfDebt;

  return {
    inputs,
    costOfEquity,
    afterTaxCostOfDebt,
    equityWeight,
    debtWeight,
    wacc,
  };
}

const inputs = parseArgs(process.argv.slice(2));
const result = calculateWacc(inputs);
console.log(JSON.stringify(result, null, 2));
