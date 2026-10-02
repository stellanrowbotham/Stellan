<!-- captured: 2026-10-02 | origin: https://github.com/tobi/qmd @ commit 04e4dbd8245c527a88f1a8f0bda547aef9ca81fb (2026-09-09) | author: tobi (GitHub) and qmd contributors | license: MIT | note: verbatim excerpts selected by Claude to check README claims; line numbers refer to that commit -->

# qmd source excerpts (commit 04e4dbd)

## src/store.ts:103 — multi-get default
```ts
export const DEFAULT_MULTI_GET_MAX_BYTES = 64 * 1024; // 64KB
```

## src/store.ts:426-430 — constants
```ts
export const STRONG_SIGNAL_MIN_SCORE = 0.85;
export const STRONG_SIGNAL_MIN_GAP = 0.15;
// Max candidates to pass to reranker — balances quality vs latency.
// 40 keeps rank 31-40 visible to the reranker (matters for recall on broad queries).
export const RERANK_CANDIDATE_LIMIT = 40;
```

## src/store.ts:5520-5584 — RRF weights and hybridQuery pipeline
```ts
 */
export function getHybridRrfWeights(rankedListMeta: RankedListMeta[]): number[] {
  return rankedListMeta.map(meta => meta.queryType === "original" ? 2.0 : 1.0);
}

/**
 * Hybrid search: BM25 + vector + query expansion + RRF + chunked reranking.
 *
 * Pipeline:
 * 1. BM25 probe → skip expansion if strong signal
 * 2. expandQuery() → typed query variants (lex/vec/hyde)
 * 3. Type-routed search: original→vector, lex→FTS, vec/hyde→vector
 * 4. RRF fusion → slice to candidateLimit
 * 5. chunkDocument() + keyword-best-chunk selection
 * 6. rerank on chunks (NOT full bodies — O(tokens) trap)
 * 7. Position-aware score blending (RRF rank × reranker score)
 * 8. Dedup by file, filter by minScore, slice to limit
 */
export async function hybridQuery(
  store: Store,
  query: string,
  options?: HybridQueryOptions
): Promise<HybridQueryResult[]> {
  const limit = options?.limit ?? 10;
  const minScore = options?.minScore ?? 0;
  const candidateLimit = options?.candidateLimit ?? RERANK_CANDIDATE_LIMIT;
  const collection = options?.collection;
  const filter = options?.filter;
  const explain = options?.explain ?? false;
  const intent = options?.intent;
  const skipRerank = options?.skipRerank ?? false;
  const hooks = options?.hooks;

  const rankedLists: RankedResult[][] = [];
  const rankedListMeta: RankedListMeta[] = [];
  const docidMap = new Map<string, string>(); // filepath -> docid
  const hasVectors = !!store.db.prepare(
    `SELECT name FROM sqlite_master WHERE type='table' AND name='vectors_vec'`
  ).get();

  // Step 1: BM25 probe — strong signal skips expensive LLM expansion
  // When intent is provided, disable strong-signal bypass — the obvious BM25
  // match may not be what the caller wants (e.g. "performance" with intent
  // "web page load times" should NOT shortcut to a sports-performance doc).
  // Pass collection and metadata filter directly into FTS query (filter at
  // SQL level, not post-hoc) — the strong-signal decision must be based only
  // on eligible documents.
  const initialFts = store.searchFTS(query, 20, collection, filter);
  const topScore = initialFts[0]?.score ?? 0;
  const secondScore = initialFts[1]?.score ?? 0;
  const hasStrongSignal = !intent && initialFts.length > 0
    && topScore >= STRONG_SIGNAL_MIN_SCORE
    && (topScore - secondScore) >= STRONG_SIGNAL_MIN_GAP;

  if (hasStrongSignal) hooks?.onStrongSignal?.(topScore);

  // Step 2: Expand query (or skip if strong signal)
  hooks?.onExpandStart?.();
  const expandStart = Date.now();
  const expanded = hasStrongSignal
    ? []
    : await store.expandQuery(query);

  hooks?.onExpand?.(query, expanded, Date.now() - expandStart);

```

## src/store.ts:5674-5678 — fusion and candidate slice
```ts
  // expansion-derived lists stay at 1x independent of insertion order.
  const weights = getHybridRrfWeights(rankedListMeta);
  const fused = reciprocalRankFusion(rankedLists, weights);
  const rrfTraceByFile = explain ? buildRrfTrace(rankedLists, weights, rankedListMeta) : null;
  const candidates = fused.slice(0, candidateLimit);
```

## src/llm.ts:1630-1722 — expandQuery
```ts
  async expandQuery(query: string, options: { context?: string, includeLexical?: boolean } = {}): Promise<Queryable[]> {
    if (this._ciMode) throw new Error("LLM operations are disabled in CI (set CI=true)");
    // Ping activity at start to keep models alive during this operation
    this.touchActivity();

    const llama = await this.ensureLlama();
    await this.ensureGenerateModel();

    const includeLexical = options.includeLexical ?? true;
    const context = options.context;

    // The expansion prompt consumes ONLY the query text. Caller intent is
    // free-form meta-language that the expansion model reproduced verbatim as
    // lex/vec sub-queries — degenerate terms that match nothing. Intent still
    // shapes retrieval where it belongs: the reranker query prefix and
    // keyword-based chunk/snippet selection.
    const prompt = `/no_think Expand this search query: ${query}`;

    // Set up inside the try so any failure (grammar creation, context
    // allocation/VRAM, session prompt) falls back to the original query
    // instead of propagating and failing the caller's operation.
    let genContext: Awaited<ReturnType<LlamaModel["createContext"]>> | undefined;
    let sequence: { dispose: () => void | Promise<void> } | undefined;
    try {
      const grammar = await llama.createGrammar({
        grammar: `
        root ::= line+
        line ::= type ": " content "\\n"
        type ::= "lex" | "vec" | "hyde"
        content ::= [^\\n]+
      `
      });

      // Create a bounded context for expansion to prevent large default VRAM allocations.
      genContext = await this.generateModel!.createContext({
        contextSize: this.expandContextSize,
      });
      sequence = genContext.getSequence();
      const { LlamaChatSession } = await loadNodeLlamaCpp();
      const session = new LlamaChatSession({ contextSequence: sequence });

      // Qwen3 recommended settings for non-thinking mode:
      // temp=0.7, topP=0.8, topK=20, presence_penalty for repetition
      // DO NOT use greedy decoding (temp=0) - causes infinite loops
      const result = await session.prompt(prompt, {
        grammar,
        maxTokens: 600,
        temperature: 0.7,
        topK: 20,
        topP: 0.8,
        repeatPenalty: {
          lastTokens: 64,
          presencePenalty: 0.5,
        },
      });

      const lines = result.trim().split("\n");
      const queryLower = query.toLowerCase();
      const queryTerms = queryLower.replace(/[^a-z0-9\s]/g, " ").split(/\s+/).filter(Boolean);

      const hasQueryTerm = (text: string): boolean => {
        const lower = text.toLowerCase();
        if (queryTerms.length === 0) return true;
        return queryTerms.some(term => lower.includes(term));
      };

      const queryables: Queryable[] = lines.map(line => {
        const colonIdx = line.indexOf(":");
        if (colonIdx === -1) return null;
        const type = line.slice(0, colonIdx).trim();
        if (type !== 'lex' && type !== 'vec' && type !== 'hyde') return null;
        const text = line.slice(colonIdx + 1).trim();
        if (!hasQueryTerm(text)) return null;
        return { type: type as QueryType, text };
      }).filter((q): q is Queryable => q !== null);

      // Filter out lex entries if not requested
      const filtered = includeLexical ? queryables : queryables.filter(q => q.type !== 'lex');
      if (filtered.length > 0) return filtered;

      const fallback: Queryable[] = [
        { type: 'hyde', text: `Information about ${query}` },
        { type: 'lex', text: query },
        { type: 'vec', text: query },
      ];
      return includeLexical ? fallback : fallback.filter(q => q.type !== 'lex');
    } catch (error) {
      console.error("Structured query expansion failed:", error);
      // Fallback to original query
      const fallback: Queryable[] = [{ type: 'vec', text: query }];
      if (includeLexical) fallback.unshift({ type: 'lex', text: query });
      return fallback;
    } finally {
```

## src/mcp/server.ts:526-531 — MCP multi_get default
```ts
        maxBytes: z.number().optional().default(DEFAULT_MULTI_GET_MAX_BYTES).describe("Skip files larger than this (default: 65536 = 64KB)"),
        lineNumbers: z.boolean().optional().default(true).describe("Add line numbers to output (format: 'N: content'). On by default; set false for raw content."),
      }),
    },
    track(async ({ pattern, maxLines, maxBytes, lineNumbers }) => {
      const { docs, errors } = await store.multiGet(pattern, { includeBody: true, maxBytes: maxBytes || DEFAULT_MULTI_GET_MAX_BYTES });
```
