# Edge Cases & Expected Behaviors

**Project:** AI-Powered Restaurant Recommendation System (Zomato Use Case)  
**Aligned with:** [ARCHITECTURE.md](./ARCHITECTURE.md) (same heading names and component names)  
**Companion:** [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)

This document defines **what can go wrong**, **expected system behavior**, and **how to verify** each case. Implement handlers in the layer indicated; do not contradict architectural constraints (filter before generate, bounded context, grounding).

---

## How to read this document

| Column | Meaning |
|--------|---------|
| **ID** | Stable reference for tests and issues |
| **Layer** | Maps to `ARCHITECTURE.md` — Logical Layers / Component Design |
| **Trigger** | Input or condition that causes the edge case |
| **Expected behavior** | Required MVP behavior per architecture |
| **HTTP / UI** | Suggested user-facing signal (if API or Streamlit) |
| **Test** | Suggested automated or manual check |

**Severity:** `P0` = must handle for milestone; `P1` = should handle; `P2` = optional / future extension.

---

## Architecture section index

| `ARCHITECTURE.md` section | Edge-case groups |
|---------------------------|------------------|
| Goals and Constraints — Grounding | EC-G*, EC-LLM* |
| Component Design → 1. Data Ingestion Pipeline | EC-ING* |
| Component Design → 2. Restaurant Store & Repository | EC-REPO* |
| Component Design → 3. User Input Module | EC-IN* |
| Component Design → 4. Filter Service | EC-FIL* |
| Component Design → 5. Integration Layer (Prompt Builder) | EC-PRM* |
| Component Design → 6. Recommendation Engine (LLM Client) | EC-LLM* |
| Component Design → 7. Recommendation Orchestrator | EC-ORCH* |
| Request Lifecycle | EC-ORCH*, EC-API* |
| LLM Integration Architecture — Failure Handling | EC-LLM* |
| API Design | EC-API* |
| Presentation Layer | EC-UI* |
| Cross-Cutting Concerns — Configuration / Security / Logging | EC-CFG*, EC-SEC* |
| Data Architecture — Budget Band Mapping | EC-ING*, EC-FIL* |

---

## 1. Data Ingestion Pipeline

*Architecture: **Component Design → 1. Data Ingestion Pipeline***

| ID | Sev | Trigger | Expected behavior | HTTP / UI | Test |
|----|-----|---------|-------------------|-----------|------|
| EC-ING-01 | P0 | Hugging Face unreachable or dataset name wrong | Ingest/startup **fails** with clear log; app does not serve recommendations with empty store | 503 on `/health` or startup error | Mock HF failure; assert no partial recommend path |
| EC-ING-02 | P0 | Raw schema columns differ from assumed names | `SchemaNormalizer` maps flexibly; document mapping in code; skip unmapped optional fields | N/A (offline) | Fixture with alternate column names |
| EC-ING-03 | P0 | Row missing `name` or `location` | Drop row during preprocess | N/A | Assert dropped count in logs |
| EC-ING-04 | P0 | Duplicate `name` + `location` | Keep one; stable `id` via hash of name+location | N/A | Dedupe unit test |
| EC-ING-05 | P0 | `rating` null, negative, or > 5 | Clamp to [0, 5] or drop if invalid per project rule | N/A | Preprocessor tests |
| EC-ING-06 | P0 | `estimated_cost` null or zero | Exclude from budget band or assign default band per config; document rule | N/A | Preprocessor tests |
| EC-ING-07 | P1 | Comma-separated cuisines string | Split to `list[str]`; lowercase; trim | N/A | `"Italian, Chinese"` → two tags |
| EC-ING-08 | P1 | Location spelling variants (e.g. Bengaluru vs Bangalore) | Normalize via alias map in preprocessor | Filter may still miss if user types unmapped variant | Alias table test |
| EC-ING-09 | P1 | Cost at band boundary (500, 1500) | Apply `BUDGET_LOW_MAX` / `BUDGET_*` thresholds consistently (≤ vs < per config) | N/A | Boundary value tests |
| EC-ING-10 | P2 | Scheduled re-ingest while app running | Out of MVP scope; if added, reload repository atomically | N/A | Future |

**Invariant:** Never call LLM during ingest (architecture — Cost Control).

---

## 2. Restaurant Store & Repository

*Architecture: **Component Design → 2. Restaurant Store & Repository**, **Data Architecture***

| ID | Sev | Trigger | Expected behavior | HTTP / UI | Test |
|----|-----|---------|-------------------|-----------|------|
| EC-REPO-01 | P0 | `DATA_PATH` missing or corrupt Parquet | Startup fails or falls back to re-ingest per config | 503 store not loaded | Missing file boot test |
| EC-REPO-02 | P0 | `get_by_ids` includes unknown id | Omit or return empty for that id; merger must not invent rows | N/A | Unknown id query |
| EC-REPO-03 | P1 | Empty dataset after cleaning | Startup fails with explicit message | 503 | Zero-row ingest |
| EC-REPO-04 | P1 | `filter(criteria)` with all criteria null/empty | Treat as invalid at validator, not repository | 400 | API validation |

---

## 3. User Input Module

*Architecture: **Component Design → 3. User Input Module***

| ID | Sev | Trigger | Expected behavior | HTTP / UI | Test |
|----|-----|---------|-------------------|-----------|------|
| EC-IN-01 | P0 | Empty `location` or `cuisine` | Reject before orchestrator | 400 validation error | Empty string POST |
| EC-IN-02 | P0 | `min_rating` < 0 or > 5 | Reject | 400 | -1, 6.0 |
| EC-IN-03 | P0 | Invalid `budget` (not low/medium/high) | Reject | 400 | `"cheap"` |
| EC-IN-04 | P0 | `top_k` < 1 or very large | Enforce sensible bounds (e.g. 1–10) per validator | 400 | 0, 100 |
| EC-IN-05 | P1 | Whitespace-only strings | Trim; if still empty → EC-IN-01 | 400 | `"   "` |
| EC-IN-06 | P1 | `additional_preferences` extremely long | Truncate or reject at max length (Cross-Cutting — Security) | 400 or truncated | > N chars |
| EC-IN-07 | P1 | Special characters / HTML in free text | Sanitize for display; do not execute | Safe render in UI | Injection strings |
| EC-IN-08 | P2 | Location not in dataset cities | Architecture: ambiguous location → fuzzy/suggest (**future**). MVP: allow substring filter; may yield zero candidates → EC-FIL-01 | Empty state or 200 empty list | Unknown city |
| EC-IN-09 | P2 | Missing optional `additional_preferences` | Accept `null`/omit; forward as none to prompt | 200 | Omit field |

**Schema note:** `additional_preferences` is `str | None` (single optional string), not a structured list, unless you extend the schema.

---

## 4. Filter Service

*Architecture: **Component Design → 4. Filter Service**, **FilterCriteria**, post-filter ranking*

| ID | Sev | Trigger | Expected behavior | HTTP / UI | Test |
|----|-----|---------|-------------------|-----------|------|
| EC-FIL-01 | P0 | **Zero matches** after location, budget, cuisine, `min_rating` | Return empty `FilterResult`; orchestrator **skips LLM**; UI empty state | 200 `recommendations: []` + helpful message | Impossible combo |
| EC-FIL-02 | P0 | **Too many matches** | Pre-sort by rating (then votes if in metadata); cap at `MAX_CANDIDATES` | 200; `meta.candidates_considered` ≤ cap | Broad city+cuisine |
| EC-FIL-03 | P0 | `additional_preferences` provided | **Do not** apply structural filter; pass text only to Prompt Builder | N/A | Assert filter ignores extras |
| EC-FIL-04 | P1 | Case mismatch on location/cuisine | Case-insensitive match on normalized fields | 200 | `"bangalore"`, `"ITALIAN"` |
| EC-FIL-05 | P1 | Cuisine substring vs tag (e.g. "Ital" vs "Italian") | Any-match on `cuisines` list per configured logic (substring acceptable for MVP) | 200 | Partial cuisine |
| EC-FIL-06 | P1 | `min_rating` exactly equals restaurant rating | Include (`rating >= min_rating`) | 200 | rating == threshold |
| EC-FIL-07 | P1 | Single candidate after filter | Still call LLM (unless product decision: skip — document if skipped) | 200 one card | One row |
| EC-FIL-08 | P2 | Ambiguous location (e.g. "MG Road") | **Future:** fuzzy match or suggest cities; MVP: substring only | TBD | Future |

**Architecture explicit edge cases (Filter Service table):**

| Scenario | Required behavior |
|----------|-----------------|
| Zero matches after hard filters | Empty result; UI message; **skip LLM** |
| Too many matches | Cap + pre-sort by rating before LLM |
| Ambiguous location | Fuzzy/suggest — **future** |

**Not in architecture MVP:** automatic constraint broadening (relaxing rating/budget). If product adds it, document under Future Extensions and set `meta.relaxed_constraints`.

---

## 5. Integration Layer (Prompt Builder)

*Architecture: **Component Design → 5. Integration Layer (Prompt Builder)***

| ID | Sev | Trigger | Expected behavior | HTTP / UI | Test |
|----|-----|---------|-------------------|-----------|------|
| EC-PRM-01 | P0 | Zero candidates passed to builder | Builder must not be invoked (orchestrator guard) | N/A | Orchestrator unit test |
| EC-PRM-02 | P0 | Large candidate list | Only top `MAX_CANDIDATES` after filter reach prompt | N/A | Count ids in prompt |
| EC-PRM-03 | P0 | Long `additional_preferences` | Truncate to token-safe length; log truncation | 200 | Max length input |
| EC-PRM-04 | P1 | `top_k` > candidate count | Instruct LLM to return at most available; parser accepts fewer | 200 | top_k=10, 3 candidates |
| EC-PRM-05 | P1 | Special characters in restaurant names | Escape safely in JSON/markdown block | 200 | Names with quotes |
| EC-PRM-06 | P1 | Missing optional metadata fields | Omit from candidate block; do not send null noise | N/A | Snapshot prompt |

**Prompt invariants:** List allowed `restaurant_id` values; instruct model not to invent venues (Goals — Grounding).

---

## 6. Recommendation Engine (LLM Client, Parser, Merger)

*Architecture: **Component Design → 6. Recommendation Engine**, **LLM Integration Architecture***

### 6.1 LLM provider failures

| ID | Sev | Trigger | Expected behavior | HTTP / UI | Test |
|----|-----|---------|-------------------|-----------|------|
| EC-LLM-01 | P0 | API **timeout** | Retry once with backoff; then **rating-based fallback** top-K | 200 degraded or 502 if no fallback | Mock timeout |
| EC-LLM-02 | P0 | **Invalid JSON** in response | Regex extract JSON block; retry repair optional; else fallback | 200 degraded | Malformed fixture |
| EC-LLM-03 | P0 | **Unknown `restaurant_id`** in LLM output | Drop entry; log warning; backfill rank from fallback if needed | 200 | ID not in candidates |
| EC-LLM-04 | P0 | Duplicate ranks or gaps in ranks | Normalize to 1..K or drop invalid; fill from fallback | 200 | ranks 1,1,3 |
| EC-LLM-05 | P0 | Fewer than `top_k` valid recommendations | Return available; no fabricated rows | 200 | Partial parse |
| EC-LLM-06 | P0 | Missing or empty `LLM_API_KEY` | Fallback ranker with template explanations | 200 + banner in UI | No env key |
| EC-LLM-07 | P1 | **Rate limit** (429) | User-visible retry message; optional cache (**future**) | 502/503 or retry UI | Mock 429 |
| EC-LLM-08 | P1 | Provider 5xx | Same as timeout path after retry | 502 if hard fail | Mock 500 |
| EC-LLM-09 | P1 | Empty LLM content | Fallback | 200 degraded | Empty string |
| EC-LLM-10 | P1 | LLM adds restaurants not in candidate list | Parser drops; never merge hallucinated ids | 200 | Extra ids in JSON |
| EC-LLM-11 | P1 | LLM omits `summary` | Return recommendations without summary | 200 | Missing summary field |
| EC-LLM-12 | P2 | Token limit exceeded on prompt | Reduce candidates or truncate; log error | 502 or fallback | Huge city |

### 6.2 Ranking and display merge

| ID | Sev | Trigger | Expected behavior | HTTP / UI | Test |
|----|-----|---------|-------------------|-----------|------|
| EC-LLM-13 | P0 | LLM rank order vs dataset fields | **Primary rank:** LLM `recommendations[].rank`; display name/cuisine/rating/cost **from repository only** | 200 | Assert name matches store |
| EC-LLM-14 | P0 | Parse fails entirely | Fallback: top-K by pre-LLM sort with generic explanation | 200 `meta.fallback_used=true` | Force parse fail |
| EC-LLM-15 | P1 | LLM explanation contradicts structured filters | Still show dataset truth; explanation is narrative only | 200 | Manual review |

**Architecture failure handling table (must implement):**

| Failure | Mitigation |
|---------|------------|
| API timeout | Retry once with backoff; then fallback ranking |
| Invalid JSON | Regex extract JSON block; else rating-based fallback |
| Unknown restaurant_id | Drop entry; log warning |
| Rate limit | Queue or cached result (optional) |

---

## 7. Recommendation Orchestrator

*Architecture: **Component Design → 7. Recommendation Orchestrator**, **Request Lifecycle***

| ID | Sev | Trigger | Expected behavior | HTTP / UI | Test |
|----|-----|---------|-------------------|-----------|------|
| EC-ORCH-01 | P0 | Valid preferences, empty candidates | Return `RecommendationResponse` with empty list; **no LLM call** | 200 empty | EC-FIL-01 integration |
| EC-ORCH-02 | P0 | UI/API calls orchestrator only | No direct UI → LLM path | N/A | Architecture review |
| EC-ORCH-03 | P1 | Concurrent requests | Stateless; shared read-only repository | 200 parallel | Load smoke |
| EC-ORCH-04 | P1 | Identical repeated requests | Optional cache (architecture optional); idempotent results acceptable | 200 | Repeat POST |
| EC-ORCH-05 | P2 | Partial LLM success (3 of 5 ids valid) | Return 3; optionally backfill to `top_k` from fallback | 200 | Mixed valid/invalid ids |

**Pipeline order (must not reorder):** validate → filter → (if empty return) → prompt → LLM → parse → merge → response.

---

## 8. API Design

*Architecture: **API Design***

| ID | Sev | Trigger | Expected behavior | HTTP / UI | Test |
|----|-----|---------|-------------------|-----------|------|
| EC-API-01 | P0 | Validation failure on POST `/api/v1/recommendations` | **400** with field errors | 400 | Invalid body |
| EC-API-02 | P0 | Store not loaded | **503** | 503 | Boot without ingest |
| EC-API-03 | P0 | LLM upstream hard failure (no fallback) | **502** | 502 | Mock unrecoverable |
| EC-API-04 | P1 | GET `/api/v1/health` | Liveness + dataset loaded flag | 200/503 | Health check |
| EC-API-05 | P2 | GET metadata locations/cuisines empty store | 503 or empty list per implementation | 503 | No data |
| EC-API-06 | P1 | Malformed JSON body | 400 | 400 | Invalid JSON |

**Response contract:** Include `meta.candidates_considered`, `meta.filters_applied` when matches exist.

---

## 9. Presentation Layer

*Architecture: **Presentation Layer**, **Component Design → 8. Output / Presentation Layer***

| ID | Sev | Trigger | Expected behavior | HTTP / UI | Test |
|----|-----|---------|-------------------|-----------|------|
| EC-UI-01 | P0 | User submits during LLM wait | Show loading spinner; disable double-submit | Spinner | Double-click |
| EC-UI-02 | P0 | Empty recommendations | Empty state message; suggest loosening rating/cuisine/location | Banner | EC-FIL-01 |
| EC-UI-03 | P0 | Validation error | Inline field errors; no stack trace | Form errors | EC-IN-* |
| EC-UI-04 | P0 | LLM failure with fallback | Show results + subtle “AI unavailable” notice | Banner | EC-LLM-06 |
| EC-UI-05 | P1 | `summary` present | Render above cards | UI | Happy path |
| EC-UI-06 | P1 | Streamlit rerun / refresh | Form state recoverable or clear | UX | Manual |
| EC-UI-07 | P2 | Very long explanation text | Wrap/truncate in card layout | UI | Long text |

**MVP stack (Technology Options — Option A):** Streamlit in-process; FastAPI+React is Option B (post-milestone).

---

## 10. Cross-Cutting Concerns

*Architecture: **Cross-Cutting Concerns***

| ID | Sev | Trigger | Expected behavior | HTTP / UI | Test |
|----|-----|---------|-------------------|-----------|------|
| EC-CFG-01 | P0 | Missing required env (`LLM_API_KEY` for live LLM) | Fallback or clear startup warning per config | Banner / log | No key |
| EC-CFG-02 | P0 | Invalid `MAX_CANDIDATES` | Default to safe value (e.g. 30) | N/A | Config test |
| EC-CFG-03 | P1 | Wrong `LLM_PROVIDER` | Fail fast at client init with message | 503/500 | Bad provider |
| EC-SEC-01 | P0 | User input used in filters | In-memory/parameterized only; **no SQL** from user strings | N/A | Security review |
| EC-SEC-02 | P0 | Secrets in repo | `.env` gitignored; never log API keys | N/A | Grep logs |
| EC-LOG-01 | P1 | Any recommendation request | Log filter count, LLM latency, parse success; correlation id | Logs | Request trace |
| EC-LOG-02 | P2 | Dev-only full prompt logging | Redacted; off in production | N/A | Env flag |

---

## 11. Goals and constraints (system-wide)

| ID | Sev | Constraint | Violation to avoid | Detection |
|----|-----|------------|-------------------|-----------|
| EC-G-01 | P0 | **Grounding** | Restaurant in output not in dataset | `test_grounding`: every id ∈ candidates |
| EC-G-02 | P0 | **Filter before generate** | LLM called before filter or on full catalog | Spy/mock call order |
| EC-G-03 | P0 | **Bounded context** | > `MAX_CANDIDATES` ids in prompt | Prompt snapshot |
| EC-G-04 | P0 | **Structured + generative** | LLM changes rating/cost/name in API response | Response merge tests |
| EC-G-05 | P1 | **Explainability** | Empty explanation on success path | Assert non-empty explanation |
| EC-G-06 | P2 | Out of scope: auth, live Zomato API, maps | Do not test as failures | N/A |

---

## 12. Request lifecycle (end-to-end scenarios)

| Scenario | Steps | Expected outcome |
|----------|-------|------------------|
| **Happy path** | Submit valid prefs → filter → LLM → parse → merge | `top_k` cards with summary; meta shows filters |
| **No candidates** | Strict filters → zero rows | Empty list; no LLM; UI empty state (sequence diagram `alt no candidates`) |
| **LLM degraded** | Valid candidates → LLM fails | Fallback rankings + template explanations |
| **Cold start** | First boot → ingest | Health OK; first recommend < latency budget for filter |
| **Demo without API key** | EC-LLM-06 | User still sees ranked restaurants |

---

## 13. Test matrix (maps to architecture Testing Strategy)

| Layer | Edge-case IDs | Test type |
|-------|---------------|-----------|
| SchemaNormalizer / Preprocessor | EC-ING-* | Unit |
| FilterService | EC-FIL-* | Unit |
| PromptBuilder | EC-PRM-* | Snapshot |
| ResponseParser | EC-LLM-02–05, EC-LLM-10 | Unit |
| RecommendationOrchestrator | EC-ORCH-*, EC-FIL-01, EC-G-* | Integration (mock LLM) |
| API routes | EC-API-* | Integration |
| E2E | Happy path + EC-FIL-01 + EC-LLM-06 | E2E / manual |

---

## 14. Optional extensions (not MVP — architecture Future Extensions)

| Enhancement | Related edge IDs | Notes |
|-------------|------------------|-------|
| Fuzzy location / city suggest | EC-IN-08, EC-FIL-08 | Architecture marks as **future** |
| Constraint broadening when zero matches | EC-FIL-01 | **Not** in architecture Filter table; if added, define explicitly |
| Response cache for identical preferences | EC-LLM-07, EC-ORCH-04 | LLM Integration — optional |
| Async job queue for long LLM | EC-UI-01 | High-Level Architecture — sync MVP |
| FastAPI + React (Option B) | EC-API-* | Technology Options |

---

## Document references

| Document | Role |
|----------|------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Source of truth for components and failure table |
| [context.md](./context.md) | Success criteria |
| [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) | Phase ownership of fixes |
| [EDGE_CASES.md](./EDGE_CASES.md) | This document |

---

*End of edge cases document.*
