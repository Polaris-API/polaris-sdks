/**
 * VeroQ Prompt Shield — One-line verification for any LLM output.
 *
 * @example
 * ```typescript
 * import { shield } from "@veroq/sdk";
 *
 * const result = await shield("NVIDIA reported $22B in Q4 revenue");
 * console.log(result.trustScore);    // 0.73
 * console.log(result.isTrusted);     // false
 * console.log(result.corrections);   // [{claim, correction, confidence}]
 * console.log(result.verifiedText);  // text with corrections inline
 *
 * // Wrap any LLM call
 * const response = await openai.chat.completions.create({...});
 * const verified = await shield(response.choices[0].message.content);
 * ```
 */

import { VeroqClient } from "./client.js";
import { VeroqError } from "./errors.js";

export interface ShieldOptions {
  /** Source identifier (e.g., "gpt-4o", "claude-3") */
  source?: string;
  /** Agent ID for memory integration */
  agentId?: string;
  /** Max claims to extract (1-10, default 5) */
  maxClaims?: number;
  /** API key override */
  apiKey?: string;
  /** If true, throws VeroqError when claims are contradicted */
  blockIfUntrusted?: boolean;
}

export interface ShieldClaim {
  text: string;
  category: string;
  verdict: string;
  confidence: number;
  correction: string | null;
  receiptId: string | null;
  evidenceChain: Array<{ source: string; position: string; snippet: string }>;
}

export class ShieldResult {
  /** Original text (truncated) */
  readonly text: string;
  /** Source identifier */
  readonly source: string;
  /** All extracted claims with verdicts */
  readonly claims: ShieldClaim[];
  /** Number of claims extracted */
  readonly claimsExtracted: number;
  /** Number of claims verified */
  readonly claimsVerified: number;
  /** Number of claims supported */
  readonly claimsSupported: number;
  /** Number of claims contradicted */
  readonly claimsContradicted: number;
  /** Overall trust score (0-1) */
  readonly trustScore: number;
  /** Overall verdict */
  readonly overallVerdict: string;
  /** Summary */
  readonly summary: string;
  /** Credits used */
  readonly creditsUsed: number;
  /** Processing time in ms */
  readonly processingTimeMs: number;

  /** Full original text (before server truncation) */
  private readonly _fullText: string;

  constructor(raw: Record<string, any>, fullText?: string) {
    this._fullText = fullText || raw.text || "";
    this.text = raw.text || "";
    this.source = raw.source || "unknown";
    this.claims = (raw.claims || []).map((c: any) => ({
      text: c.text,
      category: c.category,
      verdict: c.verdict,
      confidence: c.confidence || 0,
      correction: c.correction || null,
      receiptId: c.receipt_id || null,
      evidenceChain: c.evidence_chain || [],
    }));
    this.claimsExtracted = raw.claims_extracted || 0;
    this.claimsVerified = raw.claims_verified || 0;
    this.claimsSupported = raw.claims_supported || 0;
    this.claimsContradicted = raw.claims_contradicted || 0;
    this.trustScore = raw.overall_confidence || 0;
    this.overallVerdict = raw.overall_verdict || "unknown";
    this.summary = raw.summary || "";
    this.creditsUsed = raw.credits_used || 0;
    this.processingTimeMs = raw.processing_time_ms || 0;
  }

  /** True if no claims were contradicted */
  get isTrusted(): boolean {
    return this.claimsContradicted === 0;
  }

  /** Corrections for contradicted claims */
  get corrections(): Array<{ claim: string; correction: string; confidence: number }> {
    return this.claims
      .filter(c => c.verdict === "contradicted" && c.correction)
      .map(c => ({ claim: c.text, correction: c.correction!, confidence: c.confidence }));
  }

  /** Text with contradicted claims annotated */
  get verifiedText(): string {
    let result = this._fullText;
    for (const c of this.claims) {
      if (c.verdict === "contradicted" && c.correction && result.includes(c.text)) {
        result = result.replace(c.text, `[CORRECTED: ${c.correction.slice(0, 200)}]`);
      }
    }
    return result;
  }

  /** Verification receipt IDs */
  get receiptIds(): string[] {
    return this.claims.map(c => c.receiptId).filter((id): id is string => !!id);
  }
}

// Module-level client
let _client: VeroqClient | null = null;

function getClient(apiKey?: string): VeroqClient {
  if (!_client || apiKey) {
    _client = new VeroqClient({ apiKey });
  }
  return _client;
}

/**
 * Shield any LLM output with VeroQ verification.
 *
 * Extracts claims, verifies each against evidence, returns trust score
 * with corrections for any contradicted claims.
 *
 * @example
 * ```typescript
 * import { shield } from "@veroq/sdk";
 *
 * // Basic
 * const result = await shield("NVIDIA's Q4 revenue exceeded $22B");
 * console.log(result.trustScore, result.corrections);
 *
 * // With options
 * const result = await shield(llmOutput, {
 *   source: "gpt-4o",
 *   agentId: "my-bot",
 *   blockIfUntrusted: true,
 * });
 * ```
 */
export async function shield(text: string, options: ShieldOptions = {}): Promise<ShieldResult> {
  if (!text || text.trim().length < 20) {
    return new ShieldResult({
      text: text || "",
      claims: [],
      claims_extracted: 0,
      overall_confidence: 1.0,
      overall_verdict: "no_claims",
      summary: "Text too short to extract verifiable claims.",
    });
  }

  const client = getClient(options.apiKey);

  const raw = await client.verifyOutput(text, {
    source: options.source,
    maxClaims: options.maxClaims,
  });

  // Store to memory if agentId provided
  if (options.agentId && raw.claims?.length) {
    client.memoryStore(options.agentId, `shield:${text.slice(0, 50).replace(/\s+/g, "_")}`, {
      trust_score: raw.overall_confidence,
      verdict: raw.overall_verdict,
      claims_extracted: raw.claims_extracted,
      claims_contradicted: raw.claims_contradicted,
    }, { category: "verification", queryText: text.slice(0, 200) }).catch(() => {});
  }

  const result = new ShieldResult(raw, text);

  if (options.blockIfUntrusted && !result.isTrusted) {
    throw new VeroqError(
      `Shield blocked: ${result.claimsContradicted} of ${result.claimsExtracted} claims contradicted. ` +
      `Corrections: ${result.corrections.map(c => c.claim.slice(0, 80)).join("; ")}`,
    );
  }

  return result;
}
