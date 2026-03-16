import { readFileSync } from "fs";
import { homedir } from "os";
import { join } from "path";
import { APIError, AuthenticationError, NotFoundError, RateLimitError, } from "./errors.js";
function readCredentials() {
    const envKey = process.env.POLARIS_API_KEY;
    if (envKey)
        return envKey;
    try {
        const key = readFileSync(join(homedir(), ".polaris", "credentials"), "utf-8").trim();
        return key || undefined;
    }
    catch {
        return undefined;
    }
}
const DEFAULT_BASE_URL = "https://api.thepolarisreport.com";
function toSnakeCase(str) {
    return str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);
}
function toSnakeParams(params) {
    const result = {};
    for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null) {
            result[toSnakeCase(key)] = String(value);
        }
    }
    return result;
}
/* ── Parsers: snake_case API → camelCase SDK ── */
function parseSource(raw) {
    return {
        name: (raw.name || ""),
        url: (raw.url || ""),
        trustLevel: raw.trust_level,
        verified: raw.verified,
    };
}
function parseEntity(raw) {
    return {
        name: (raw.name || ""),
        type: raw.type,
        sentiment: raw.sentiment,
        mentionCount: (raw.mention_count ?? raw.mentions_24h),
        ticker: raw.ticker,
        role: raw.role,
    };
}
function parseProvenance(raw) {
    return {
        reviewStatus: raw.review_status,
        aiContributionPct: raw.ai_contribution_pct,
        humanContributionPct: raw.human_contribution_pct,
        confidenceScore: raw.confidence_score,
        biasScore: raw.bias_score,
        agentsInvolved: raw.agents_involved,
    };
}
function parseBrief(raw) {
    const prov = raw.provenance
        ? parseProvenance(raw.provenance)
        : undefined;
    return {
        id: raw.id,
        headline: (raw.headline || ""),
        summary: raw.summary,
        body: raw.body,
        confidence: raw.confidence ?? prov?.confidenceScore,
        biasScore: raw.bias_score ?? prov?.biasScore,
        sentiment: raw.sentiment,
        counterArgument: raw.counter_argument,
        category: raw.category,
        tags: raw.tags,
        sources: raw.sources
            ? raw.sources.map(parseSource)
            : undefined,
        entitiesEnriched: raw.entities_enriched
            ? raw.entities_enriched.map(parseEntity)
            : undefined,
        structuredData: raw.structured_data,
        publishedAt: raw.published_at,
        reviewStatus: raw.review_status,
        provenance: prov,
        briefType: raw.brief_type,
        trending: raw.trending,
        topics: raw.topics,
        entities: raw.entities,
        impactScore: raw.impact_score,
        readTimeSeconds: raw.read_time_seconds,
        sourceCount: raw.source_count,
        correctionsCount: raw.corrections_count,
        biasAnalysis: raw.bias_analysis,
        fullSources: raw.full_sources,
    };
}
function parseSourceAnalysis(raw) {
    return {
        outlet: raw.outlet,
        headline: raw.headline,
        framing: raw.framing,
        politicalLean: raw.political_lean,
        loadedLanguage: raw.loaded_language,
        emphasis: raw.emphasis,
        omissions: raw.omissions,
        sentiment: raw.sentiment,
        rawExcerpt: raw.raw_excerpt,
    };
}
export class PolarisClient {
    constructor(options = {}) {
        this.apiKey = options.apiKey ?? readCredentials();
        this.baseUrl = (options.baseUrl || DEFAULT_BASE_URL).replace(/\/+$/, "");
    }
    async request(method, path, params, body) {
        let url = `${this.baseUrl}${path}`;
        if (params) {
            const snaked = toSnakeParams(params);
            const qs = new URLSearchParams(snaked).toString();
            if (qs)
                url += `?${qs}`;
        }
        const headers = { "Content-Type": "application/json" };
        if (this.apiKey) {
            headers["Authorization"] = `Bearer ${this.apiKey}`;
        }
        const init = { method, headers };
        if (body !== undefined) {
            init.body = JSON.stringify(body);
        }
        const resp = await fetch(url, init);
        if (!resp.ok) {
            await this.throwError(resp);
        }
        return resp.json();
    }
    async throwError(resp) {
        let body;
        try {
            body = await resp.json();
        }
        catch {
            body = await resp.text();
        }
        const msg = (body && typeof body === "object" && "error" in body)
            ? String(body.error)
            : String(body);
        if (resp.status === 401) {
            throw new AuthenticationError(msg, body);
        }
        if (resp.status === 404) {
            throw new NotFoundError(msg, body);
        }
        if (resp.status === 429) {
            const retryAfter = resp.headers.get("Retry-After") || resp.headers.get("RateLimit-Reset");
            const parsed = retryAfter ? (isNaN(Number(retryAfter)) ? retryAfter : Number(retryAfter)) : null;
            throw new RateLimitError(msg, body, parsed);
        }
        throw new APIError(msg, resp.status, body);
    }
    async feed(options = {}) {
        const params = { ...options };
        if (params.limit !== undefined) {
            params.perPage = params.limit;
            delete params.limit;
        }
        const data = await this.request("GET", "/api/v1/feed", params);
        return {
            briefs: (data.briefs || []).map(parseBrief),
            total: (data.total || 0),
            page: (data.page || 1),
            perPage: (data.per_page || 20),
            generatedAt: data.generated_at,
            agentVersion: data.agent_version,
            sourcesScanned24h: data.sources_scanned_24h,
        };
    }
    async brief(id, options = {}) {
        const params = {};
        if (options.includeFullText !== undefined) {
            params.includeFullText = options.includeFullText;
        }
        const data = await this.request("GET", `/api/v1/brief/${id}`, params);
        return parseBrief((data.brief || data));
    }
    async search(query, options = {}) {
        const params = { q: query, ...options };
        const data = await this.request("GET", "/api/v1/search", params);
        const dm = data.depth_metadata;
        return {
            briefs: (data.briefs || []).map(parseBrief),
            total: (data.total || 0),
            facets: data.facets,
            relatedQueries: data.related_queries,
            didYouMean: data.did_you_mean,
            tookMs: data.took_ms,
            meta: data.meta,
            depthMetadata: dm ? {
                depth: dm.depth,
                searchMs: dm.search_ms,
                crossRefMs: dm.cross_ref_ms,
                verificationMs: dm.verification_ms,
                totalMs: dm.total_ms,
            } : undefined,
        };
    }
    async generate(topic, category) {
        const body = { topic };
        if (category)
            body.category = category;
        const data = await this.request("POST", "/api/v1/generate/brief", undefined, body);
        return parseBrief((data.brief || data));
    }
    async entities(options = {}) {
        const data = await this.request("GET", "/api/v1/entities", options);
        return {
            entities: (data.entities || []).map(parseEntity),
        };
    }
    async entityBriefs(name, options = {}) {
        const data = await this.request("GET", `/api/v1/entities/${encodeURIComponent(name)}/briefs`, options);
        return (data.briefs || []).map(parseBrief);
    }
    async trendingEntities(limit) {
        const params = {};
        if (limit !== undefined)
            params.limit = limit;
        const data = await this.request("GET", "/api/v1/entities/trending", params);
        return {
            entities: (data.entities || []).map(parseEntity),
        };
    }
    async similar(id, options = {}) {
        const data = await this.request("GET", `/api/v1/similar/${id}`, options);
        return (data.briefs || []).map(parseBrief);
    }
    async clusters(options = {}) {
        const data = await this.request("GET", "/api/v1/clusters", options);
        return {
            clusters: (data.clusters || []),
            period: data.period,
        };
    }
    async data(options = {}) {
        const data = await this.request("GET", "/api/v1/data", options);
        return { data: (data.data || []) };
    }
    async agentFeed(options = {}) {
        const data = await this.request("GET", "/api/v1/agent-feed", options);
        return {
            briefs: (data.briefs || []).map(parseBrief),
            total: (data.total || 0),
            page: (data.page || 1),
            perPage: (data.per_page || 20),
            generatedAt: data.generated_at,
            agentVersion: data.agent_version,
            sourcesScanned24h: data.sources_scanned_24h,
        };
    }
    async compareSources(briefId) {
        const data = await this.request("GET", "/api/v1/compare/sources", { briefId });
        const rawBrief = data.polaris_brief;
        const rawAnalyses = data.source_analyses;
        return {
            topic: data.topic,
            shareId: data.share_id,
            polarisBrief: rawBrief ? parseBrief(rawBrief) : undefined,
            sourceAnalyses: rawAnalyses ? rawAnalyses.map(parseSourceAnalysis) : undefined,
            polarisAnalysis: data.polaris_analysis,
            generatedAt: data.generated_at,
        };
    }
    async research(query, options = {}) {
        const body = { query };
        if (options.maxSources !== undefined)
            body.max_sources = options.maxSources;
        if (options.depth !== undefined)
            body.depth = options.depth;
        if (options.category !== undefined)
            body.category = options.category;
        if (options.includeSources !== undefined)
            body.include_sources = options.includeSources;
        if (options.excludeSources !== undefined)
            body.exclude_sources = options.excludeSources;
        if (options.outputSchema !== undefined)
            body.output_schema = options.outputSchema;
        const data = await this.request("POST", "/api/v1/research", undefined, body);
        const sourcesUsed = (data.sources_used || []).map((s) => ({
            briefId: s.brief_id,
            headline: s.headline,
            confidence: s.confidence,
            category: s.category,
        }));
        const entityMap = (data.entity_map || []).map((e) => ({
            name: e.name,
            type: e.type,
            mentions: e.mentions,
            coOccursWith: (e.co_occurs_with || []).map((c) => ({
                entity: c.entity,
                count: c.count,
            })),
        }));
        const meta = data.metadata;
        return {
            query: data.query,
            report: data.report,
            sourcesUsed,
            entityMap,
            subQueries: data.sub_queries,
            metadata: meta ? {
                briefsAnalyzed: (meta.briefs_analyzed || 0),
                uniqueSources: (meta.unique_sources || 0),
                processingTimeMs: meta.processing_time_ms,
                modelsUsed: meta.models_used,
            } : undefined,
            structuredOutput: data.structured_output,
            structuredOutputError: data.structured_output_error,
        };
    }
    async extract(urls, includeMetadata) {
        const body = { urls };
        if (includeMetadata !== undefined)
            body.include_metadata = includeMetadata;
        const data = await this.request("POST", "/api/v1/extract", undefined, body);
        return {
            results: (data.results || []).map((r) => ({
                url: r.url,
                title: r.title,
                text: r.text,
                wordCount: r.word_count,
                language: r.language,
                publishedDate: r.published_date,
                domain: r.domain,
                success: r.success,
                error: r.error,
            })),
            creditsUsed: (data.credits_used || 0),
        };
    }
    async verify(claim, options = {}) {
        const body = { claim };
        if (options.context !== undefined)
            body.context = options.context;
        const data = await this.request("POST", "/api/v1/verify", undefined, body);
        const mapBrief = (b) => ({
            id: b.id,
            headline: b.headline,
            confidence: b.confidence,
            relevance: (b.relevance ?? null),
        });
        return {
            claim: data.claim,
            verdict: data.verdict,
            confidence: (data.confidence || 0),
            summary: (data.summary || ""),
            supportingBriefs: (data.supporting_briefs || []).map(mapBrief),
            contradictingBriefs: (data.contradicting_briefs || []).map(mapBrief),
            nuances: (data.nuances ?? null),
            sourcesAnalyzed: (data.sources_analyzed || 0),
            briefsMatched: (data.briefs_matched || 0),
            creditsUsed: (data.credits_used || 0),
            cached: (data.cached || false),
            processingTimeMs: (data.processing_time_ms || 0),
            modelUsed: (data.model_used ?? null),
        };
    }
    async trending(options = {}) {
        const data = await this.request("GET", "/api/v1/trending", options);
        return (data.briefs || []).map(parseBrief);
    }
    stream(options = {}) {
        let controller = null;
        return {
            start: (onBrief, onError) => {
                controller = new AbortController();
                const params = {};
                if (options.categories)
                    params.categories = options.categories;
                let url = `${this.baseUrl}/api/v1/stream`;
                const snaked = toSnakeParams(params);
                const qs = new URLSearchParams(snaked).toString();
                if (qs)
                    url += `?${qs}`;
                const headers = { Accept: "text/event-stream" };
                if (this.apiKey)
                    headers["Authorization"] = `Bearer ${this.apiKey}`;
                fetch(url, { headers, signal: controller.signal })
                    .then(async (resp) => {
                    if (!resp.ok) {
                        await this.throwError(resp);
                    }
                    const reader = resp.body?.getReader();
                    if (!reader)
                        return;
                    const decoder = new TextDecoder();
                    let buffer = "";
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done)
                            break;
                        buffer += decoder.decode(value, { stream: true });
                        const lines = buffer.split("\n");
                        buffer = lines.pop() || "";
                        for (const line of lines) {
                            if (line.startsWith("data:")) {
                                const payload = line.slice(5).trim();
                                if (payload && payload !== "[DONE]") {
                                    try {
                                        const data = JSON.parse(payload);
                                        onBrief(parseBrief(data));
                                    }
                                    catch {
                                        // skip malformed JSON
                                    }
                                }
                            }
                        }
                    }
                })
                    .catch((err) => {
                    if (err.name !== "AbortError") {
                        onError?.(err);
                    }
                });
            },
            stop: () => {
                controller?.abort();
                controller = null;
            },
        };
    }
}
//# sourceMappingURL=client.js.map