---
name: edge-case-review
description: >-
  Systematic edge-case review framework, 20-point product/UX catalog, layer-by-layer engineering
  checklist, risk × discoverability prioritization, and QA spec-readiness rules for PRDs, UI states,
  APIs, databases, background jobs, and algorithms. Trigger BEFORE coding a complex feature/spec
  (Mode A), when auditing existing endpoints/UI flows or git diffs for failure modes and writing
  failing tests (Mode B), or when stress-testing pure functions, schemas, and data pipelines (Mode C).
  Pairs with data-quality-and-contract-testing and quality-assurance.
---

# Edge-Case Review & Pre-Coding Checklist

An edge case is a condition at a boundary or outside a product's usual happy path—valid or invalid input, missing data, wrong-state transitions, timing issues, permission changes, concurrency, or dependency failures at the worst moment.

> **Core Rule:** Every edge case needs three things: **what happens**, **the mitigation**, and **the test that fails if the mitigation is removed**. A case without a test is a wish.

Choose edge cases by asking *what failures the architecture makes possible* (not random brainstorming), focusing on failures that are expensive, hard to discover, or likely to be missed.

---

## 1. Agent Execution Protocol (Mode Routing)

Before auditing, classify the target and apply only the relevant checklists (never force-fit UI/tab/session checks onto pure backend or algorithmic code):

1. **Mode A — PRD / Spec / Design Review (Pre-Coding):**
   * Run the **QA Spec-Readiness Gate (Section 6)** first to catch vague prose, missing status codes, or implicit setup.
   * Walk the **20-Point Catalog (Section 2)** and **Frontend/Contract/Rollout Checks (Section 4)**.
   * Output the **Audit Matrix** + full **Specification Cards (Section 6)** for the top release-blocking risks.
2. **Mode B — Full-Stack / UI / API Endpoint Review (Code or PR):**
   * Trace actual entry points, state mutations, auth checks, and external calls in the codebase first (`file:line`).
   * Walk **System Layers (Section 3)**, **API Contract & Skew (Section 4)**, and **Boundary Probes (Section 6)**.
   * Output findings tied to exact code locations + concrete unit/integration/E2E test cases.
3. **Mode C — Pure Function / Data Pipeline / Algorithm Review:**
   * Skip UI, session, and popup checks. Focus on **Input Boundaries, Type-Specific Probes, Invariants, Concurrency, and Scale (Sections 3 & 6)**.
   * Identify the core invariant and construct minimal inputs that violate it.

### High-Leverage Invocation Patterns & Skill Chaining
* **Pre-Coding Spec Stress-Test (Mode A):** Run on a PRD or implementation plan *before* writing code—flag Section 7 Spec-Readiness Gate violations first, then output the Audit Matrix and P0 Specification Cards.
* **Code / Diff Audit → Direct to Failing Tests (Mode B):** Run on a target module or `git diff`, then immediately implement the top 5 prioritized failing tests (Part 3) and the defensive guards to make them pass.
* **Skill Chaining:** Pair Mode C findings with `data-quality-and-contract-testing` to turn input/null/Unicode traps into schema contracts, or hand the Part 3 Architecture Test Map to `quality-assurance` to scaffold the test suite.

---

## 2. The 20-Point Product & UX Catalog (Across 8 Discovery Categories)

Walk every applicable category against the flow under review:

### A. Input & Validation Boundaries
1. **Empty required input:** Blank or whitespace-only required field. Prevent submission and explain exactly what to fix.
2. **Maximum-length input:** Value far exceeds mockup or schema length. Verify validation, truncation, wrapping, and downstream rendering.
3. **Unexpected characters & encoding:** Emoji (4-byte Unicode), non-Latin/RTL scripts, punctuation, or pasted rich text. Explicitly specify whether length limits count code points, UTF-16 units, or bytes.

### B. Concurrency, Idempotency & Uniqueness
4. **Duplicate action:** Double-click Submit or retry after a slow response. Enforce idempotency keys so duplicate orders, invites, payments, or records are never created.
5. **Concurrent editing:** Answer three questions when two users (or two tabs/workers) submit within 100ms:
   * **Who wins:** last write, first write, or conflict (`409`) returned to both?
   * **What the loser sees:** silent overwrite, error banner, or merge screen?
   * **How the loser's screen catches up:** immediate refresh, live subscription, polling, or reload?

### C. Network, Latency & Partial Failure
6. **Network drops during save:** Connectivity disappears mid-request.
   * *Acceptance check:* A lost response does not prove failure. Preserve drafts safely, check the server's recorded outcome on reconnect, make retries idempotent (at most one record created), and report the confirmed result.
7. **Slow API response:** Dependency stalls (e.g., 30s vs. 300ms). Provide explicit loading state, timeout behavior, and recovery instead of an indefinite spinner.
8. **Partial success & recovery:** Multi-step or batch action partially succeeds (e.g., 3 of 5 uploads succeed, or account created but welcome email fails).
   * *Acceptance check:* Show per-item status and offer targeted retry (*Retry failed only*) that leaves completed work intact and never duplicates it. Ensure rollback never leaves inconsistent data.
9. **User goes offline:** Define what stays readable, what is disabled, and how state reconciles on reconnect.

### D. State Transitions, Sessions & Navigation
10. **Wrong-state transitions:** Actions attempted from loading, empty, partial, stale, or completed status (e.g., double cancel, re-activation, acting while pending).
11. **Session expires during a task:** Auth expires while a form or workflow is open.
    * *Acceptance check:* Preserve entered work only within data-handling policy. After re-login, confirm the same account, workspace, and current permission before saving; block and explain if changed, and never expose drafts to another account.
12. **Account changes in another tab:** Sign-out, account switch, or workspace switch in Tab B must invalidate stale identity/permissions in Tab A.
13. **Back button after a one-time action:** Prevent unsafe replay of completed checkout, payment, or final submission.

### E. Permissions & Authorization
14. **Permission is revoked mid-session:** Enforce server-side authorization on **every** request (OWASP). Remove unavailable controls, ensure stale tabs cannot read or mutate restricted data, leave the resource unchanged on rejection (`403`), and explain how to request access.
15. **Role changes while the page is open:** Admin becomes viewer (or vice versa). Verify control visibility, cached data exposure, and clear feedback.
16. **Expired invitation or magic link:** Explain clearly (`410 Gone` for reused reset/invite links) and provide a direct way to request a fresh link.

### F. Scale, Quota & Time Boundaries
17. **Zero-data state:** Explain why it is empty and surface the primary action to create the first useful result.
18. **Extremely large dataset:** Verify pagination, filtering, sorting, exports, bulk actions, and render performance at 20,000+ rows.
19. **Resource limit reached:** Seat, storage, API, or usage quota hit mid-workflow. Show the exact limit and permitted next step; verify no partial/corrupt record is created, existing data stays intact, and retry works once capacity is freed.
20. **Time-zone, DST & calendar edges:** Store and display timestamps unambiguously (UTC+13 vs. UTC−12); verify jobs scheduled during DST skipped/repeated hours do not run twice or get skipped; handle Feb 29 and varying month lengths without silent date drift.

---

## 3. Edge Cases Across System Layers & High-Risk Domains

Assign each edge case to its owning layer so the right engineer writes the test:

| Layer | What to Audit |
| :--- | :--- |
| **UI** | Double-clicks, stale tabs, back-button replay, expired sessions, long strings, empty/loading/partial states. |
| **API** | Malformed JSON, missing required headers, oversized payloads (`413`), unexpected `Content-Type`, idempotency keys. |
| **Service** | Dependency unavailability (`503`), timeouts, retry storms, circuit-breaker states, cache invalidation timing. |
| **Database** | Unique constraint violations, foreign-key failures on delete, transaction isolation levels, migration rollback safety. |
| **Background Jobs** | Queue backup under load, duplicate execution on failed ack, worker crash mid-job, poison messages, dead-letter queues. |
| **Storage / Files** | Expired signed URLs, partial upload cleanup, size at `limit` vs. `limit + 1 byte`, content-type spoofing (inspect bytes, not extension). |

### High-Risk Domain Patterns
* **Payments:** `amount = 0.00` (reject before gateway); currency mismatch (`400`, no charge); gateway timeout after charge initiated (record ambiguous state, trigger reconciliation, return `503` with retryable flag); duplicate attempt within 10s (return original receipt, no second charge).
* **Authentication & Approvals:** Expired token after grace window (`401`, not `403`); valid token for deactivated account (`403` with `account_suspended`); password reset link reuse (`410 Gone`); **bind approval tokens to the exact target resource/path server-side** so an approval for `/a` is rejected (`403`) on `/b`.
* **Files, Paths & Data Integrity:** Size at `limit` accepted vs. `limit + 1 byte` (`413`); content-type spoofing rejected by byte inspection; path traversal (`..`) refused and slashes normalized (`//a//b/` ≡ `/a/b`) before auth checks; **never allow saving a truncated document/payload** (mark read-only to prevent silent data destruction); use clock-skew-safe version tokens (ID + hash/size, not timestamps); write local drafts *before* firing network saves and handle `localStorage` quota exhaustion with oldest-first eviction.
* **Accessibility, Locale & Rendering:** IME composition (CJK) and dead keys (`⌥e` → `é`), 200% zoom without clipped controls, forced-colors & dark-mode contrast, `prefers-reduced-motion`, zero focus traps, and `0.0000` CLS on mount.

---

## 4. Frontend, API Contract, Mockup & Rollout Checklist

Use these targeted checks during design and API contract reviews to catch UAT show-stoppers early:

* **API Contract Coordination:**
  * *Prerequisite data:* Is all required request data already on the client, or does it require chained GET calls?
  * *Multi-API failures:* If 1 of 3 GETs fails, show partial content, inline alert, or full error? If a multi-step POST fails partway, do GET + PATCH counterparts exist so retry skips completed calls?
  * *Null vs. omitted:* How does the API treat `null`, `""`, or `{}` vs. an omitted field? Is there a consistent error shape and feature-level error isolation (no full-app crash on unexpected errors)?
  * *Lifecycle state API:* Can the client query whether the user is in the *initial*, *in-progress*, or *completed* state?
* **Design Mockups & Device Reality:**
  * *Touch & mobile:* Critical info hidden in hover-only tooltips; virtual keyboard covering primary CTAs; absolutely positioned illustrations overlapping buttons on narrow screens.
  * *Interactive & gate states:* Explicit hover/focus/active states, keyboard navigation (Tab + Enter submit), validation timing (`onChange` vs. `onBlur` vs. `onSubmit`), server-side validation error placement, and prerequisite verification gates (email/phone verification).
* **Product Behavior & Multi-Step Flows:**
  * *Popups & dismissals:* Coordination/priority when two features trigger popups simultaneously; persisting dismissals (e.g., "X" button or celebration banners) server-side instead of `localStorage` so they hold across devices; hiding entry promo cards once the user reaches the end state.
  * *Multi-step wizards:* Out-of-order navigation, editing an earlier step (does it invalidate later steps?), exiting mid-flow (checkpoint restoration), and exiting mid-request (cancel vs. finish in background without jarring notifications).
* **Deployment Skew & Client Hygiene:**
  * *Client/server skew:* During a staggered rollout (e.g., 40-minute gap), verify **new server + old client** and **old server + new client** both keep working.
  * *`localStorage` deprecation:* Version or namespace keys so removed keys don't collide with future features on stale clients.
  * *Rollout & performance:* Feature-flag removal path, analytics/attribution events, client bundle-size impact, and third-party SaaS latency/privacy impact.

---

## 5. Prioritization: Risk × Discoverability & Release-Blocking Rules

Prioritize using **consequence (risk)** × **ease of detection in QA/monitoring (discoverability)**:

| | **Low Discoverability** | **High Discoverability** |
| :--- | :--- | :--- |
| **High Risk** | **P0 — Document & test before coding:** payment conflicts, concurrent writes, permission bypass, silent data corruption. | **P1 — Document & add monitoring:** performance degradation, third-party outages, schema validation failures. |
| **Low Risk** | **P2 — Document as out-of-scope with rationale:** cosmetic rendering edges, non-default locale formatting. | **P3 — Note, do not block:** minor validation errors with clear user copy. |

### Release-Blocking Policy
* **Blocks release:** money movement can duplicate or disappear; a permission boundary can be bypassed; user data can be overwritten without warning; a retry can trigger a second irreversible action; support cannot identify the failed state in logs.
* **Can ship as documented risk:** cosmetic copy mismatch; rare timing issue with zero data loss; non-critical notification delayed with a clear retry path; admin-only workflow with a manual workaround.

---

## 6. Writing Testable Edge Cases & Required Output Format

### Structural Rules
1. **Three error paths for every happy path:** Document **Validation** (`400`/`422`), **Authorization** (`401`/`403`), and **Downstream Dependency Failure** (`503`/timeout) with exact HTTP status codes and UI copy.
2. **Write failures as scenes, not nouns:** Replace *"Interrupted upload"* with *"A 200 MB file on a slow connection drops at 80% and the browser refreshes."*
3. **Describe behavior, not implementation:** Specify *"retries up to 3 times"* rather than internal data structures.
4. **End in an observable outcome:** API response, UI state, DB row, or a named audit log entry.
5. **Name a shared test fixture** (e.g., `duplicate-pay-now.json`) so API, UI, log, and DB assertions reuse the same input.

### Six Input Boundary Values & Type-Specific Probes
Test every input against: **empty**, **1 (minimum)**, **max**, **max + 1**, **negative** (if numeric), and **4-byte Unicode/emoji**. For an integer range `[1, 10]`, test `0, 1, 2, 9, 10, 11` plus blank, non-numeric, and fractional inputs.

Apply targeted probes by data type and structure:
* **Numeric & falsy traps:** `0` failing truthiness checks (`if x:` vs. `if x is not None:`), `NaN`, `Infinity`/`-Infinity`, `MAX_SAFE_INTEGER`, overflow, and ties/equal-value sorting stability.
* **Strings & injection:** RTL text (e.g., Arabic), SQLi (`' OR 1=1 --`), XSS (`<script>alert(1)</script>`), null bytes/control characters, and type-coercion strings (`"null"`, `"undefined"`, `"true"`, `"123"`).
* **Collections & nulls:** `null`/`None` vs. empty container (`[]`/`{}`), `null`/`undefined` elements *inside* a collection, all-identical values, duplicates at first/last boundary positions, reverse-sorted input, and partially populated objects.
* **Graphs, loops & invariants:** State the core **invariant** (what must *always* stay true) and pick 3–5 inputs specifically to break it; check cycles, self-loops, disconnected components, deep recursion, and loop/retry termination on duplicates.
* **Authorization & IDOR (mandatory for every API):** Unauthenticated request, accessing another user's resource, accessing a deleted/expired resource, and privilege escalation by passing someone else's ID in the request body.
* **External dependencies:** Unexpected response shape (e.g., array instead of string, missing key), timeout, `503`, DB constraint violation, and full/read-only disk.

### Unit-Test & Property-Test Hygiene
* Name tests by **behavior**, not internal implementation; use **minimally passing inputs** that isolate one behavior.
* **Avoid logic (`if`/loops) inside test bodies**—use parameterized test cases instead.
* Not every edge case needs a dedicated test; some are best handled with a single defensive guard at the function boundary.
* **Round-trip & parity properties:** Assert `deserialize(serialize(x)) ≡ x` and `apply(diff(base, target), base) ≡ target`. When validation or security rules exist in two languages (e.g., TypeScript UI + Python API), run a shared corpus test asserting identical verdicts at build time.

### Required Audit Output Format

Structure every `/edge-case-review` output in three parts:

#### Part 1: Compact Edge-Case Audit Matrix
Group all discovered edge cases by severity (`Critical [Blocks Release]`, `High`, `Medium`, `Out of Scope`):

| Severity & Layer | Failure Scene (Trigger & State) | Required Mitigation (Behavior & Status/Copy) | Failing Test / Observable Assertion |
| :--- | :--- | :--- | :--- |
| **Critical** (API / DB) | *User double-clicks Pay Now within 100ms on unpaid `$49` invoice* | Enforce idempotency key; 1 charge attempt; second call returns existing `attempt_id` | Concurrent POST test asserts 1 ledger row and identical `attempt_id` (`duplicate-pay-now.json`) |

#### Part 2: Deep Specification Cards (Top 3–5 Release-Blocking / P0 Cases Only)
Expand only the highest-risk items (`High Risk × Low Discoverability`) into full cards:

| Field | Specification |
| :--- | :--- |
| **Scenario** | *e.g., Duplicate Pay Now click on unpaid invoice* |
| **Layer & Owner** | API / Payments engineer + QA reviewer (`file:line` if auditing code) |
| **Start state & input** | Logged-in user, 1 unpaid `$49` invoice, same `invoice_id` submitted twice within 60s |
| **Trigger (When)** | User clicks Pay Now twice (or retries after 30s timeout) |
| **Expected UI** | Single "Payment pending" banner; no duplicate confirmation |
| **Data & API behavior** | Reuses original idempotency key; 1 gateway charge attempt; second call returns existing `attempt_id` |
| **Recovery action** | Poll or refresh confirmed status; support locates pending payment by `order_id` in audit log |
| **Evidence & fixture** | Ledger has 1 pending row; `duplicate-pay-now.json` |
| **Release rule** | **Blocks release** |

#### Part 3: Top 5–7 Prioritized Test Cases (and Architecture Test Map for Large Features)
List the exact automated tests to write first (ordered by `Risk × Discoverability`), plus a `Group | Harness | Location | Gate` table when auditing multi-layer features.

---

## 7. QA Spec-Readiness Gate & Definition of Done

### Send the Spec Back When You See:
* Edge cases written as prose instead of criteria (*"Handle expired sessions gracefully"*).
* Error paths missing status codes or exact user copy (*"Show an error"*).
* A whole category missing (e.g., no concurrency section on shared state).
* Adjectives standing in for numbers (*"fast"*, *"reasonable"*, *"significant"*).
* Implicit setup (missing data, permissions, feature flags, timing, or network state).

**5-Minute Readiness Check:** Pick one edge case and try to write the QA test without opening code or asking anyone. If you cannot state the exact input, trigger, and assertion, the spec owes another sentence.

### Definition of Done
* Every high-risk edge case has a mapped automated/QA test case.
* Retry, idempotency, and partial-failure behaviors are documented and verified.
* Production alerts exist for high-risk edge-case regressions.
* Rollback does not create inconsistent data states.
