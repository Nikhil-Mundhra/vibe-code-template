---
name: github-issues
description: End-to-end toolkit for agents to inspect, audit, verify against codebase and git history, and safely close GitHub issues. Use when triaging issues, checking milestone/track progress, verifying requirements, running audit matrices, or closing completed issues.
---

# GitHub Issues Audit and Resolution Toolkit

## Overview

A deterministic, evidence-based toolkit for AI agents to audit, verify, and resolve GitHub issues. Prevents premature closure, hallucinated completions, and untracked changes by enforcing git archaeology, codebase validation, and test suite execution before closing any issue.

---

## When to Use

Activate this skill when:
- Triaging open GitHub issues across a repository, track, or milestone.
- Auditing whether an issue's scope and acceptance criteria are satisfied in the current working tree.
- Deciding which issues in a split/work-plan issue (e.g. tracks, phases) can be closed.
- Generating a verifiable audit report linking issues to commits and files.
- Closing GitHub issues with traceable resolution summaries and commit references.

---

## The 6-Phase Issue Resolution Protocol

```
+------------------+     +------------------------+     +-------------------------+
| 1. Discovery     | --> | 2. Requirements        | --> | 3. Git & Codebase       |
|    & Triage      |     |    Extraction          |     |    Archaeology          |
+------------------+     +------------------------+     +-------------------------+
                                                                     |
                                                                     v
+------------------+     +------------------------+     +-------------------------+
| 6. Traceable     | <-- | 5. Audit Matrix &      | <-- | 4. Automated            |
|    Closure       |     |    Verdict Synthesis   |     |    Verification Gate    |
+------------------+     +------------------------+     +-------------------------+
```

### Phase 1: Discovery & Triage

1. **List Open Issues**:
   Fetch current open issues with labels and update timestamps.
   ```bash
   gh issue list --state open --limit 50
   ```
   Or using the bundled auditor:
   ```bash
   .agents/skills/github-issues/scripts/issue-auditor.py list --state open
   ```

2. **Identify Orchestration / Meta-Issues**:
   Look for work-plan, track partition, or milestone issues that group related tasks (e.g. `Split: 3-developer work plan for #5-#15`).
   Run track extraction:
   ```bash
   .agents/skills/github-issues/scripts/issue-auditor.py tracks <meta_issue_id>
   ```

3. **Check Dependencies & Blockers**:
   Inspect whether the target issue is marked as blocked by another issue or unresolved architectural decision.

---

### Phase 2: Requirements & Deliverables Extraction

Inspect each target issue thoroughly before looking at code:
```bash
gh issue view <issue_id>
```
Or:
```bash
.agents/skills/github-issues/scripts/issue-auditor.py inspect <issue_id>
```

Extract four distinct lists:
1. **Target Artifacts**: Explicit file paths, folders, contracts, or routes mentioned (e.g., `rules/src/profiling.rule.ts`, `contracts/src/`).
2. **Behavioral Scope**: Required functional logic, constants, algorithms, or UI views.
3. **Acceptance Criteria**: Checkbox tasks (`- [ ]`), test expectations, locale requirements, or benchmark gates.
4. **Research / Citation Requirements**: Citations, papers, modeling sources, or competitor/judge literature checks.

---

### Phase 3: Git & Codebase Archaeology

Never assume an issue is open because work has not started, nor that an open issue is done without inspecting the commit trail.

1. **Commit Log Search**:
   Search for commits referencing the issue number:
   ```bash
   git log --grep="#<issue_id>" --oneline -n 10
   ```
   Search for commits matching the domain keywords:
   ```bash
   git log --grep="<keyword>" --oneline -n 10
   ```

2. **Inspect Commit Contents**:
   Verify what changes were actually committed:
   ```bash
   git show --stat <commit_hash>
   ```

3. **Workspace File Validation**:
   Confirm that all files declared as deliverables actually exist in the working directory:
   - Check file presence.
   - Inspect key functions, constants, or type definitions.
   - Verify that citations or comments required by the issue are present.

---

### Phase 4: Automated Verification Gate

Every candidate for closure must pass the repository's verification gates. Do not accept untested code.

1. **Typecheck Verification**:
   ```bash
   npm run typecheck
   ```
   Ensure zero TypeScript diagnostic errors across all workspace packages.

2. **Automated Test Suites**:
   Run full unit and integration tests:
   ```bash
   make test
   # Or workspace-specific:
   npm test --workspace=backend
   npm test --workspace=frontend
   ```

3. **Documentation & Drift Linting**:
   If the repository has doc-drift or docs-lint checks:
   ```bash
   make docs-lint
   ```

4. **Working Tree Cleanliness**:
   ```bash
   git status
   ```
   Ensure no untracked regressions or broken uncommitted files.

---

### Phase 5: Audit Matrix & Verdict Synthesis

Compile a structured evidence matrix before presenting to the user or closing on GitHub:

| Requirement / Scope Item | Code Implementation (File & Lines) | Commit Hash | Test / Gate Status |
|---|---|---|---|
| Domain Rules / Constants | `rules/src/<rule>.ts` | `c1b2dc5` | Unit test passed |
| Shared Zod Contract | `contracts/src/<module>/...` | `c1b2dc5` | Typecheck passed |
| Frontend Component / View | `frontend/src/features/...` | `58438ca` | UI component test passed |
| Source Citations | `docs/implementation-plan.md` | `c1b2dc5` | Docs lint passed |

Assign one of three verdicts:
- **READY_TO_CLOSE**: Every acceptance criterion is satisfied in the codebase, tests pass, and commits are on main.
- **INCOMPLETE**: Code exists but is missing specific deliverables, edge cases, tests, or documentation.
- **BLOCKED**: Implementation is waiting on an open upstream dependency or decision issue.

---

### Phase 6: Safe & Traceable Closure

When closing issues, always provide an audit-proof resolution comment specifying the exact commit hashes and deliverables.

1. **Closure Standards**:
   - Reference the exact commit hash(es) where the work landed.
   - List the key deliverables added or modified.
   - Note test passing status.
   - Never use emojis in comments, commits, or documentation.

2. **Execution Command**:
   ```bash
   gh issue close <issue_id> --comment "Completed in commit <hash>: <summary of delivered artifacts and verification>."
   ```
   Or via the script:
   ```bash
   .agents/skills/github-issues/scripts/issue-auditor.py close <issue_id> --comment "Completed in commit <hash>: <summary>."
   ```

3. **Post-Closure Verification**:
   Confirm the issue status flipped to `CLOSED`:
   ```bash
   gh issue view <issue_id> --json state
   ```

---

## Bundled CLI Tool Reference (`issue-auditor.py`)

The bundled Python script automates the inspection, cross-referencing, and verification workflow.

### Location
`.agents/skills/github-issues/scripts/issue-auditor.py`

### Commands

| Command | Usage | Description |
|---|---|---|
| `list` | `issue-auditor.py list [--state open/closed/all] [--limit N]` | Formats open or closed issues in a clean table |
| `inspect` | `issue-auditor.py inspect <issue_id>` | Parses files, checklists, and metadata from issue body |
| `tracks` | `issue-auditor.py tracks <meta_issue_id>` | Extracts tracks/phases and constituent issues from a split issue |
| `audit` | `issue-auditor.py audit <issue_id> [--run-typecheck] [--run-tests] [--json]` | Cross-references issue with git, checks file existence, tests, and emits verdict |
| `close` | `issue-auditor.py close <issue_id> --comment "<comment>"` | Closes issue with structured audit comment |

---

## Anti-Patterns to Avoid

- **No Ghost Closures**: Never close an issue based solely on a PR title or verbal claim. Always verify files on disk and check git logs.
- **No Vague Comments**: Comments like "Done" or "Fixed" provide no audit trail. Always cite commit hashes and file paths.
- **No Skipped Test Gates**: If `make test` or `npm run typecheck` fails, the issue is not ready to close.
- **No Policy Violations**: Strictly adhere to repository conventions (e.g. no emojis, kebab-case file naming, dependency boundaries).
