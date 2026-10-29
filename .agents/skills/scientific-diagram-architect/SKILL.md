---
name: scientific-diagram-architect
description: Architectural specifications, aesthetic palettes, mathematical layout formulas, and high-fidelity vector-to-raster rendering pipelines for scientific and ML architecture SVG diagrams.
---

# Scientific Diagram Architect & Vector-to-Raster Skill

This skill defines the architectural design standards, typography hierarchies, container sizing formulas, and vector-to-raster pipelines required to produce publication-grade machine learning and medical system diagrams in SVG with companion high-resolution Retina PNG previews.

---

## 1. Visual Aesthetic & Palette Standards

All diagrams must employ a modern, high-contrast, professional dark theme designed for technical publications, presentations, and GitHub markdown documentation.

### The Canonical Color Palette
- **Canvas Background:** `#080c14` to `#0f172a` (deep obsidian/slate gradient `grad-bg`)
- **Card Containers:** `#1e293b` with 95% opacity transitioning to `#0f172a` (`grad-card`)
- **Container Borders:** Subtle slate boundaries (`#334155` or `#475569`, stroke-width: 1.5–1.8 px)
- **Primary Stream / Encoder:** Electric Blue (`#38bdf8` to `#0284c7`)
- **Secondary Stream / Decoder:** Emerald / Teal (`#2dd4bf` to `#0d9488` or `#34d399` to `#059669`)
- **Bottleneck / ViT Transformer:** Deep Indigo / Purple (`#c084fc` to `#7e22ce` or `#818cf8` to `#4338ca`)
- **Loss Engine & Objective Math:** Royal Indigo (`#1e1b4b` background, `#6366f1` border, `#a5b4fc` text)
- **Warnings / Failure Modes:** Soft Rose / Coral (`#fb7185` to `#e11d48`)
- **Key Benchmarks & Outlier Shield:** Amber (`#fbbf24` to `#d97706`)

---

## 2. Root SVG Dimension Contract (Critical)

### The Rule
Every SVG file intended for multi-platform documentation, browser rendering, or rasterization **must declare explicit pixel dimensions on the root `<svg>` element matching its `viewBox`**:

```xml
<!-- CORRECT: Explicit pixel dimensions matching viewBox -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1520 920" width="1520" height="920">

<!-- INCORRECT: Relative percentage dimensions (BREAKS RASTERIZERS) -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1520 920" width="100%" height="100%">
```

### Why This Matters
When `width="100%"` or `height="100%"` is used:
1. Vector rendering engines such as **PyMuPDF (`fitz`)**, **Cairo**, or **Inkscape** cannot infer physical pixel bounds and fall back to default US Letter page dimensions ($612 \times 792\,\text{pt}$).
2. The graphic is distorted, clipped, or forced into arbitrary aspect ratios.
3. QuickLook and browser print drivers introduce unpredictable whitespace margins.

---

## 3. Typography & Mathematical Layout Engineering

### 3.1 Font Stacks & Sizes
- **General Labels & Headers:** `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
  - Main Diagram Title: `font-size="20" - "24"`, `font-weight="800"`, `fill="#f8fafc"`
  - Section Headers: `font-size="14" - "16"`, `font-weight="700"`, `fill="#a5b4fc"`
  - Body Explanations: `font-size="11" - "13"`, `font-weight="400" - "500"`, `fill="#cbd5e1"`
  - Micro-annotations (e.g. downsample strides): `font-size="9" - "10"`, `fill="#fbbf24"`
- **Tensors, Code, & Mathematical Formulas:** `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace`
  - Tensor Dimensions: `font-size="11" - "12"`, `font-weight="700"`, `fill="#818cf8"`
  - Loss Formulas: `font-size="11" - "12"`, `font-weight="700"`, `fill="#e0e7ff"`

### 3.2 Preventing Text Overflows & Math Leaks
In standard monospace fonts at font-size $S$, each character occupies approximately:
$$W_{\text{char}} \approx 0.60 \times S\,\text{px}$$

For an equation containing $N$ characters at font-size $12\,\text{px}$:
$$W_{\text{text}} \approx N \times 7.2\,\text{px}$$

| Formula Length | Char Count ($N$) | Required Text Width | Minimum Container Width ($\ge 20\%$ safety) | Action Required |
| :--- | :---: | :---: | :---: | :--- |
| Short Tensor | 22 | $\sim 158\,\text{px}$ | $200\,\text{px}$ | Single line |
| Moderate Loss Term | 45 | $\sim 324\,\text{px}$ | $400\,\text{px}$ | Single line |
| Composite Loss Equation | 75+ | $\sim 540\,\text{px}$ | **$\ge 650\,\text{px}$** | **Split into 2+ lines!** |

### Standard Multi-Line Equation Pattern
Never squeeze complex multi-term loss functions into a single line. Break them into indented lines:

```xml
<g transform="translate(28, 385)">
  <rect width="664" height="135" rx="10" fill="#1e1b4b" stroke="#6366f1" stroke-width="1.5"/>
  <text x="20" y="28" font-family="system-ui, sans-serif" font-size="14" font-weight="700" fill="#a5b4fc">3. Multi-Objective Joint Loss</text>
  <text x="20" y="52" font-family="monospace" font-size="12" font-weight="700" fill="#e0e7ff">L_total = 1.0·L_Tversky + 0.5·L_BCE_mask + 1.0·L_boundary</text>
  <text x="20" y="74" font-family="monospace" font-size="12" font-weight="700" fill="#c7d2fe">        + 0.2·L_cup + 0.5·L_thickness + 0.1·L_edge</text>
  <text x="20" y="98" font-family="system-ui, sans-serif" font-size="11" fill="#cbd5e1">• Tversky Loss handles class imbalance (RNFL &lt; 4% of volume)</text>
  <text x="20" y="118" font-family="system-ui, sans-serif" font-size="11" fill="#cbd5e1">• Optical edge loss locks regression heads to reflectance gradients</text>
</g>
```

---

## 4. Vector-to-Raster Engine Standards (PyMuPDF vs. `qlmanage`)

### The `qlmanage` Anti-Pattern
Never use macOS QuickLook (`/usr/bin/qlmanage -t -s <size>`) followed by mathematical bounding-box cropping (`im.crop`):
- `qlmanage` is a Finder icon thumbnail generator, **not** a vector rasterizer.
- It enforces a square canvas ($3200 \times 3200$) and applies thumbnail zooming heuristics that push content into unpredictable offsets.
- Blind mathematical cropping (`crop((0, y_offset, S, y_offset + target_h))`) cuts off top titles, bottom analysis boxes, and outer columns.

### The Gold Standard: PyMuPDF Direct Vector Rasterization
Use **PyMuPDF (`import fitz`)** to directly rasterize SVG vector primitives using the high-performance C MuPDF engine:
- Reads the exact vector paths directly from the SVG DOM.
- Calculates the scaling transformation:
  $$\text{scale} = \frac{W_{\text{target}}}{W_{\text{viewBox}}}, \quad \mathbf{M} = \begin{bmatrix} \text{scale} & 0 \\ 0 & \text{scale} \end{bmatrix}$$
- Outputs full-frame, native $3200\,\text{px}$ Retina PNGs with **zero cropping, zero letterboxing, and zero distortion**.

---

## 5. Standalone CLI Utility: `rasterize_svg.py`

This skill provides a self-contained CLI script located at:
`scripts/rasterize_svg.py`

### 5.1 Subcommands & Examples

```bash
# 1. Validate SVG syntax, dimensions, and scan for potential text overflows
python3 .agents/skills/scientific-diagram-architect/scripts/rasterize_svg.py validate path/to/diagrams/

# 2. Automatically fix root <svg> dimensions to match its viewBox
python3 .agents/skills/scientific-diagram-architect/scripts/rasterize_svg.py fix-dimensions path/to/diagram.svg

# 3. Rasterize a single SVG to 3200px Retina PNG
python3 .agents/skills/scientific-diagram-architect/scripts/rasterize_svg.py rasterize path/to/diagram.svg

# 4. Batch-rasterize an entire directory of SVGs to Retina PNGs
python3 .agents/skills/scientific-diagram-architect/scripts/rasterize_svg.py rasterize path/to/svg_dir/ --width 3200
```

---

## 6. GitHub Markdown Presentation Pattern

When linking diagrams in GitHub repositories or documentation:
1. Always commit both the source `.svg` and the companion $3200\,\text{px}$ `.png`.
2. Embed the raster PNG as the inline preview, wrapped in a markdown link pointing to the vector SVG:

```markdown
[![Architecture Diagram Description](./svg/model_architecture.png)](./svg/model_architecture.svg)
```

**Benefits:**
- GitHub renders the high-res PNG instantly across all mobile, tablet, and desktop viewports with zero SVG sanitization or font rendering bugs.
- Clicking the image opens the vector SVG, allowing users to zoom indefinitely into vector details.

---

## 7. Mandatory Radar / Spider Chart Rule (Regular Polygon Rings)

### The Rule: NEVER Render Circular Polar Orbits
In clinical and benchmark documentation, all Radar / Spider charts **must be drawn with crisp regular polygon rings matching the number of axes $N$** (e.g. pentagons for $N=5$, hexagons for $N=6$). Circular polar gridlines and spines are strictly prohibited:

```python
# MANDATORY PATTERN for Radar / Spider Charts:
ax.spines['polar'].set_visible(False)
ax.grid(False)

# Draw concentric regular polygon rings (N vertices)
rings = [0.2, 0.4, 0.6, 0.8, 1.0]
for r in rings:
    ax.plot(angles_closed, [r] * (N + 1), color='#cbd5e1', linestyle='--', linewidth=1.0)

# Radial spokes from origin to polygon vertices
for angle in angles:
    ax.plot([angle, angle], [0, 1.0], color='#cbd5e1', linewidth=1.2)
```

---

## 8. Pre-Flight Checklist Before Committing Diagrams

Before committing any new architecture diagram:
- [ ] Root `<svg>` has explicit pixel `width="W"` and `height="H"` matching `viewBox="0 0 W H"`.
- [ ] XML passes `validate` without syntax errors.
- [ ] Long equations ($>50$ chars) are split across multiple lines and containers have $\ge 20\%$ margin.
- [ ] Rendered PNG was created via PyMuPDF vector rasterizer (`rasterize_svg.py rasterize`), **not** `qlmanage`.
- [ ] Radar / Spider charts use **concentric regular polygon rings** and radial spokes (`ax.spines['polar'].set_visible(False)`). No circular polar orbits!
- [ ] Visually verified with `view_file` that the PNG has no cropped headers, no sliced columns, and no white letterbox bars.
- [ ] Markdown documents reference `[![Alt](./svg/<name>.png)](./svg/<name>.svg)`.

