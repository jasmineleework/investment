/**
 * Yahoo Finance Data Fetcher
 *
 * Usage: npx tsx yahoo-fetch.ts <TICKER>
 * Output: JSON to stdout with quote, financials, balance sheet, cash flow,
 *         historical prices, and analyst ratings.
 *
 * Dependencies: yahoo-finance2
 */

import yahooFinance from "yahoo-finance2";

const ticker = process.argv[2];

if (!ticker) {
  console.error("Usage: npx tsx yahoo-fetch.ts <TICKER>");
  process.exit(1);
}

interface FetchResult {
  ticker: string;
  fetchDate: string;
  quote: Record<string, unknown> | null;
  financials: Record<string, unknown> | null;
  balanceSheet: Record<string, unknown> | null;
  cashFlow: Record<string, unknown> | null;
  historicalPrices: unknown[] | null;
  analystRatings: Record<string, unknown> | null;
  errors: string[];
}

async function fetchAll(symbol: string): Promise<FetchResult> {
  const result: FetchResult = {
    ticker: symbol,
    fetchDate: new Date().toISOString().split("T")[0],
    quote: null,
    financials: null,
    balanceSheet: null,
    cashFlow: null,
    historicalPrices: null,
    analystRatings: null,
    errors: [],
  };

  // Quote summary
  try {
    const quote = await yahooFinance.quoteSummary(symbol, {
      modules: [
        "price",
        "summaryDetail",
        "defaultKeyStatistics",
        "financialData",
        "earningsTrend",
        "recommendationTrend",
      ],
    });
    result.quote = {
      price: quote.price?.regularMarketPrice,
      marketCap: quote.price?.marketCap,
      currency: quote.price?.currency,
      exchange: quote.price?.exchangeName,
      name: quote.price?.longName || quote.price?.shortName,
      pe: quote.summaryDetail?.trailingPE,
      forwardPe: quote.summaryDetail?.forwardPE,
      pb: quote.defaultKeyStatistics?.priceToBook,
      ps: quote.summaryDetail?.priceToSalesTrailing12Months,
      evToEbitda: quote.defaultKeyStatistics?.enterpriseToEbitda,
      evToRevenue: quote.defaultKeyStatistics?.enterpriseToRevenue,
      dividendYield: quote.summaryDetail?.dividendYield,
      beta: quote.defaultKeyStatistics?.beta,
      fiftyTwoWeekHigh: quote.summaryDetail?.fiftyTwoWeekHigh,
      fiftyTwoWeekLow: quote.summaryDetail?.fiftyTwoWeekLow,
      avgVolume: quote.summaryDetail?.averageVolume,
      sharesOutstanding: quote.defaultKeyStatistics?.sharesOutstanding,
      floatShares: quote.defaultKeyStatistics?.floatShares,
      shortRatio: quote.defaultKeyStatistics?.shortRatio,
      targetMeanPrice: quote.financialData?.targetMeanPrice,
      targetHighPrice: quote.financialData?.targetHighPrice,
      targetLowPrice: quote.financialData?.targetLowPrice,
      numberOfAnalystOpinions:
        quote.financialData?.numberOfAnalystOpinions,
      recommendationKey: quote.financialData?.recommendationKey,
      grossMargin: quote.financialData?.grossMargins,
      operatingMargin: quote.financialData?.operatingMargins,
      profitMargin: quote.financialData?.profitMargins,
      returnOnEquity: quote.financialData?.returnOnEquity,
      returnOnAssets: quote.financialData?.returnOnAssets,
      revenueGrowth: quote.financialData?.revenueGrowth,
      earningsGrowth: quote.financialData?.earningsGrowth,
      totalDebt: quote.financialData?.totalDebt,
      totalCash: quote.financialData?.totalCash,
      debtToEquity: quote.financialData?.debtToEquity,
      currentRatio: quote.financialData?.currentRatio,
      freeCashflow: quote.financialData?.freeCashflow,
      operatingCashflow: quote.financialData?.operatingCashflow,
    };
  } catch (e) {
    result.errors.push(`quote: ${(e as Error).message}`);
  }

  // Income statement (annual + quarterly)
  try {
    const annual = await yahooFinance.fundamentalsTimeSeries(symbol, {
      period1: "2022-01-01",
      type: "annual",
      module: "financials",
    });
    const quarterly = await yahooFinance.fundamentalsTimeSeries(symbol, {
      period1: "2024-01-01",
      type: "quarterly",
      module: "financials",
    });
    result.financials = { annual, quarterly };
  } catch (e) {
    result.errors.push(`financials: ${(e as Error).message}`);
  }

  // Balance sheet
  try {
    const annual = await yahooFinance.fundamentalsTimeSeries(symbol, {
      period1: "2022-01-01",
      type: "annual",
      module: "balance-sheet",
    });
    result.balanceSheet = { annual };
  } catch (e) {
    result.errors.push(`balanceSheet: ${(e as Error).message}`);
  }

  // Cash flow
  try {
    const annual = await yahooFinance.fundamentalsTimeSeries(symbol, {
      period1: "2022-01-01",
      type: "annual",
      module: "cash-flow",
    });
    result.cashFlow = { annual };
  } catch (e) {
    result.errors.push(`cashFlow: ${(e as Error).message}`);
  }

  // Historical prices (2 years)
  try {
    const twoYearsAgo = new Date();
    twoYearsAgo.setFullYear(twoYearsAgo.getFullYear() - 2);
    const history = await yahooFinance.chart(symbol, {
      period1: twoYearsAgo.toISOString().split("T")[0],
      interval: "1wk",
    });
    result.historicalPrices = history.quotes?.map((q) => ({
      date: q.date,
      open: q.open,
      high: q.high,
      low: q.low,
      close: q.close,
      volume: q.volume,
    })) || [];
  } catch (e) {
    result.errors.push(`historicalPrices: ${(e as Error).message}`);
  }

  // Analyst ratings (from recommendationTrend)
  try {
    const rec = await yahooFinance.quoteSummary(symbol, {
      modules: ["recommendationTrend"],
    });
    result.analystRatings = {
      trend: rec.recommendationTrend?.trend,
    };
  } catch (e) {
    result.errors.push(`analystRatings: ${(e as Error).message}`);
  }

  return result;
}

fetchAll(ticker)
  .then((data) => {
    console.log(JSON.stringify(data, null, 2));
  })
  .catch((err) => {
    console.error(`Fatal error: ${err.message}`);
    process.exit(1);
  });
