# Global Agent Directives — Vibe Code Template

Welcome to the **Vibe Code Template**. This repository serves as the universal springboard for building high-velocity, production-grade applications. It provides a curated suite of 36 battle-tested agent skills and foundational engineering directives.

---

## 1. Initial Agent Onboarding Protocol

Whenever you (an AI agent) are initialized in a new project instantiated from this template, you MUST execute the following three onboarding steps before writing application code:

### Step 1: Project Scoping & Skill Suite Trimming
Assess the project requirements, architecture, and technology stack. Do not keep unused skills cluttering the workspace.
1. Identify the project type:
   - **Web / Fullstack App:** (React, Next.js, Astro, Tailwind, Node/FastAPI)
   - **Deep Learning / Computer Vision:** (PyTorch, U-Net, Kaggle, DICOM, Segmentation)
   - **Enterprise Data Engineering:** (DuckDB, Parquet, Data Lake, Lakehouse, ETL)
   - **Minimal Utility / CLI / Script:** (Lightweight tools, scripting, automation)
2. Trim the skill suite down to only the skills relevant to the project:
   - Use the automated trimmer script:
     ```bash
     # Apply a preset (minimal, web-app, deep-learning, data-engineering)
     python3 scripts/trim_skills.py --preset web-app

     # Or explicitly keep only specific skills
     python3 scripts/trim_skills.py --keep refactor,quality-assurance,graphify,docmancer,glassmorphism-ui
     ```
   - Alternatively, remove unneeded directories manually from `.agents/skills/`.
3. **Synchronize README:** Ensure `README.md` is updated with the list of removed skills and the retained active skills (handled automatically by `trim_skills.py`).

### Step 2: Complexity Anticipation & Online Template Acquisition
If the project requirements are complex, specialized, or involve intricate boilerplate (e.g., custom WebGL pipelines, auth with multi-tenancy, cross-platform mobile, novel deep learning architectures):
1. **Anticipate architectural friction:** Identify standard patterns, libraries, and structures needed early rather than scaffolding everything from scratch.
2. **Research an online reference repository:** Use search tools or GitHub API to find an open-source template or reference project that fits the tech stack.
3. **The 5,000 Commits Rule (Mandatory):**
   - **NEVER use repositories with over 5,000 commits as templates.**
   - *Rationale:* Giant repositories (>5k commits) are typically enterprise monorepos or legacy codebases. They suffer from bloat, obscure build tooling, massive dependency trees, deprecated configurations, and excessive token overhead that degrade agent performance.
   - Look for clean, focused, modular starters or templates with under 5,000 commits (ideally 100 to 2,000 commits).
4. **Curl and download the archive:**
   - Download the clean tarball/zip directly to avoid dragging in external git histories:
     ```bash
     curl -L "https://github.com/<owner>/<repo>/archive/refs/heads/main.tar.gz" -o starter.tar.gz
     tar -xzf starter.tar.gz --strip-components=1 -C .
     rm starter.tar.gz
     ```
   - Inspect and clean up unwanted boilerplate (.github workflows, extraneous docs, author-specific licenses/readmes).

### Step 3: Establish Bearings Before Execution
Before taking any action or answering architectural questions:
1. **Internal Map (Graphify):** If `graphify-out/` or `/graphify` is present, consult the knowledge graph to understand symbol dependencies and file topologies.
2. **External Guide (Docmancer):** If third-party libraries, APIs, or framework rules are involved, query Docmancer (`docmancer query`) to retrieve authoritative, version-accurate syntax.

---

## 2. Core Communication & Typography Directives

### Strict "No Emojis" Policy
- **No Unicode emojis anywhere:** Emojis are strictly forbidden across user-facing UI copy, HTML/JSX templates, code comments, terminal logs, git commit messages, documentation files, and markdown artifacts.
- **Console and terminal badges:** Use clean, square-bracketed textual badges (`[INFO]`, `[PASS]`, `[FAIL]`, `[WARN]`, `[AUTH]`, `[DB]`).
- **SVG Icon Standard:** When visual icons or indicators are needed in user interfaces, always use accessible, inline or external SVG vector icons:
  - Specify `viewBox="0 0 24 24"`.
  - Use `fill="currentColor"` (or `stroke="currentColor"` with `fill="none"`).
  - Include `aria-hidden="true"` on decorative icons, or provide `aria-label` / `<title>` on interactive buttons.

### Strict "No Em-Dash / mdash" Policy
- **Em-dashes (`—`, `&mdash;`, `\u2014`) are strictly prohibited.**
- Use clean, standard punctuation (commas, colons, parentheses, standard hyphens `-`, or periods) instead.

---

## 3. Subagent Delegation Model

When assigned multiple features, tasks, or bug fixes in a single session, decide between parallel delegation and sequential execution based on codebase overlap:

1. **Parallel Delegation (`self` subagents):**
   - Use for naturally isolated tasks with zero file overlap (e.g., one agent writes backend endpoints, one builds independent frontend components, one generates documentation).
   - Spawn subagents simultaneously via `invoke_subagent`.
2. **Sequential Execution (Single agent):**
   - Mandatory for intertwined tasks modifying shared files or configurations.
   - For overlapping changes, execute them sequentially yourself to maintain complete context and prevent git merge conflicts or race conditions.

---

## 4. Hardware & Runtime Guardrails

### macOS / Apple Silicon Constraints
- **Port Conflict Awareness:** Port 5000 is occupied by macOS Control Center / AirPlay Receiver. Always use **port 5001** for backend dev servers and **port 3000** for frontend dev servers.
- **Optimal DataLoader Config:** For PyTorch model training and evaluation on Apple Silicon, default to:
  ```python
  batch_size = 64
  num_workers = 4
  pin_memory = False
  ```
  This configuration prevents Unified Memory saturation and worker thread deadlocks.
- **GPU Acceleration:** Always auto-detect and utilize available acceleration (`cuda` or `mps`):
  ```python
  device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
  ```

### No Inline Python in Terminal
- **NEVER execute Python logic inline via terminal commands** (e.g., `python3 -c "..."` or heredocs).
- Inline execution causes string escaping bugs, IO buffering deadlocks, and truncated stack traces.
- **Rule:** Always write a dedicated scratch script file (e.g., `scratch/test_step.py`) and execute it directly (`python3 scratch/test_step.py`).

---

## 5. Testing, Verification & Code Quality

1. **Automate Before Visual Checking:**
   - In web applications, always run automated smoke tests and type-checks (`npm test`, `npm run build`, `npm run type-check`) before performing browser or visual inspections.
2. **Cheap vs. Expensive Test Suites:**
   - Always run fast, lightweight unit tests first. Only run heavy end-to-end integration or volumetric training suites once unit tests pass.
3. **Machine-Readable Outputs:**
   - Rely on structured JSON manifests or run reports (`run_report.json`, `statistics.json`) rather than scraping human stdout in pipelines.
4. **Zero Fluff & Complete Implementations:**
   - Never leave lazy placeholders (`// TODO: implement later` or `# insert logic here`).
   - Write complete, robust implementations with comprehensive error handling.

---

## 6. Git & Documentation Hygiene

1. **Clean Commit Messages:**
   - Use clear conventional commit style (`feat: ...`, `fix: ...`, `refactor: ...`).
   - Never add tool attributions or AI co-author trailers in commit messages.
2. **Single Responsibility:**
   - Keep commits atomic. If code changes alter documentation or route tables, update the owning documentation files in the exact same commit.
3. **Naming Conventions:**
   - Internal documentation files use `kebab-case.md` (e.g., `initial-agent-instructions.md`).
   - Workspace root markers remain uppercase (`AGENTS.md`, `README.md`, `LICENSE`).

---

## 7. Visual Aesthetics & Generative Motion Archetypes

When designing user interfaces, creative landing pages, or ambient canvas backgrounds, agents should reference these four core generative visual archetypes rather than defaulting to generic static styles:

1. **Constellation & Interactive Particle Physics:** ([particles.js](https://github.com/VincentGarreau/particles.js/))
   - *Design Philosophy:* Declarative, zero-dependency 2D canvas particle physics. Treats Euclidean mathematical proximity as an emergent connective fabric, simulating interconnected networks, neural synapses, and living digital matter.
   - *Aesthetic Style & Motion:* Minimalist floating points with subtle linear drift, delicate linking segments that form and dissolve dynamically, and responsive mouse physics (repulse, grab, and burst).
   - *Best Used For:* Technical landing pages, Web3/crypto protocols, developer portfolios, and cybersecurity or AI network dashboards.

2. **Algorithmic Low-Poly Delaunay Geometry:** ([Trianglify](https://github.com/qrohlf/trianglify))
   - *Design Philosophy:* Computational order emerging from controlled randomness. Utilizes Poisson-disc or jittered-grid point distributions combined with Delaunay triangulation to bridge mathematical algorithms with generative color theory.
   - *Aesthetic Style & Motion:* Crisp, low-poly faceted meshes, smooth chromatic gradients interpolated across triangle centroids, and crystalline, jewel-like vector backdrops.
   - *Best Used For:* High-resolution hero banners, printable graphic assets, tech event posters, and mathematically structured brand identities.

3. **Organic Cartographic Isoline Topography:** ([Gradient Topography Animation](https://github.com/codrops/GradientTopographyAnimation/))
   - *Design Philosophy:* Translating elevation cartography into animated editorial art. Combines contour lines (isolines) with fluid generative SVG morphing and multi-stop color meshes to create an organic, breathing landscape.
   - *Aesthetic Style & Motion:* Concentric undulating contour curves morphing and rotating via Anime.js with staggered easings, paired with saturated duotone and sunset gradient meshes (magentas, oranges, deep purples, and midnight blues).
   - *Best Used For:* High-fashion digital design, creative agency portfolios, editorial storytelling, and modern generative SaaS landing pages.

4. **Turnkey 3D WebGL Ambient Environments:** ([Vanta.js](https://github.com/tengbao/vanta) / [vantajs.com](https://www.vantajs.com))
   - *Design Philosophy:* Democratizing complex 3D WebGL shaders and procedural simulation into a plug-and-play, single-function background layer without boilerplate GLSL setup.
   - *Aesthetic Style & Motion:* Immersive 3D motion: boids flocking simulation (`Birds`), specular sine-wave heightmaps (`Waves`), volumetric noise fields (`Fog`, `Clouds`), and 3D spatial node webs (`Net`), continuously reacting to cursor movement, scroll parallax, and camera angle.
   - *Best Used For:* High-impact SaaS hero sections, experiential marketing portals, interactive product launches, and immersive spatial web apps.

