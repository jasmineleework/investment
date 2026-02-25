/**
 * DCF (Discounted Cash Flow) Calculator
 *
 * Usage: npx tsx calc-dcf.ts [options]
 * Options:
 *   --fcf=<amount>            Base year FCF (e.g., 5000000000 for $5B)
 *   --growth=<rates>          Comma-separated growth rates for Y1-Y5 (e.g., 0.20,0.18,0.15,0.12,0.10)
 *   --wacc=<rate>             WACC (decimal, e.g., 0.10)
 *   --terminal-growth=<rate>  Terminal growth rate (decimal, default: 0.03)
 *   --net-debt=<amount>       Net debt (positive = debt, negative = net cash)
 *   --shares=<count>          Diluted shares outstanding
 *
 * Output: JSON with projected FCFs, terminal value, enterprise value,
 *         equity value, per-share value, and sensitivity table.
 */

interface DcfInputs {
  baseFcf: number;
  growthRates: number[];
  wacc: number;
  terminalGrowth: number;
  netDebt: number;
  shares: number;
}

interface DcfOutput {
  inputs: DcfInputs;
  projectedFcf: { year: number; fcf: number; pvFcf: number }[];
  terminalValue: number;
  pvTerminalValue: number;
  enterpriseValue: number;
  equityValue: number;
  perShareValue: number;
  impliedTerminalMultiple: number;
  sensitivity: {
    waccDelta: number;
    growthDelta: number;
    perShareValue: number;
  }[];
}

function parseArgs(args: string[]): DcfInputs {
  const getFlag = (name: string, fallback?: number): number => {
    const arg = args.find((a) => a.startsWith(`--${name}=`));
    if (arg) return parseFloat(arg.split("=")[1]);
    if (fallback !== undefined) return fallback;
    console.error(`Missing required flag: --${name}`);
    process.exit(1);
  };

  const getGrowthRates = (): number[] => {
    const arg = args.find((a) => a.startsWith("--growth="));
    if (!arg) {
      console.error("Missing required flag: --growth");
      process.exit(1);
    }
    return arg.split("=")[1].split(",").map(Number);
  };

  return {
    baseFcf: getFlag("fcf"),
    growthRates: getGrowthRates(),
    wacc: getFlag("wacc"),
    terminalGrowth: getFlag("terminal-growth", 0.03),
    netDebt: getFlag("net-debt", 0),
    shares: getFlag("shares"),
  };
}

function runDcf(inputs: DcfInputs): DcfOutput {
  const { baseFcf, growthRates, wacc, terminalGrowth, netDebt, shares } =
    inputs;

  // Project FCFs
  const projectedFcf: { year: number; fcf: number; pvFcf: number }[] = [];
  let currentFcf = baseFcf;

  for (let i = 0; i < growthRates.length; i++) {
    currentFcf = currentFcf * (1 + growthRates[i]);
    const pvFcf = currentFcf / Math.pow(1 + wacc, i + 1);
    projectedFcf.push({ year: i + 1, fcf: currentFcf, pvFcf });
  }

  // Terminal value
  const lastFcf = projectedFcf[projectedFcf.length - 1].fcf;
  const terminalValue = (lastFcf * (1 + terminalGrowth)) / (wacc - terminalGrowth);
  const pvTerminalValue =
    terminalValue / Math.pow(1 + wacc, growthRates.length);

  // Enterprise & equity value
  const sumPvFcf = projectedFcf.reduce((sum, p) => sum + p.pvFcf, 0);
  const enterpriseValue = sumPvFcf + pvTerminalValue;
  const equityValue = enterpriseValue - netDebt;
  const perShareValue = equityValue / shares;

  // Implied terminal EV/EBITDA (approximate: assume EBITDA ≈ FCF × 1.3)
  const impliedTerminalMultiple = terminalValue / (lastFcf * 1.3);

  // Sensitivity table: WACC ±1%, Growth ±2%
  const sensitivity: DcfOutput["sensitivity"] = [];
  for (const wDelta of [-0.01, 0, 0.01]) {
    for (const gDelta of [-0.02, 0, 0.02]) {
      const adjWacc = wacc + wDelta;
      const adjGrowth = growthRates.map((g) => g + gDelta);
      let fcf = baseFcf;
      let sumPv = 0;
      let lastY = 0;
      for (let i = 0; i < adjGrowth.length; i++) {
        fcf = fcf * (1 + adjGrowth[i]);
        sumPv += fcf / Math.pow(1 + adjWacc, i + 1);
        lastY = fcf;
      }
      const tv = (lastY * (1 + terminalGrowth)) / (adjWacc - terminalGrowth);
      const pvTv = tv / Math.pow(1 + adjWacc, adjGrowth.length);
      const ev = sumPv + pvTv;
      const eq = ev - netDebt;
      sensitivity.push({
        waccDelta: wDelta,
        growthDelta: gDelta,
        perShareValue: eq / shares,
      });
    }
  }

  return {
    inputs,
    projectedFcf,
    terminalValue,
    pvTerminalValue,
    enterpriseValue,
    equityValue,
    perShareValue,
    impliedTerminalMultiple,
    sensitivity,
  };
}

const inputs = parseArgs(process.argv.slice(2));
const result = runDcf(inputs);
console.log(JSON.stringify(result, null, 2));
