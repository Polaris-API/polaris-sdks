"""
VeroQ Prompt Shield — One-line verification for any LLM output.

Usage:
    from veroq import shield

    # Basic
    result = shield("NVIDIA reported $22B in Q4 revenue")
    print(result.trust_score)       # 0.73
    print(result.verified_text)     # corrected version
    print(result.corrections)       # list of corrections

    # Wrap any LLM call
    response = openai.chat.completions.create(model="gpt-4o", messages=[...])
    verified = shield(response.choices[0].message.content)

    # With config
    result = shield(text, agent_id="my-bot", block_if_untrusted=True)
"""

from .client import VeroqClient


class ShieldResult:
    """Result of shielding an LLM output through VeroQ verification."""

    def __init__(self, raw, full_text=None):
        self._raw = raw
        self._full_text = full_text
        self.text = raw.get("text", "")
        self.source = raw.get("source", "unknown")
        self.claims = raw.get("claims", [])
        self.claims_extracted = raw.get("claims_extracted", 0)
        self.claims_verified = raw.get("claims_verified", 0)
        self.claims_supported = raw.get("claims_supported", 0)
        self.claims_contradicted = raw.get("claims_contradicted", 0)
        self.overall_confidence = raw.get("overall_confidence", 0)
        self.overall_verdict = raw.get("overall_verdict", "unknown")
        self.trust_score = raw.get("overall_confidence") or 0
        self.summary = raw.get("summary", "")
        self.credits_used = raw.get("credits_used", 0)
        self.processing_time_ms = raw.get("processing_time_ms", 0)

    @property
    def is_trusted(self):
        """True if all extracted claims are supported or unverifiable (none contradicted)."""
        return self.claims_contradicted == 0

    @property
    def corrections(self):
        """List of corrections for contradicted claims."""
        return [
            {"claim": c["text"], "correction": c.get("correction"), "confidence": c.get("confidence", 0)}
            for c in self.claims
            if c.get("verdict") == "contradicted" and c.get("correction")
        ]

    @property
    def verified_text(self):
        """Original text with contradicted claims annotated."""
        text = self._full_text or self._raw.get("text", "")
        for c in self.claims:
            if c.get("verdict") == "contradicted" and c.get("correction"):
                original = c["text"]
                if original in text:
                    text = text.replace(original, "[CORRECTED: {}]".format(c["correction"][:200]))
        return text

    @property
    def receipt_ids(self):
        """List of verification receipt IDs for each claim."""
        return [c.get("receipt_id") for c in self.claims if c.get("receipt_id")]

    def __repr__(self):
        icon = "+" if self.is_trusted else "!"
        return "<ShieldResult [{}] trust={:.0%} claims={} corrected={}>".format(
            icon, self.trust_score, self.claims_extracted, self.claims_contradicted
        )


# Module-level client (lazy-initialized)
_client = None


def _get_client(api_key=None, base_url=None):
    global _client
    if _client is None or api_key:
        _client = VeroqClient(api_key=api_key, base_url=base_url)
    return _client


def shield(text, source=None, agent_id=None, max_claims=5, api_key=None, base_url=None, block_if_untrusted=False):
    """Verify any LLM output with one function call.

    Takes any text (from any LLM, any source) and returns a ShieldResult
    with trust score, claim verdicts, corrections, and receipt IDs.

    Args:
        text: The LLM output to verify (string, 20-10000 chars).
        source: Optional source identifier (e.g., "gpt-4o", "claude-3").
        agent_id: Optional agent ID for memory integration.
        max_claims: Max claims to extract and verify (1-10, default 5).
        api_key: Optional API key override.
        base_url: Optional API base URL override.
        block_if_untrusted: If True, raises VeroqError when claims are contradicted.

    Returns:
        ShieldResult with trust_score, corrections, verified_text, receipt_ids.

    Raises:
        VeroqError: If block_if_untrusted=True and claims are contradicted.

    Example::

        from veroq import shield

        result = shield("NVIDIA's Q4 revenue was $22B")
        print(result.trust_score)    # 0.85
        print(result.is_trusted)     # False
        print(result.corrections)    # [{"claim": "...", "correction": "..."}]
        print(result.verified_text)  # text with corrections inline
    """
    if not text or not isinstance(text, str) or len(text.strip()) < 20:
        return ShieldResult({
            "text": text or "",
            "claims": [],
            "claims_extracted": 0,
            "overall_confidence": 1.0,
            "overall_verdict": "no_claims",
            "summary": "Text too short to extract verifiable claims.",
        })

    client = _get_client(api_key, base_url)

    # Call verify/output
    raw = client.verify_output(text, source=source, max_claims=max_claims)

    # Store to agent memory if agent_id provided
    if agent_id and raw.get("claims"):
        try:
            client.memory_store(
                agent_id=agent_id,
                key="shield:{}".format(text[:50].replace(" ", "_")),
                value={
                    "trust_score": raw.get("overall_confidence", 0),
                    "verdict": raw.get("overall_verdict"),
                    "claims_extracted": raw.get("claims_extracted", 0),
                    "claims_contradicted": raw.get("claims_contradicted", 0),
                },
                category="verification",
                query_text=text[:200],
            )
        except Exception:
            pass  # Memory storage is non-blocking

    result = ShieldResult(raw, full_text=text)

    if block_if_untrusted and not result.is_trusted:
        from .exceptions import VeroqError
        raise VeroqError(
            "Shield blocked: {} of {} claims contradicted. Corrections: {}".format(
                result.claims_contradicted, result.claims_extracted,
                "; ".join(c["claim"][:80] for c in result.corrections),
            )
        )

    return result
