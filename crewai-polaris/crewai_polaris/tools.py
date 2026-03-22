from typing import Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from polaris_news import PolarisClient


class SearchInput(BaseModel):
    query: str = Field(description="Search query for verified intelligence")
    category: Optional[str] = Field(default=None, description="Category slug (e.g. ai_ml, markets, crypto)")
    depth: Optional[str] = Field(default=None, description="Speed tier: fast, standard, or deep")


class PolarisSearchTool(BaseTool):
    name: str = "polaris_search"
    description: str = "Search verified intelligence across 18 verticals. Returns briefs with confidence scores and bias ratings."
    args_schema: Type[BaseModel] = SearchInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, query: str, category: str = None, depth: str = None) -> str:
        client = PolarisClient(api_key=self.api_key)
        result = client.search(query, category=category, depth=depth)
        if not result.briefs:
            return "No results found for '{}'.".format(query)
        lines = []
        for b in result.briefs[:5]:
            lines.append("- {} (confidence: {}, bias: {})".format(
                b.headline,
                b.confidence or "N/A",
                b.bias_score or "N/A",
            ))
            if b.summary:
                lines.append("  {}".format(b.summary[:200]))
        return "\n".join(lines)


class FeedInput(BaseModel):
    category: Optional[str] = Field(default=None, description="Category slug to filter by")
    limit: Optional[int] = Field(default=None, description="Max number of briefs to return")
    include_sources: Optional[str] = Field(default=None, description="Comma-separated source domains to include")


class PolarisFeedTool(BaseTool):
    name: str = "polaris_feed"
    description: str = "Get latest verified intelligence briefs, optionally filtered by category or source domain."
    args_schema: Type[BaseModel] = FeedInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, category: str = None, limit: int = None, include_sources: str = None) -> str:
        client = PolarisClient(api_key=self.api_key)
        result = client.feed(category=category, limit=limit, include_sources=include_sources)
        if not result.briefs:
            return "No briefs found."
        lines = []
        for b in result.briefs[:10]:
            lines.append("- [{}] {} (confidence: {})".format(b.category or "general", b.headline, b.confidence or "N/A"))
            if b.summary:
                lines.append("  {}".format(b.summary[:200]))
        return "\n".join(lines)


class EntityInput(BaseModel):
    name: str = Field(description="Entity name to look up (person, company, technology)")


class PolarisEntityTool(BaseTool):
    name: str = "polaris_entities"
    description: str = "Look up entities (companies, people, technologies) mentioned in verified intelligence coverage."
    args_schema: Type[BaseModel] = EntityInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, name: str) -> str:
        client = PolarisClient(api_key=self.api_key)
        briefs = client.entity_briefs(name)
        if not briefs:
            return "No coverage found for entity '{}'.".format(name)
        lines = ["Coverage for '{}':".format(name)]
        for b in briefs[:5]:
            lines.append("- {} ({})".format(b.headline, b.published_at or ""))
        return "\n".join(lines)


class BriefInput(BaseModel):
    brief_id: str = Field(description="Brief ID to retrieve")
    include_full_text: Optional[bool] = Field(default=None, description="Include full source article text")


class PolarisBriefTool(BaseTool):
    name: str = "polaris_brief"
    description: str = "Get a specific verified intelligence brief by ID with full analysis, sources, and counter-arguments."
    args_schema: Type[BaseModel] = BriefInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, brief_id: str, include_full_text: bool = None) -> str:
        client = PolarisClient(api_key=self.api_key)
        b = client.brief(brief_id, include_full_text=include_full_text)
        parts = [b.headline or "Untitled"]
        if b.summary:
            parts.append("Summary: {}".format(b.summary))
        if b.body:
            parts.append("Body: {}".format(b.body[:500]))
        if b.counter_argument:
            parts.append("Counter-argument: {}".format(b.counter_argument))
        parts.append("Confidence: {} | Bias: {} | Sentiment: {}".format(
            b.confidence or "N/A", b.bias_score or "N/A", b.sentiment or "N/A"))
        if b.sources:
            parts.append("Sources: {}".format(", ".join(s.name for s in b.sources)))
        return "\n".join(parts)


class ExtractInput(BaseModel):
    urls: str = Field(description="Comma-separated URLs to extract article content from")


class PolarisExtractTool(BaseTool):
    name: str = "polaris_extract"
    description: str = "Extract clean article content from URLs. Returns structured text with metadata."
    args_schema: Type[BaseModel] = ExtractInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, urls: str) -> str:
        url_list = [u.strip() for u in urls.split(",") if u.strip()]
        if not url_list:
            return "No URLs provided."
        client = PolarisClient(api_key=self.api_key)
        result = client.extract(url_list[:5])
        lines = []
        for r in result.results:
            if r.success:
                lines.append("--- {} ---".format(r.title or r.url))
                lines.append("Domain: {} | Words: {} | Language: {}".format(r.domain or "N/A", r.word_count or 0, r.language or "N/A"))
                if r.text:
                    lines.append(r.text[:1000])
            else:
                lines.append("Failed: {} — {}".format(r.url, r.error or "Unknown error"))
        lines.append("Credits used: {}".format(result.credits_used))
        return "\n".join(lines)


class ResearchInput(BaseModel):
    query: str = Field(description="Research query to investigate across intelligence briefs")
    category: Optional[str] = Field(default=None, description="Category slug to filter briefs (e.g. ai_ml, policy, markets)")
    max_sources: Optional[int] = Field(default=None, description="Maximum briefs to analyze (1-50, default: 20)")


class PolarisResearchTool(BaseTool):
    name: str = "polaris_research"
    description: str = "Deep research across verified intelligence briefs. Expands a query into sub-queries, searches in parallel, aggregates entities, and synthesizes a comprehensive report with key findings and information gaps. Requires Growth plan. Costs 5 API credits."
    args_schema: Type[BaseModel] = ResearchInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, query: str, category: str = None, max_sources: int = None) -> str:
        client = PolarisClient(api_key=self.api_key)
        result = client.research(query, category=category, max_sources=max_sources)
        lines = []
        if result.report:
            summary = result.report.get("summary", "")
            if summary:
                lines.append("Summary: {}".format(summary[:500]))
            findings = result.report.get("key_findings", [])
            if findings:
                lines.append("Key Findings:")
                for f in findings[:10]:
                    lines.append("- {}".format(f))
            gaps = result.report.get("information_gaps", [])
            if gaps:
                lines.append("Information Gaps:")
                for g in gaps[:5]:
                    lines.append("- {}".format(g))
        if result.entity_map:
            lines.append("Top Entities:")
            for e in result.entity_map[:5]:
                lines.append("- {} ({}, {} mentions)".format(e.name, e.type or "N/A", e.mentions or 0))
        if result.metadata:
            lines.append("Analyzed {} briefs from {} sources in {}ms".format(
                result.metadata.briefs_analyzed, result.metadata.unique_sources, result.metadata.processing_time_ms or 0))
        if not lines:
            return "No results found for research query '{}'.".format(query)
        return "\n".join(lines)


class VerifyInput(BaseModel):
    claim: str = Field(description="The claim to fact-check (10-1000 characters)")
    context: Optional[str] = Field(default=None, description="Category to narrow the search (e.g. tech, policy, markets)")


class PolarisVerifyTool(BaseTool):
    name: str = "polaris_verify"
    description: str = "Fact-check a claim against the Polaris brief corpus. Returns a verdict (supported/contradicted/partially_supported/unverifiable) with confidence, evidence, and nuances. Costs 3 API credits."
    args_schema: Type[BaseModel] = VerifyInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, claim: str, context: str = None) -> str:
        client = PolarisClient(api_key=self.api_key)
        result = client.verify(claim, context=context)
        lines = ["Verdict: {} (confidence: {:.0%})".format(result.verdict, result.confidence)]
        if result.summary:
            lines.append("Summary: {}".format(result.summary))
        if result.supporting_briefs:
            lines.append("Supporting Evidence:")
            for b in result.supporting_briefs:
                lines.append("- {} ({})".format(b.headline, b.id))
        if result.contradicting_briefs:
            lines.append("Contradicting Evidence:")
            for b in result.contradicting_briefs:
                lines.append("- {} ({})".format(b.headline, b.id))
        if result.nuances:
            lines.append("Nuances: {}".format(result.nuances))
        lines.append("Sources analyzed: {} | Briefs matched: {} | Credits: {}".format(
            result.sources_analyzed, result.briefs_matched, result.credits_used))
        return "\n".join(lines)


class CompareInput(BaseModel):
    topic: str = Field(description="Topic to compare coverage across outlets")


class PolarisCompareTool(BaseTool):
    name: str = "polaris_compare"
    description: str = "Compare how different outlets covered the same story. Shows framing, bias, and what each side emphasizes or omits."
    args_schema: Type[BaseModel] = CompareInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, topic: str) -> str:
        client = PolarisClient(api_key=self.api_key)
        search_result = client.search(topic, per_page=1)
        if not search_result.briefs:
            return "No coverage found for topic '{}'.".format(topic)
        brief_id = search_result.briefs[0].id
        try:
            comparison = client.compare_sources(brief_id)
        except Exception as e:
            return "Could not compare sources: {}".format(str(e))
        lines = ["Topic: {}".format(comparison.topic or topic)]
        if comparison.source_analyses:
            for sa in comparison.source_analyses:
                lines.append("- {} ({})".format(sa.outlet or "Unknown", sa.political_lean or "N/A"))
                if sa.framing:
                    lines.append("  {}".format(sa.framing[:200]))
        if comparison.polaris_analysis:
            summary = comparison.polaris_analysis.get("summary", "") if isinstance(comparison.polaris_analysis, dict) else str(comparison.polaris_analysis)
            lines.append("Synthesis: {}".format(summary[:500]))
        return "\n".join(lines)


class TrendingInput(BaseModel):
    limit: Optional[int] = Field(default=None, description="Max number of trending entities to return")


class PolarisTrendingTool(BaseTool):
    name: str = "polaris_trending"
    description: str = "Get trending entities across the intelligence network — the people, companies, and topics generating the most coverage right now."
    args_schema: Type[BaseModel] = TrendingInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, limit: int = None) -> str:
        client = PolarisClient(api_key=self.api_key)
        entities = client.trending_entities(limit=limit)
        if not entities:
            return "No trending entities found."
        lines = ["Trending entities:"]
        for e in entities:
            lines.append("- {} ({}, {} mentions)".format(
                e.name, e.type or "N/A", e.mention_count or 0))
        return "\n".join(lines)


# ── Market Data Tools ──


class CandlesInput(BaseModel):
    symbol: str = Field(description="Ticker symbol (e.g. 'AAPL', 'NVDA')")
    interval: Optional[str] = Field(default=None, description="Candle interval: 1d, 1wk, or 1mo (default 1d)")
    range: Optional[str] = Field(default=None, description="Date range: 1mo, 3mo, 6mo, 1y, 2y, 5y (default 6mo)")


class PolarisCandlesTool(BaseTool):
    name: str = "polaris_candles"
    description: str = "Get OHLCV candlestick data for a ticker symbol. Returns date, open, high, low, close, and volume for each period."
    args_schema: Type[BaseModel] = CandlesInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, symbol: str, interval: str = None, range: str = None) -> str:
        client = PolarisClient(api_key=self.api_key)
        result = client.candles(symbol, interval=interval or '1d', range=range or '6mo')
        candles = result.get("candles", [])
        if not candles:
            return "No candle data found for '{}'.".format(symbol)
        lines = ["{} — {} candles ({}, {})".format(
            result.get("ticker", symbol),
            result.get("candle_count", len(candles)),
            result.get("interval", "1d"),
            result.get("range", "6mo"),
        )]
        for c in candles[-10:]:
            lines.append("  {} O={} H={} L={} C={} V={}".format(
                c.get("date", "?"),
                c.get("open", "?"),
                c.get("high", "?"),
                c.get("low", "?"),
                c.get("close", "?"),
                c.get("volume", "?"),
            ))
        if len(candles) > 10:
            lines.insert(1, "(showing last 10 of {})".format(len(candles)))
        return "\n".join(lines)


class TechnicalsInput(BaseModel):
    symbol: str = Field(description="Ticker symbol (e.g. 'NVDA')")
    range: Optional[str] = Field(default=None, description="Date range for indicator calculation: 1mo, 3mo, 6mo, 1y, 2y, 5y (default 6mo)")


class PolarisTechnicalsTool(BaseTool):
    name: str = "polaris_technicals"
    description: str = "Get all technical indicators and a signal summary for a ticker. Includes SMA, EMA, RSI, MACD, Bollinger Bands, ATR, Stochastic, ADX, OBV, VWAP with an overall buy/sell/neutral verdict."
    args_schema: Type[BaseModel] = TechnicalsInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, symbol: str, range: str = None) -> str:
        client = PolarisClient(api_key=self.api_key)
        result = client.technicals(symbol, range=range or '6mo')
        ticker = result.get("ticker", symbol)
        summary = result.get("summary", {})
        indicators = result.get("indicators", {})
        lines = ["{} — Technical Analysis".format(ticker)]
        if summary:
            lines.append("Signal: {} | Buy: {} | Sell: {} | Neutral: {}".format(
                summary.get("signal", "N/A"),
                summary.get("buy_count", 0),
                summary.get("sell_count", 0),
                summary.get("neutral_count", 0),
            ))
        price = result.get("price", {})
        if price:
            lines.append("Price: {} | Range: {}-{}".format(
                price.get("close", "N/A"),
                price.get("low", "N/A"),
                price.get("high", "N/A"),
            ))
        for name, data in indicators.items():
            if isinstance(data, dict):
                signal = data.get("signal", "")
                value = data.get("value", data.get("latest", ""))
                lines.append("  {}: {} [{}]".format(name.upper(), value, signal))
        return "\n".join(lines)


class MarketMoversInput(BaseModel):
    pass


class PolarisMarketMoversTool(BaseTool):
    name: str = "polaris_market_movers"
    description: str = "Get top market movers — gainers, losers, and most active stocks by volume. Useful for a quick snapshot of what is moving in the market right now."
    args_schema: Type[BaseModel] = MarketMoversInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self) -> str:
        client = PolarisClient(api_key=self.api_key)
        result = client.market_movers()
        lines = ["Market Movers"]
        for section, label in [("gainers", "Top Gainers"), ("losers", "Top Losers"), ("most_active", "Most Active")]:
            items = result.get(section, [])
            if items:
                lines.append("\n{}:".format(label))
                for item in items[:5]:
                    change = item.get("change_percent", item.get("changesPercentage", "N/A"))
                    lines.append("  {} — ${} ({}%)".format(
                        item.get("symbol", item.get("ticker", "?")),
                        item.get("price", "?"),
                        change,
                    ))
        return "\n".join(lines)


class EconomyInput(BaseModel):
    indicator: Optional[str] = Field(default=None, description="Indicator slug (e.g. gdp, cpi, unemployment, fed_funds). Omit for summary of all.")
    limit: Optional[int] = Field(default=None, description="Number of historical observations to return (default 30, max 100)")


class PolarisEconomyTool(BaseTool):
    name: str = "polaris_economy"
    description: str = "Get economic indicators from the FRED API. Without an indicator slug, returns a summary of all key indicators (GDP, CPI, unemployment, etc.). With a slug, returns that indicator's history."
    args_schema: Type[BaseModel] = EconomyInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, indicator: str = None, limit: int = None) -> str:
        client = PolarisClient(api_key=self.api_key)
        result = client.economy(indicator=indicator, limit=limit)
        if indicator:
            lines = ["{} ({})".format(result.get("name", indicator), result.get("indicator", indicator))]
            latest = result.get("latest", {})
            if latest:
                lines.append("Latest: {} ({}) | Units: {} | Frequency: {}".format(
                    latest.get("value", "N/A"),
                    latest.get("date", "N/A"),
                    result.get("units", "N/A"),
                    result.get("frequency", "N/A"),
                ))
            observations = result.get("observations", [])
            if observations:
                lines.append("Recent observations:")
                for obs in observations[:10]:
                    lines.append("  {} = {}".format(obs.get("date", "?"), obs.get("value", "?")))
        else:
            indicators = result.get("indicators", [])
            if not indicators:
                return "No economic data available."
            lines = ["Economic Indicators Summary ({} indicators)".format(len(indicators))]
            for ind in indicators:
                lines.append("  {} ({}): {} ({})".format(
                    ind.get("name", "?"),
                    ind.get("slug", "?"),
                    ind.get("latest_value", "N/A"),
                    ind.get("latest_date", "N/A"),
                ))
        return "\n".join(lines)


class ForexInput(BaseModel):
    pair: Optional[str] = Field(default=None, description="Forex pair (e.g. EURUSD, GBPJPY). Omit for all major pairs.")


class PolarisForexTool(BaseTool):
    name: str = "polaris_forex"
    description: str = "Get forex rates. Without a pair, returns all major currency pairs with current rates. With a pair, returns that pair's rate, change, and session data."
    args_schema: Type[BaseModel] = ForexInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, pair: str = None) -> str:
        client = PolarisClient(api_key=self.api_key)
        result = client.forex(pair=pair)
        if pair:
            lines = ["{} — Forex".format(result.get("pair", pair))]
            lines.append("Rate: {} | Change: {}%".format(
                result.get("rate", result.get("price", "N/A")),
                result.get("change_percent", result.get("changesPercentage", "N/A")),
            ))
            if result.get("high"):
                lines.append("High: {} | Low: {} | Open: {}".format(
                    result.get("high", "N/A"),
                    result.get("low", "N/A"),
                    result.get("open", "N/A"),
                ))
        else:
            pairs = result.get("pairs", result.get("rates", []))
            if not pairs:
                return "No forex data available."
            lines = ["Forex Rates ({} pairs)".format(len(pairs))]
            for p in pairs:
                lines.append("  {} = {} ({}%)".format(
                    p.get("pair", p.get("symbol", "?")),
                    p.get("rate", p.get("price", "?")),
                    p.get("change_percent", p.get("changesPercentage", "N/A")),
                ))
        return "\n".join(lines)


class CommoditiesInput(BaseModel):
    symbol: Optional[str] = Field(default=None, description="Commodity symbol (e.g. GC for gold, CL for crude oil). Omit for all commodities.")


class PolarisCommoditiesTool(BaseTool):
    name: str = "polaris_commodities"
    description: str = "Get commodity prices. Without a symbol, returns all tracked commodities with current prices. With a symbol, returns that commodity's price, change, and details."
    args_schema: Type[BaseModel] = CommoditiesInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, symbol: str = None) -> str:
        client = PolarisClient(api_key=self.api_key)
        result = client.commodities(symbol=symbol)
        if symbol:
            lines = ["{} — {}".format(
                result.get("symbol", symbol),
                result.get("name", "Commodity"),
            )]
            lines.append("Price: ${} | Change: {}%".format(
                result.get("price", "N/A"),
                result.get("change_percent", result.get("changesPercentage", "N/A")),
            ))
            if result.get("high"):
                lines.append("High: ${} | Low: ${} | Open: ${}".format(
                    result.get("high", "N/A"),
                    result.get("low", "N/A"),
                    result.get("open", "N/A"),
                ))
        else:
            commodities = result.get("commodities", result.get("data", []))
            if not commodities:
                return "No commodity data available."
            lines = ["Commodities ({} tracked)".format(len(commodities))]
            for c in commodities:
                lines.append("  {} ({}) — ${} ({}%)".format(
                    c.get("symbol", "?"),
                    c.get("name", "?"),
                    c.get("price", "?"),
                    c.get("change_percent", c.get("changesPercentage", "N/A")),
                ))
        return "\n".join(lines)


# ── Crypto Tools ──


class CryptoInput(BaseModel):
    symbol: Optional[str] = Field(default=None, description="Crypto symbol (e.g. BTC, ETH, SOL). Omit for market overview.")


class PolarisCryptoTool(BaseTool):
    name: str = "polaris_crypto"
    description: str = "Get crypto market data. Without a symbol, returns market overview (total market cap, BTC dominance). With a symbol, returns that token's price, volume, and metadata."
    args_schema: Type[BaseModel] = CryptoInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, symbol: str = None) -> str:
        client = PolarisClient(api_key=self.api_key)
        result = client.crypto(symbol=symbol)
        if symbol:
            lines = ["{} — {}".format(
                result.get("symbol", symbol),
                result.get("name", "Unknown"),
            )]
            lines.append("Price: ${} | 24h Change: {}%".format(
                result.get("price", result.get("current_price", "N/A")),
                result.get("change_24h", result.get("price_change_percentage_24h", "N/A")),
            ))
            lines.append("Market Cap: ${} | 24h Volume: ${}".format(
                result.get("market_cap", "N/A"),
                result.get("volume_24h", result.get("total_volume", "N/A")),
            ))
            if result.get("ath"):
                lines.append("ATH: ${} | ATH Change: {}%".format(
                    result.get("ath", "N/A"),
                    result.get("ath_change_percentage", "N/A"),
                ))
        else:
            lines = ["Crypto Market Overview"]
            lines.append("Total Market Cap: ${}".format(result.get("total_market_cap", "N/A")))
            lines.append("BTC Dominance: {}%".format(result.get("btc_dominance", "N/A")))
            lines.append("24h Volume: ${}".format(result.get("total_volume_24h", "N/A")))
            top = result.get("top_coins", [])
            if top:
                lines.append("\nTop coins:")
                for coin in top[:10]:
                    lines.append("  {} — ${} ({}%)".format(
                        coin.get("symbol", "?"),
                        coin.get("price", coin.get("current_price", "?")),
                        coin.get("change_24h", coin.get("price_change_percentage_24h", "?")),
                    ))
        return "\n".join(lines)


class DefiInput(BaseModel):
    protocol: Optional[str] = Field(default=None, description="DeFi protocol slug (e.g. aave, uniswap, lido). Omit for overview.")


class PolarisDefiTool(BaseTool):
    name: str = "polaris_defi"
    description: str = "Get DeFi data. Without a protocol, returns TVL overview with top protocols and chain breakdown. With a protocol slug, returns that protocol's TVL history and details."
    args_schema: Type[BaseModel] = DefiInput
    api_key: str = ""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, protocol: str = None) -> str:
        client = PolarisClient(api_key=self.api_key)
        result = client.crypto_defi(protocol=protocol)
        if protocol:
            lines = ["{} — DeFi Protocol".format(result.get("name", protocol))]
            lines.append("TVL: ${} | Chain: {}".format(
                result.get("tvl", "N/A"),
                result.get("chain", result.get("chains", "N/A")),
            ))
            if result.get("category"):
                lines.append("Category: {}".format(result.get("category")))
            history = result.get("tvl_history", [])
            if history:
                lines.append("Recent TVL history:")
                for h in history[-5:]:
                    lines.append("  {} = ${}".format(h.get("date", "?"), h.get("tvl", "?")))
        else:
            lines = ["DeFi Overview"]
            lines.append("Total TVL: ${}".format(result.get("total_tvl", "N/A")))
            protocols = result.get("top_protocols", result.get("protocols", []))
            if protocols:
                lines.append("\nTop protocols:")
                for p in protocols[:10]:
                    lines.append("  {} — TVL: ${} ({})".format(
                        p.get("name", "?"),
                        p.get("tvl", "?"),
                        p.get("chain", p.get("chains", "N/A")),
                    ))
            chains = result.get("chains", [])
            if isinstance(chains, list) and chains:
                lines.append("\nChain TVL:")
                for ch in chains[:10]:
                    lines.append("  {} — ${}".format(ch.get("name", "?"), ch.get("tvl", "?")))
        return "\n".join(lines)
