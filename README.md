# VEROQ SDKs + CLI

**The truth protocol for agentic AI. Verified intelligence for agents that can't afford to be wrong.**

Official SDKs, CLI, and framework integrations for [VEROQ](https://veroq.ai) — 1,061+ tickers, 20 technical indicators, NLP screener, trade signals, and verified intelligence.

## Fastest Way to Start

```bash
npm install -g @veroq/cli
export VEROQ_API_KEY=vq_live_xxx   # Free: veroq.ai/pricing

veroq ask "What's happening with NVDA?"
veroq screen "oversold semiconductors"
veroq signal MSFT
veroq compare AAPL MSFT GOOGL
```

Or use the SDKs:

```python
from veroq import Agent
agent = Agent()
result = agent.ask("What's happening with NVDA?")
print(result.summary)        # Markdown summary with bottom line
print(result.trade_signal)   # { action: "hold", score: 50, factors: [...] }
```

```typescript
import { Agent } from 'polaris-news-api';
const agent = new Agent();
const result = await agent.ask("What's happening with NVDA?");
```

[Try it live](https://veroq.ai) — no signup required.

## Packages

| Package | Type | Install |
|---------|------|---------|
| [`@veroq/cli`](./veroq-cli/) | CLI | `npm install -g @veroq/cli` |
| [`veroq`](./veroq-python/) | Python SDK | `pip install veroq` |
| [`polaris-news-api`](./typescript/) | TypeScript SDK | `npm install polaris-news-api` |
| [`@veroq/ai`](./veroq-ai/) | Vercel AI SDK | `npm install @veroq/ai` |
| [`crewai-veroq`](./crewai-veroq/) | CrewAI | `pip install crewai-veroq` |
| [`langchain-veroq`](./langchain-veroq/) | LangChain | `pip install langchain-veroq` |
| [`n8n-nodes-veroq`](./n8n-veroq/) | n8n | `npm install n8n-nodes-veroq` |
| [`veroq-mcp`](./veroq-mcp/) | MCP Server | `npm install -g veroq-mcp` |

## CLI Commands

| Command | Description |
|---------|-------------|
| `veroq ask <question>` | Natural language query — returns structured intelligence |
| `veroq price <TICKER>` | Live price |
| `veroq screen <criteria>` | NLP stock screener |
| `veroq compare <T1> <T2>` | Side-by-side comparison |
| `veroq signal <TICKER>` | Trade readiness score (0-100) |
| `veroq earnings <TICKER>` | Next earnings + estimates |
| `veroq insider <TICKER>` | Insider transactions |
| `veroq technicals <TICKER>` | RSI, MACD, SMA, signals |
| `veroq full <TICKER>` | 9 data sources in one call |
| `veroq market` | Market overview + VIX |
| `veroq news <query>` | Search intelligence briefs |
| `veroq verify <claim>` | Fact-check against brief corpus |

JSON by default (agent-first). Use `--human` for formatted output.

## Examples

See [`examples/`](./examples/) for working integration examples:
- `trading-bot.py` — Automated trading signals
- `research-agent.ts` — Multi-step research pipeline
- `crypto-monitor.py` — Real-time crypto tracking

## What You Get

- **1,061+ tickers** — equities, crypto, ETFs, commodities, indices (auto-discovery for any ticker)
- **20 technical indicators** + composite signal summary
- **Trade readiness signal** — 0-100 score combining RSI, sentiment, VIX, technicals, earnings proximity
- **NLP screener** — "oversold semiconductors" → structured filters → results
- **Insider trades, SEC filings, analyst ratings, congressional trades**
- **Verified intelligence briefs** — bias-scored, confidence-rated
- **Real-time subscriptions** via SSE
- **300+ API endpoints** — all structured JSON

## Auth

```bash
export VEROQ_API_KEY=vq_live_xxx
```

Get a free key (1,000 credits/month): [veroq.ai/pricing](https://veroq.ai/pricing)

## Links

- [Interactive Demo](https://veroq.ai)
- [API Documentation](https://veroq.ai/docs)
- [API Reference](https://veroq.ai/api-reference)
- [TradingAgents-Pro](https://github.com/Polaris-API/TradingAgents-Pro) — 18-agent trading framework powered by VEROQ

## License

MIT
