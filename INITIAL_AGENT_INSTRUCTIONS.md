# Initial Agent Instructions

This document specifies the initial bootstrapping checklist for any AI coding agent starting work in a project cloned from this template.

---

## The 3-Step Bootstrapping Protocol

```
 ┌─────────────────────────────────────────────────────────────┐
 │                  INITIAL AGENT BOOTSTRAP                    │
 ├─────────────────────────────────────────────────────────────┤
 │ 1. Classify Project Type                                    │
 │    └── Web / Fullstack | ML / Vision | Data Eng | Minimal   │
 │                                                             │
 │ 2. Trim Skill Suite                                         │
 │    ├── Run python3 scripts/trim_skills.py                   │
 │    └── Update README.md with removed skills                 │
 │                                                             │
 │ 3. Anticipate Complexity & Online Template Discovery        │
 │    ├── Check for intricate requirements                     │
 │    ├── Search GitHub for fitting starters                   │
 │    ├── Hard Rule: AVOID repos > 5,000 commits               │
 │    └── Curl download & unpack clean archive                 │
 └─────────────────────────────────────────────────────────────┘
```

---

## 1. Project Classification & Skill Trimming

Do not keep all 36 skills in a specialized project. Assess the goal and trim the suite immediately:

1. **Classify Project Type:**
   - **`web-app`:** React, Next.js, Astro, Tailwind, UI components, API routes.
   - **`deep-learning`:** PyTorch, U-Net, CNNs, Kaggle, DICOM, medical imaging.
   - **`data-engineering`:** DuckDB, Parquet, data lakes, ETL pipelines, schema design.
   - **`minimal`:** Lightweight utility, CLI tool, or isolated script.

2. **Execute Trimming:**
   Run the included trimmer script from the repository root:
   ```bash
   # Option A: Preset trimming
   python3 scripts/trim_skills.py --preset web-app

   # Option B: Custom retention
   python3 scripts/trim_skills.py --keep refactor,quality-assurance,document-manipulation,graphify,docmancer

   # Option C: Custom removal
   python3 scripts/trim_skills.py --remove totalsegmentator,kaggle,esf-audit-verification
   ```

3. **Update README:**
   `scripts/trim_skills.py` will automatically update the active and removed skill sections in `README.md`. If trimming manually, make sure to record all removed skills in `README.md` under the `## Removed Skills` heading.

---

## 2. Anticipating Complexity & Online Template Acquisition

If the user's project involves non-trivial boilerplate, complex architecture, or unfamiliar domain stacks (e.g., decentralized protocols, multi-tenant authentication, 3D WebGL viewers, real-time audio streams):

### A. Anticipate Architectural Pain Points
Identify high-risk architectural decisions before writing initial code. Determine what foundational components (routing, middleware, state management, worker threads) are standard for this domain.

### B. Search for an Open Source Reference
Search online (GitHub, GitLab, or verified template registries) for a focused template repository that matches the tech stack.

### C. The 5,000 Commits Rule
> [!IMPORTANT]
> **Strictly avoid repositories with over 5,000 commits as templates.**
> Repositories with >5,000 commits are monolithic, contain years of legacy baggage, use complex custom monorepo tooling, and introduce bloat that slows down builds and pollutes context windows.
> Choose concise, modern starter repositories with clean commits (ideally under 2,000 commits, never over 5,000).

### D. Curl and Download the Starter
Never clone large histories with `.git`. Instead, download the archive tarball directly:

```bash
# 1. Download tarball via curl
curl -L "https://github.com/<owner>/<repo>/archive/refs/heads/main.tar.gz" -o starter.tar.gz

# 2. Extract into current directory (stripping top folder)
tar -xzf starter.tar.gz --strip-components=1 -C .

# 3. Clean up archive file
rm starter.tar.gz
```

Inspect the downloaded structure, remove unneeded sample pages or CI workflows, and adapt it to the project brief.

---

## 3. Mandatory Engineering Standards

Follow these core principles from [AGENTS.md](AGENTS.md) throughout development:

- **No Emojis:** Strictly prohibited across UI, logs, comments, commit messages, and docs. Use accessible inline SVG icons.
- **No Em-Dashes:** Avoid `—` or `&mdash;`; use standard hyphens, commas, or colons.
- **Pre-execution Bearings:** Always consult `graphify` (internal map) and `docmancer` (external API docs) before making structural edits.
- **Subagent Strategy:** Use parallel `self` subagents only for disjoint tasks with zero file overlap; execute intertwined tasks sequentially.
- **Port Discipline:** Use port 5001 for backend servers (avoiding macOS AirPlay port 5000) and port 3000 for frontend servers.
- **No Inline Terminal Python:** Never run `python3 -c "..."`. Write dedicated scratch script files to disk.
- **Verification First:** Ensure `npm test`, `pytest`, or build commands pass with 0 errors and 0 warnings before committing.

---

## 4. Visual Aesthetics & Generative Motion Archetypes

When designing user interfaces, creative landing pages, or ambient canvas backgrounds, agents should reference these four core generative visual archetypes rather than defaulting to generic static styles:

### A. Constellation & Interactive Particle Physics
* **Reference:** [VincentGarreau/particles.js](https://github.com/VincentGarreau/particles.js/)
* **Design Philosophy:** Declarative, zero-dependency 2D canvas particle physics. Treats Euclidean mathematical proximity as an emergent connective fabric, simulating interconnected networks, neural synapses, and living digital matter.
* **Aesthetic Style & Motion:** Minimalist floating points with subtle linear drift, delicate linking segments that form and dissolve dynamically, and responsive mouse physics (repulse, grab, and burst).
* **Best Used For:** Technical landing pages, Web3/crypto protocols, developer portfolios, and cybersecurity or AI network dashboards.

### B. Algorithmic Low-Poly Delaunay Geometry
* **Reference:** [qrohlf/trianglify](https://github.com/qrohlf/trianglify)
* **Design Philosophy:** Computational order emerging from controlled randomness. Utilizes Poisson-disc or jittered-grid point distributions combined with Delaunay triangulation to bridge mathematical algorithms with generative color theory.
* **Aesthetic Style & Motion:** Crisp, low-poly faceted meshes, smooth chromatic gradients interpolated across triangle centroids, and crystalline, jewel-like vector backdrops.
* **Best Used For:** High-resolution hero banners, printable graphic assets, tech event posters, and mathematically structured brand identities.

### C. Organic Cartographic Isoline Topography
* **Reference:** [codrops/GradientTopographyAnimation](https://github.com/codrops/GradientTopographyAnimation/)
* **Design Philosophy:** Translating elevation cartography into animated editorial art. Combines contour lines (isolines) with fluid generative SVG morphing and multi-stop color meshes to create an organic, breathing landscape.
* **Aesthetic Style & Motion:** Concentric undulating contour curves morphing and rotating via Anime.js with staggered easings, paired with saturated duotone and sunset gradient meshes (magentas, oranges, deep purples, and midnight blues).
* **Best Used For:** High-fashion digital design, creative agency portfolios, editorial storytelling, and modern generative SaaS landing pages.

### D. Turnkey 3D WebGL Ambient Environments
* **Reference:** [tengbao/vanta](https://github.com/tengbao/vanta) ([Vanta.js](https://www.vantajs.com))
* **Design Philosophy:** Democratizing complex 3D WebGL shaders and procedural simulation into a plug-and-play, single-function background layer without boilerplate GLSL setup.
* **Aesthetic Style & Motion:** Immersive 3D motion: boids flocking simulation (`Birds`), specular sine-wave heightmaps (`Waves`), volumetric noise fields (`Fog`, `Clouds`), and 3D spatial node webs (`Net`), continuously reacting to cursor movement, scroll parallax, and camera angle.
* **Best Used For:** High-impact SaaS hero sections, experiential marketing portals, interactive product launches, and immersive spatial web apps.

