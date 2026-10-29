# vibe-code-template

A universal, agentic repository template pre-configured with 36 battle-tested agent skills, disciplined engineering principles, and automated onboarding workflows.

Designed for AI coding agents and engineers to rapidly initialize clean, high-velocity projects without starting from an empty directory.

---

## Quick Start for Agents

When an AI agent is initialized in a new project using this template, consult:
1. [`AGENTS.md`](AGENTS.md) — Canonical agent directives, communication rules, and runtime guardrails.
2. [`INITIAL_AGENT_INSTRUCTIONS.md`](INITIAL_AGENT_INSTRUCTIONS.md) — Initial onboarding checklist:
   - **Step 1:** Classify project type and trim the skill suite (`python3 scripts/trim_skills.py --preset <type>`).
   - **Step 2:** If the project requirements are complex, research an online template (<10k commits) and curl download it.
   - **Step 3:** Update this README with the list of removed skills.
   - **Step 4:** Reference the visual aesthetic archetypes (particles, Delaunay, topography, 3D WebGL) in [`INITIAL_AGENT_INSTRUCTIONS.md`](INITIAL_AGENT_INSTRUCTIONS.md) when building frontend/creative interfaces.

---

## Automated Skill Trimming

The template includes an automated skill trimmer located in `scripts/trim_skills.py`.

```bash
# View all available skills and categories
python3 scripts/trim_skills.py --list

# Apply a preset (minimal, web-app, deep-learning, data-engineering)
python3 scripts/trim_skills.py --preset web-app

# Or selectively keep specific skills
python3 scripts/trim_skills.py --keep refactor,quality-assurance,graphify,docmancer,glassmorphism-ui

# Or selectively remove unneeded skills
python3 scripts/trim_skills.py --remove totalsegmentator,kaggle,esf-audit-verification
```

`trim_skills.py` will delete the unneeded `.agents/skills/<name>` directories and automatically regenerate the Active vs. Removed skills tables below.

---

## Active Skills

<!-- BEGIN_ACTIVE_SKILLS -->

| Skill Name | Category | Description |
| :--- | :--- | :--- |
| `cnn-unet-architect` | Deep Learning & Medical Computer Vision | Architectural specifications, tensor dimension contracts, mathematical loss formulations, and design rules for building U-Net and deep CNN models. |
| `cohort-dataset-splitting` | Deep Learning & Medical Computer Vision | Clinical ophthalmic OCT dataset auditing, QC outlier filtering, and zero-leakage stratified train/validation cohort splitting. |
| `competence50-course-builder` | Specialized Domain, Auditing & Demos | Scaffolds, manages, or validates the 5-module Competence 5.0 course structure with the 3 content lanes. |
| `data-lake-and-zone-architecture` | Enterprise Data Engineering & Lakehouse | Guides agents through data lake and zone architecture design across raw, refined, curated, and publish layers. |
| `data-quality-and-contract-testing` | Enterprise Data Engineering & Lakehouse | Drives data implementation with contracts, assertions, and validation evidence before publishing. |
| `data-reconciliation-and-financial-controls` | Enterprise Data Engineering & Lakehouse | Guides agents through reconciliation and control design for business-critical and financial data. |
| `dct-tourism-hackathon-reviewer` | Specialized Domain, Auditing & Demos | Review, score, and improve submissions for the Advanced Technology Pioneers 2026 DCT challenge. |
| `diagnose-model-health` | Deep Learning & Medical Computer Vision | Runs a strict, predefined battery of diagnostic tests against a model checkpoint to verify network health. |
| `docmancer` | Codebase & Documentation Navigation | Query local context, fetch public documentation, and retrieve API references using the docmancer CLI. |
| `document-manipulation` | Publishing, Diagrams & Content Polish | Toolkit for manipulating documents including docx to mdx/html conversions and markdown to PDF. |
| `duckdb-local-analytics-and-dev` | Enterprise Data Engineering & Lakehouse | Guides agents through DuckDB-based local analytics and rapid development workflows. |
| `esf-audit-verification` | Specialized Domain, Auditing & Demos | Audits, tests, and verifies ESF+ compliance data in Competence 5.0 LMS. |
| `feature-store-and-ml-data-pipelines` | Enterprise Data Engineering & Lakehouse | Guides agents through machine-learning data pipelines and feature serving workflows. |
| `file-and-partner-feed-ingestion` | Enterprise Data Engineering & Lakehouse | Guides agents through file-based and partner-feed ingestion workflows with quarantine mechanisms. |
| `github-issues` | Core Quality & Refactoring | End-to-end toolkit for agents to inspect, audit, verify against codebase and git history, and safely close GitHub issues. |
| `glassmorphism-ui` | Frontend, UI/UX & Design Systems | Framework-agnostic rules for building frosted-glass (glassmorphism) interfaces and backdrop filters. |
| `graphify` | Codebase & Documentation Navigation | Use for questions about a codebase, architecture, file relationships, or project content via knowledge graph. |
| `greeting-demo` | Specialized Domain, Auditing & Demos | Greet the user in a distinctive, easy-to-verify format for skill activation demos. |
| `humanizer` | Publishing, Diagrams & Content Polish | Rewrite AI-sounding text so it reads naturally without changing what it says. |
| `kaggle` | Deep Learning & Medical Computer Vision | Mandatory skill for deploying, writing, running, or debugging model training scripts on Kaggle. |
| `klara-suggestions` | Frontend, UI/UX & Design Systems | Guidelines and architectural rules for debugging, modifying, or extending Klara Suggestion Cards. |
| `macbook-cnn-training` | Deep Learning & Medical Computer Vision | Execution rules, DataLoader worker limits, and Unified Memory management for PyTorch on Apple Silicon. |
| `master-data-and-entity-resolution` | Enterprise Data Engineering & Lakehouse | Guides agents through master data and entity resolution workflows and deduplication. |
| `notebook-to-production-hardening` | Enterprise Data Engineering & Lakehouse | Guides agents through converting exploratory notebooks into production-ready data jobs. |
| `python-data-engineering-and-pipeline-packaging` | Enterprise Data Engineering & Lakehouse | Guides agents through Python-based data engineering implementation, packaging, and CLI jobs. |
| `python-scratchpad` | Core Quality & Refactoring | Isolated test scripts and execution scratchpad for fast Python validation. |
| `quality-assurance` | Core Quality & Refactoring | Automatic quality control, testing patterns, and static analysis procedures. |
| `refactor` | Core Quality & Refactoring | Surgical code refactoring to improve maintainability without changing external behavior. |
| `rest-api-caller` | Core Quality & Refactoring | Call REST APIs from Python, parse JSON responses, and report structured data. |
| `run-opencode` | Core Quality & Refactoring | Run OpenCode CLI for AI-powered code analysis, refactoring, and troubleshooting. |
| `run-segmentation-training` | Deep Learning & Medical Computer Vision | Executes the fine-tuning training loop for hierarchical U-Net segmentation models. |
| `scientific-diagram-architect` | Publishing, Diagrams & Content Polish | Architectural specifications and vector-to-raster rendering for publication-quality diagrams. |
| `semantic-layer-and-metric-governance` | Enterprise Data Engineering & Lakehouse | Guides agents through semantic layer and shared metric design and governance. |
| `totalsegmentator` | Deep Learning & Medical Computer Vision | Non-interactive anatomical segmentation CLI and run-report parsing for medical imaging. |
| `warehouse-and-schema-design` | Enterprise Data Engineering & Lakehouse | Guides agents through data warehouse and schema design, fact/dim modeling, and keys. |
| `wealth-advisor-ui` | Frontend, UI/UX & Design Systems | Design and build UI for wealth advisor frontend (React 19, Tailwind 4, CVA, React Hook Form). |

<!-- END_ACTIVE_SKILLS -->

---

## Removed Skills

<!-- BEGIN_REMOVED_SKILLS -->

_No skills removed yet. Full suite intact._

<!-- END_REMOVED_SKILLS -->

---

## Core Engineering Directives

- **Zero Emojis:** Strictly prohibited in code, comments, terminal logs, commits, and UI. Use accessible inline SVG icons.
- **Zero Em-Dashes:** No `—` or `&mdash;` typography; use commas, colons, or standard hyphens `-`.
- **Dual Bearings:** Consult `graphify` (internal code graph) and `docmancer` (external documentation) prior to making code edits.
- **Subagent Policy:** Use parallel `self` subagents for isolated domains; execute sequentially on shared files.
- **macOS Port Guard:** Port 5001 for backend servers (avoiding macOS AirPlay on port 5000); port 3000 for frontend servers.
- **No Inline Terminal Python:** Never run `python3 -c "..."`. Write dedicated scratch script files.
- **Verification First:** Run automated test suites before visual inspections; require zero errors and zero warnings before committing.

---

## Visual Aesthetics & Generative Motion Archetypes

When developing frontend interfaces or interactive backgrounds, consult the four core design archetypes documented in [`INITIAL_AGENT_INSTRUCTIONS.md`](INITIAL_AGENT_INSTRUCTIONS.md):

1. **Constellation & Particle Physics:** ([particles.js](https://github.com/VincentGarreau/particles.js/)) — Minimalist 2D canvas particle networks, Euclidean proximity linking, and interactive mouse repulsion/grab.
2. **Algorithmic Delaunay Geometry:** ([Trianglify](https://github.com/qrohlf/trianglify)) — Low-poly Delaunay triangulation, Poisson-disc sampling, and crystalline chromatic color palettes.
3. **Organic Cartographic Isoline Topography:** ([Gradient Topography Animation](https://github.com/codrops/GradientTopographyAnimation/)) — Concentric SVG contour morphing with Anime.js and rich multi-stop gradient meshes.
4. **Turnkey 3D WebGL Environments:** ([Vanta.js](https://github.com/tengbao/vanta)) — Turnkey Three.js animated worlds (Birds, Waves, Fog, Clouds, Net, Topology) with cursor reactivity.
