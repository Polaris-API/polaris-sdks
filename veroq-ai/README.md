# @veroq/ai

> Verified AI. One function call.

> **New:** VeroQ 2.0 adds Verified Swarm (multi-agent pipelines), Agent Runtime (finance/legal/research/compliance verticals), and secure external MCP integration. Available via the [MCP server](https://www.npmjs.com/package/veroq-mcp) and [SDKs](https://veroq.ai/docs).

VEROQ tools for the [Vercel AI SDK](https://sdk.vercel.ai). Drop verified financial intelligence into any AI SDK agent with one line.

## Install

```bash
npm install @veroq/ai ai zod
```

## Quick Start

The fastest way -- `veroqTools()` gives your agent access to all 53 tools:

```typescript
import { generateText } from "ai";
import { anthropic } from "@ai-sdk/anthropic";
import { veroqTools } from "@veroq/ai";

const result = await generateText({
  model: anthropic("claude-sonnet-4-20250514"),
  tools: veroqTools(),
  prompt: "How is NVDA doing today?",
});
```

Or import just the tools you need:

```typescript
import { veroqAsk, veroqVerify } from "@veroq/ai";

const result = await generateText({
  model: anthropic("claude-sonnet-4-20250514"),
  tools: {
    ask: veroqAsk({ apiKey: "your-api-key" }),
    verify: veroqVerify({ apiKey: "your-api-key" }),
  },
  prompt: "Fact-check: NVIDIA revenue grew 200% last quarter",
});
```

Set the `VEROQ_API_KEY` environment variable to skip passing `apiKey` everywhere.

## Tools

### Primary

| Export | Description |
|--------|------------|
| `veroqAsk()` | Ask any question about markets, companies, or economics |
| `veroqVerify()` | Fact-check a claim against the intelligence corpus |

### Search & Discovery

| Export | Description |
|--------|------------|
| `veroqSearch()` | Search verified news briefs with confidence scores |
| `veroqFeed()` | Get latest intelligence feed |
| `veroqBrief()` | Get a specific brief by ID |
| `veroqExtract()` | Extract article content from URLs |
| `veroqEntities()` | Look up entity coverage |
| `veroqTrending()` | Get trending entities |
| `veroqCompare()` | Compare outlet coverage of a story |
| `veroqResearch()` | Deep multi-source research (5 credits) |
| `veroqTimeline()` | Story evolution timeline for living briefs |
| `veroqForecast()` | Forward-looking topic forecasts |
| `veroqContradictions()` | Find contradictions across intelligence |
| `veroqEvents()` | Notable events from intelligence briefs |
| `veroqWebSearch()` | Web search with trust scoring |
| `veroqCrawl()` | Extract structured content from URLs |

### Market Data

| Export | Description |
|--------|------------|
| `veroqTickerResolve()` | Resolve ticker symbols |
| `veroqTicker()` | Get ticker price data |
| `veroqTickerHistory()` | Historical ticker data |
| `veroqTickerScore()` | Composite trading signal score |
| `veroqFull()` | Full ticker profile |
| `veroqSectors()` | Sector overview with sentiment |
| `veroqPortfolioFeed()` | Portfolio-aware news feed |
| `veroqEventsCalendar()` | Events calendar |
| `veroqCandles()` | OHLCV candlestick data |
| `veroqTechnicals()` | Technical indicators and signals |
| `veroqMarketMovers()` | Top gainers, losers, most active |
| `veroqEconomy()` | Macroeconomic indicators |
| `veroqForex()` | Foreign exchange rates |
| `veroqCommodities()` | Commodity prices |
| `veroqCrypto()` | Cryptocurrency data |
| `veroqCryptoDefi()` | DeFi TVL and protocol data |
| `veroqBacktest()` | Backtesting with equity curves |
| `veroqCorrelation()` | Correlation matrix analysis |
| `veroqScreener()` | Multi-criteria stock/crypto screener |
| `veroqNewsImpact()` | News impact scoring |
| `veroqCompetitors()` | Competitor intelligence |

### Fundamentals & Social

| Export | Description |
|--------|------------|
| `veroqInsider()` | Insider trading activity |
| `veroqFilings()` | SEC filings |
| `veroqAnalysts()` | Analyst ratings and targets |
| `veroqCongress()` | Congressional trading activity |
| `veroqInstitutions()` | Institutional ownership |
| `veroqSocialSentiment()` | Social media sentiment |
| `veroqSocialTrending()` | Social media trending topics |

### Other

| Export | Description |
|--------|------------|
| `veroqIpoCalendar()` | IPO calendar from SEC filings |
| `veroqTickerNews()` | Ticker-specific news |
| `veroqTickerAnalysis()` | Comprehensive ticker analysis |
| `veroqSearchSuggest()` | Search autocomplete |
| `veroqDefiProtocol()` | Detailed DeFi protocol data |
| `veroqEconomyIndicator()` | Specific economic indicators |
| `veroqGenerateReport()` | AI-powered research reports |
| `veroqGetReport()` | Retrieve generated reports |
| `veroqRunAgent()` | Run pre-built AI agents |

### Convenience

| Export | Description |
|--------|------------|
| `veroqTools()` | Returns all tools in a single object for `generateText({ tools })` |

Each function accepts an optional `{ apiKey }` config and returns an AI SDK `tool()`.

## Get an API Key

Sign up at [veroq.ai/settings](https://veroq.ai/settings).

## License

MIT
