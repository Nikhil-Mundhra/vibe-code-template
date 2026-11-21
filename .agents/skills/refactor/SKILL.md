---
name: refactor
description: Surgical code refactoring to improve maintainability without changing external behavior. Covers extracting functions, renaming variables, breaking down god functions, improving type safety, eliminating code smells, and applying design patterns. Use for gradual improvements.
---

# Refactor

## Overview

Improve code structure and readability without changing external behavior. Refactoring is gradual evolution, not rewriting from scratch.

## When to Use

Use this skill when:
- Code is hard to understand or maintain
- Functions or classes are too large
- Code smells need addressing
- User explicitly requests "clean up this code", "refactor this", or "improve this structure"

---

## MANDATORY PREREQUISITE: Test Coverage Requirement

> [!CAUTION]
> **NO REFACTORING WITHOUT ADEQUATE TESTS.**
> Refactoring preserves existing external behavior. Without automated test coverage, changes cannot be safely validated.
>
> 1. **Check for Tests**: Before modifying any implementation code, verify that adequate automated unit/integration tests exist for the target functions or modules.
> 2. **Refusal Protocol**: If adequate tests do NOT exist, **the agent MUST refuse to execute the refactoring request**.
> 3. **Remediation**: Inform the user that adequate tests must be written first. Offer to write or expand the test suite before proceeding with any refactoring.

---

## Golden Rules of Refactoring

1. **Behavior Preservation:** Refactoring changes only code structure, never functional behavior.
2. **Dual Verification (Tests + Strict Typecheck/Build):** Run both the automated test suite **and** the strict compiler/typechecker/build command (e.g., `tsc -b` / `npm run build`, `mypy`, `cargo check`) before starting, after every small incremental change, and upon completion. Transpile-only test runners (`vitest`/`esbuild`) strip types and silently ignore unused imports (`noUnusedLocals`, `noUnusedParameters`) or type drift left behind during file extraction.
3. **Small Steps:** Make tiny, localized changes; verify tests and build after each step.
4. **Focused Scope:** Do not mix feature additions, bug fixes, or behavioral changes with refactoring.

---

## Safe Refactoring Workflow

1. **PREPARE & VERIFY TESTS**
   - Confirm test suite and strict build/typecheck exist and are passing.
   - **Refuse to proceed if adequate tests are missing.**

2. **IDENTIFY & PLAN**
   - Identify specific code smells and target refactoring operations.
   - Plan minimal-impact structural changes and a clean dependency order before moving code.

3. **EXECUTE INCREMENTALLY**
   - Make one small change at a time (extract one layer or component/module per step).
   - Run unit/integration tests **and** strict type-checking/build immediately after each edit.
   - Fix any breakage or unused imports before moving to the next edit.

4. **VERIFY & CLEAN UP**
   - Ensure all automated tests pass with zero regressions.
   - Run the strict type-checker, production build, and linters.
   - Clean up remaining dead code, unused imports, or obsolete comments.

---

## Module Splitting & Architecture Rules

1. **Strict One-Way Dependency DAG**
   - When decomposing a large monolithic file into a sub-directory, extract bottom-up in a strict acyclic hierarchy so lower layers never import from higher layers:
     `types` → `constants` → `helpers` (pure functions) → leaf UI components / domain services → top-level coordinator.
   - Never allow leaf components, helpers, or constants to import from the coordinator entry file.

2. **Preserve Public Module Boundary (Re-Export Barrels)**
   - Moving types, constants, or helpers out of an entry module into sub-files must never break external imports or test files.
   - Keep the original entry file as a re-export barrel for every public symbol it previously exported (e.g., `export type { ... } from "./sub/types"`, `export { ... } from "./sub/constants"`, `export { ... } from "./sub/helpers"`).

---

## UI & React Monolith Refactoring Rules

1. **State Colocation (Push State Down)**
   - When extracting a UI section or modal from a "God Component", move local UI state (`isOpen`, active tab, filter controls, draft inputs, expansion toggles, copy timers) *inside* the extracted child component instead of prop-drilling state and setter callbacks from the parent.
   - Keep only shared cross-section domain state and callbacks in the top-level coordinator.

2. **Custom Hook Extraction**
   - Extract complex stateful async or side-effect orchestration (e.g., SSE/stream readers, multi-endpoint polling, keyboard navigation or focus managers) into dedicated hooks or helper functions when separating orchestration logic from JSX layout.

3. **DOM, Landmark & ARIA Invariants**
   - Preserve semantic HTML landmarks (`<main>`, `<nav>`, `<header>`, `<section>`, `<dialog>`), `role` attributes, `aria-labelledby`/`aria-controls` IDs, and keyboard/focus semantics exactly across extractions.
   - Component splits must leave accessibility behavior and DOM integration queries (`getByRole`, `within(main)`) unbroken.

---

## Index of Code Smells & Anti-Patterns

> **Need code examples & diffs?** Read [`references/code_smells_and_patterns.md`](./references/code_smells_and_patterns.md) for full before/after code snippets.

1. **Long Method/Function**: Function performing multiple duties. *Fix: Extract Method.*
2. **Duplicated Code**: Identical or near-identical logic repeated in multiple places. *Fix: Extract Function/Module.*
3. **Large Class/Module (God Object)**: Class/module managing too many unrelated responsibilities. *Fix: Single Responsibility Principle / Extract Class.*
4. **Long Parameter List**: Functions taking too many arguments. *Fix: Introduce Parameter Object / Options struct.*
5. **Feature Envy**: Method accessing another object's internal data more than its own. *Fix: Move Method to owner object.*
6. **Primitive Obsession**: Using raw primitives (strings, numbers) for rich domain concepts. *Fix: Value Objects / Enums.*
7. **Magic Numbers/Strings**: Hardcoded literal values without semantic naming. *Fix: Replace Magic Number with Constant.*
8. **Nested Conditionals (Arrow Anti-Pattern)**: Deeply nested `if/else` cascades. *Fix: Guard Clauses / Early Returns.*
9. **Dead Code**: Unused functions, parameters, or commented-out blocks. *Fix: Delete completely.*
10. **Inappropriate Intimacy**: Classes tightly coupling to each other's internal state. *Fix: Encapsulation / Law of Demeter.*
11. **God Component & Prop Drilling**: Giant UI component holding unrelated section/modal state and passing setters down. *Fix: State Colocation + Section/Modal Extraction.*
12. **Tangled File Split / Broken Imports**: Splitting a large file with circular imports or broken caller imports. *Fix: One-Way Dependency DAG + Re-Export Barrel.*
13. **Inline Async Orchestration in UI**: Heavy streaming/fetch loops mixed directly with presentational JSX. *Fix: Extract Custom Hook / Controller.*

---

## Refactoring Operations & Design Patterns Index

| Operation / Pattern | When to Apply | Full Examples Link |
|---|---|---|
| **Extract Method / Function** | Break up long methods into focused single-purpose helpers | [View Diff](./references/code_smells_and_patterns.md#1-long-methodfunction) |
| **Extract Class / Module** | Split monolithic classes into single-responsibility services | [View Diff](./references/code_smells_and_patterns.md#3-large-classmodule) |
| **Introduce Parameter Object** | Combine 4+ parameters into a structured type | [View Diff](./references/code_smells_and_patterns.md#4-long-parameter-list) |
| **Guard Clauses / Early Returns** | Flatten nested conditional pyramids | [View Diff](./references/code_smells_and_patterns.md#8-nested-conditionals) |
| **Strategy Pattern** | Replace branching conditional logic with interchangeable strategies | [View Diff](./references/code_smells_and_patterns.md#strategy-pattern) |
| **Introduce Type Safety / Value Objects** | Replace raw strings/numbers with typed value wrappers | [View Diff](./references/code_smells_and_patterns.md#6-primitive-obsession) |
| **Colocate State (Push State Down)** | Move local modal/tab/filter state out of a God Component into extracted child components | [View Diff](./references/code_smells_and_patterns.md#11-god-component-and-prop-drilling) |
| **Split Module with One-Way DAG + Re-Export Barrel** | Decompose large files bottom-up while preserving existing caller and test imports | [View Diff](./references/code_smells_and_patterns.md#12-monolithic-file-split) |
| **Extract Custom Hook** | Isolate complex async, streaming, or DOM event state from JSX components | [View Diff](./references/code_smells_and_patterns.md#13-inline-async-orchestration-in-ui) |
| **Inline Method / Class** | Remove unnecessary abstraction when logic is simple | [View Reference](./references/code_smells_and_patterns.md#common-refactoring-operations) |
| **Replace Conditional with Polymorphism** | Replace switch/if cascades with object dispatch | [View Reference](./references/code_smells_and_patterns.md#common-refactoring-operations) |

---

## Refactoring Checklist

- [ ] Automated tests cover the code under refactor and are passing
- [ ] Code smell identified and matched to target refactoring operation
- [ ] Functions and UI components are focused and do one thing well
- [ ] Local UI state is colocated inside extracted components (no unnecessary prop-drilling)
- [ ] Split modules follow a strict one-way dependency DAG (`types` → `constants` → `helpers` → leaves → coordinator)
- [ ] Original entry file re-exports moved public types, constants, and helpers (barrel preserved)
- [ ] Semantic landmarks, ARIA attributes, and focus/keyboard behavior are preserved
- [ ] Duplicate code is eliminated
- [ ] Variable, function, and class names clearly convey intent
- [ ] Magic numbers and strings are replaced with named constants
- [ ] Unused (dead) code, unused imports, and obsolete comments are removed
- [ ] Both automated tests **and** strict type-checker/build/linters pass after refactoring

---

## Detailed References

For comprehensive examples of code smells, design patterns, and standard refactoring operations, open and read:
- [`references/code_smells_and_patterns.md`](./references/code_smells_and_patterns.md)
