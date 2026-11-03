---
name: ipmi-visual-architect
description: Architectural specifications, aesthetic palettes, Springer LNCS dimension contracts, vector-raster hybrid standards, and programmatic SVG-to-PDF/PNG generation pipelines for publication-grade IPMI and medical imaging diagrams.
---

# IPMI Visual Architect & Medical Figure Engineering Skill

This skill defines the architectural design standards, typography hierarchies, layout geometry, color theory, and automated rendering pipelines required to produce publication-grade medical imaging figures for the **International Conference on Information Processing in Medical Imaging (IPMI)** and **Springer LNCS** proceedings (such as MICCAI and IPMI).

Every standard in this skill is derived from empirical analysis of canonical IPMI proceedings volumes (*Information Processing in Medical Imaging*, Springer LNCS 14644 / ISBN 978-3-031-96628-6) and the battle-tested vector SVG architectures in this codebase (`OCT-Analyser-Capstone/docs/cohort_reports/shift_invariant_detilted_29d_proof_of_concept/generate_ipmi_svgs.py`).

---

## 1. The Core Axiom: Intentional Visualization vs. Math Containers

> **The Golden Law of Scientific Illustration:**  
> **A diagram is supposed to be a visualization.** If there is math or text in the diagram that could have been visualized instead, **the diagram fails.**

A publication diagram exists to give the reader an **instant, intuitive visual mental model** of a mechanism in 3 to 5 seconds. The LaTeX document body already contains formal equations in Section 3 and Section 5. Copying formulas into colored boxes (`FancyBboxPatch`) is an amateur anti-pattern, not visualization.

### What is Intentional Visualization?
1. **The Functional Truth Axiom (No Fantasy Metaphors):**
   * **Strict Ban on Pseudo-Physical Cartoons:** Never invent arbitrary physical metaphors (pinched hourglasses, stretched taffy, balloons, gears, rubber bands, cartoon crosshairs/targets). They introduce cognitive friction and clinical confusion (e.g., labeling a negative logit as an "interior void" falsely implies an anatomical cyst or macular hole).
   * **Plot the True Functional Space Directly:** If a phenomenon involves activations, features, or losses: **plot the true 1D or 2D function curve directly on calibrated axes**.
     * *Example (Logit Suppression / Theorem 1):* Plot axial depth $y$ on the vertical axis vs. voxel logit $z(y) = \mathbf{w}_{\text{mask}}^\top \mathbf{h}(y)$ on the horizontal axis. Draw the $z = 0$ threshold ($p = 0.5$). Show the activation curve peaking above zero at $y_{\text{ILM}}$ and $y_{\text{NFL}}$ while visibly sagging below zero ($z < 0$) in the interior. In 2 seconds, any reviewer or student understands the exact mathematical mechanism with zero fantasy metaphors.
   * **Equivariance / Lie Group Invariance:** Never write commutator formulas $[\xi_1, \xi_2]$. Draw an intuitive 3D reference object (like a paper airplane) undergoing rigid transformations in space.
2. **The Simplest & Neatest Way to Draw Diagrams:**
   * **Programmatic Vector SVG $\longrightarrow$ PyMuPDF (`fitz`) 600 DPI Vector PDF & Retina PNG:**
     * Do **NOT** use Matplotlib patches (`FancyBboxPatch`, `ax.annotate`) for network architectures or multi-panel composite figures. Matplotlib's layout engine dynamically places text boxes based on font bounding boxes which differ across backends and fonts, resulting in overlaps, collisions, and clipped labels.
     * SVG provides **deterministic mathematical control** over coordinates, smooth Bezier curves, clean functional axes, exact pixel docking, and crisp modern typography.
     * PyMuPDF compiles the SVG directly into a native vector PDF stream (`doc.convert_to_pdf()`) and crystal-clear 600 DPI Retina PNGs with zero distortion, zero clipping, and infinite vector zoom.

---

## 2. The Canonical Tripartite SVG Figure Architecture (The 1400 × 640 Canon)

Learned directly from canonical reference `generate_ipmi_svgs.py`, all high-level IPMI methodology figures should follow the **Tripartite Composition Pattern** inside an explicit coordinate system:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ viewBox="0 0 1400 640" (Aspect Ratio: 2.19, strictly within Springer LNCS [1.9, 2.5]) │
│                                                                                        │
│ ┌────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ PANEL (a): MACRO PIPELINE (Top Full-Width Panel: x=16, y=12, w=1368, h=264)        │ │
│ │ End-to-End Volumetric Data Flow: Inputs → Core Modules → Heads → Consensus          │ │
│ └────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                        │
│ ┌──────────────────────────────────────────┐ ┌───────────────────────────────────────┐ │
│ │ PANEL (b): MICRO MECHANISM               │ │ PANEL (c): FORMAL BOUND & BENCHMARK   │ │
│ │ (Bottom-Left: x=16, y=286, w=668, h=342) │ │ (Bottom-Right: x=698, y=286, w=686)   │ │
│ │ Sub-block 1: Functional Curve / Axes     │ │ Top Card: Mathematical Law / Bound    │ │
│ │ Sub-block 2: Authentic Anatomical Cross  │ │ Bottom: N=40 Cohort Benchmark Table   │ │
│ └──────────────────────────────────────────┘ └───────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Deterministic Layout Math (Zero Text Overlap Guarantee)
To guarantee zero collisions across any rendering engine:
1. **Container Cards:** Fixed $(x, y, w, h)$ bounding rectangles with subtle border radius (`rx=5` or `rx=6`).
2. **Header Banners:** Filled top banner path `<path d="M x y+r Q x y x+r y L x+w-r y Q x+w y x+w y+r L x+w y+h_hdr L x y+h_hdr Z"/>` with high-contrast text (`fill="#ffffff"` on saturated fills, or `#0f172a` on light tints).
3. **Line-Height Stepping Formula:** Every text line is assigned a strictly deterministic vertical baseline:
   $$y_{\text{line}}(i) = y_{\text{header}} + \text{offset} + i \cdot \Delta y$$
   where $\Delta y = 17\,\text{px}$ for $9.5\text{--}10\,\text{pt}$ text, and $14\,\text{px}$ for $8.5\,\text{pt}$ annotations.
4. **Tables:** Fixed column coordinates ($x_{\text{col0}}, x_{\text{col1}}, \dots$) with explicit `text-anchor="start"`, `"middle"`, or `"end"`.
5. **No Relative Shifting:** Never stack text using unanchored `<tspan>` tags without explicit `x` and `y` attributes.

---

## 3. Strict Anti-Patterns (Why They Fail & How to Enforce)

| Anti-Pattern | Why It Fails | Strict Enforcement Rule |
| :--- | :--- | :--- |
| **Arrow & Connector Crossings / Slicing Text** | Drawing backward gradient arrows or skip connections that cross directly over forward data arrows, or placing text labels without dedicated clearance so arrow shafts slice right through the text. | **STRICT BAN:** Never cross forward and backward arrows. In bidirectional junctions (e.g. forward activations $\to$ vs backward gradients $\leftarrow$), allocate **dedicated parallel horizontal lanes** (e.g. Forward at $y$, Backward at $y + 36\,\text{px}$ pointing in reverse). Use centered pill badges (`<rect>` + `<text>`) on the arrow shafts with explicit backgrounds. |
| **Matplotlib Multi-Line Text Collisions** | Matplotlib's layout engine dynamically places text boxes based on font bounding boxes which differ across backends and fonts, smashing titles into labels (e.g. "The Dual-Dice Paradox" overlapping "Surface-Guided Dice"). | **STRICT BAN:** Build composite architecture figures in **Programmatic SVG** with explicit mathematical coordinates $(x, y)$. |
| **Dark-on-Dark Unreadable Text** | Placing dark red text (`#b91c1c`) on dark or black backgrounds. Collapses into an illegible muddy smudge on print or slides. | **STRICT BAN:** All text must meet WCAG AAA contrast against pure white (`#ffffff`) or light tint backgrounds (`#fcf8ed`, `#ddebe1`, `#eef4fa`). White text is only permitted inside saturated header banners. |
| **Fantasy Metaphors (Hourglasses, Pinches, Taffy)** | Drawing arbitrary geometric shapes (hourglasses, pinched waists, cartoon targets) that have no basis in the anatomy or tensor math. Forces the reader to decode a useless metaphor. | **STRICT BAN:** Plot the actual mathematical function (e.g., 1D axial depth $y$ vs. logit $z(y)$) on clean coordinate axes. |
| **Clinical Terminology Pollution** | Using terms like "Interior Void" for a negative logit, which ophthalmologists mistake for a macular hole or intraretinal fluid cyst. | **STRICT RULE:** Use mathematically precise terms: "Logit Suppression ($z < 0$)", "Sub-threshold Probability ($p < 0.40$)", "Unsegmented Thin Lamina Dropout". |
| **Math Dumped into Boxes** | Copying LaTeX formulas like `$\mathcal{L}_{\text{coord}} \propto Y$` into colored rectangles. The diagram becomes an unreadable wall of text. | **STRICT BAN:** Translate the formula into physical geometry: a vector arrow, a functional profile curve, or a calibrated scale. |
| **Cartoonish / Software QA Tropes** | Using red `x` marks, green checkmarks, `[PASS]`/`[FAIL]` badges, or ALL-CAPS words like `(DOMINANT)`. | **STRICT BAN:** Use understated academic typography, clean calipers, and precise numerical deltas ($\Delta\text{Dice} = -0.6607$). |
| **Hand-Wavy Schematics Without Data Grounding / Black Voids** | Drawing solid black or dark abstract rectangles with opaque cartoon polygons instead of showing real medical tissue. Eliminates authentic anatomical speckle, tissue stratification, and clinical credibility. | **MANDATORY DATA GROUNDING:** Always embed **authentic clinical scan slices** (e.g. real OCT B-scans with speckle, vitreous cavity, ILM, retinal layers, and hyperreflective RPE). Use semi-transparent overlays ($\alpha \approx 0.35\text{--}0.45$) for segmentation masks so the real tissue remains visible underneath. |
| **Unconstrained Canvas Width** | Figures that spill over the $122\,\text{mm}$ margin or shrink down to an unreadable sliver. | **STRICT DIMENSION CONTRACT:** Canvas width must strictly equal **$122.0\,\text{mm} \approx 348.4\,\text{pt}$** ($4.838\,\text{in}$). |

---

## 4. Canonical Reusable Vector SVG Primitives

The following Python helper primitives from `generate_ipmi_svgs.py` must be used for drawing consistent geometry:

### 1. Isometric 3D Tensor Cuboid (`iso_cuboid`)
Renders an authentic 3D tensor volume with front, top, and right perspective facets:
```python
def iso_cuboid(x, y, w, h, dx, dy, front_fill, top_fill, side_fill, stroke, stroke_w=1.2):
    front = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{front_fill}" stroke="{stroke}" stroke-width="{stroke_w}" stroke-linejoin="round"/>'
    top = f'<polygon points="{x},{y} {x+dx},{y-dy} {x+w+dx},{y-dy} {x+w},{y}" fill="{top_fill}" stroke="{stroke}" stroke-width="{stroke_w}" stroke-linejoin="round"/>'
    side = f'<polygon points="{x+w},{y} {x+w+dx},{y-dy} {x+w+dx},{y+h-dy} {x+w},{y+h}" fill="{side_fill}" stroke="{stroke}" stroke-width="{stroke_w}" stroke-linejoin="round"/>'
    return f"<g>{top}{side}{front}</g>"
```

### 2. Geometric Polygon Arrowhead (`arrow_line` & `ortho_path_arrow`)
Renders sharp geometric polygon arrowheads without renderer bugs:
```python
def arrow_line(x1, y1, x2, y2, color="#1e293b", width=1.5, dashed=False, head_len=7.5, head_w=4.2):
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 1e-3: return ""
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    lx2, ly2 = x2 - ux * (head_len * 0.7), y2 - uy * (head_len * 0.7)
    bx, by = x2 - ux * head_len, y2 - uy * head_len
    p1x, p1y = bx + px * head_w, by + py * head_w
    p2x, p2y = bx - px * head_w, by - py * head_w
    dash = ' stroke-dasharray="5,3"' if dashed else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{lx2:.1f}" y2="{ly2:.1f}" stroke="{color}" stroke-width="{width}"{dash}/>' \
           f'<polygon points="{x2:.1f},{y2:.1f} {p1x:.1f},{p1y:.1f} {p2x:.1f},{p2y:.1f}" fill="{color}"/>'
```

### 3. Circular Math Operator Nodes (`math_op_node`)
Clean mathematical operator nodes ($\oplus, \otimes, \nabla$):
```python
def math_op_node(cx, cy, r, symbol, stroke="#1e293b", fill="#ffffff"):
    lines = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>']
    if symbol == "+":
        d = r * 0.55
        lines.append(f'<line x1="{cx-d}" y1="{cy}" x2="{cx+d}" y2="{cy}" stroke="{stroke}" stroke-width="1.4"/>')
        lines.append(f'<line x1="{cx}" y1="{cy-d}" x2="{cx}" y2="{cy+d}" stroke="{stroke}" stroke-width="1.4"/>')
    elif symbol == "x":
        d = r * 0.42
        lines.append(f'<line x1="{cx-d}" y1="{cy-d}" x2="{cx+d}" y2="{cy+d}" stroke="{stroke}" stroke-width="1.4"/>')
        lines.append(f'<line x1="{cx-d}" y1="{cy+d}" x2="{cx+d}" y2="{cy-d}" stroke="{stroke}" stroke-width="1.4"/>')
    return "\n".join(lines)
```

---

## 5. The Canonical IPMI Palette & Semantic Assignment

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          THE CANONICAL IPMI PALETTE                         │
├───────────────┬───────────────┬───────────────┬──────────────┬──────────────┤
│  Steel Blue   │   Sage Herb   │  Terracotta   │    Mauve     │  Sand Cream  │
│    #52a0c8    │    #87a256    │    #c46b2e    │   #c2a8c4    │   #cabd9e    │
│  (Encoders/   │  (Proposed/   │    (Loss/     │ (Bottleneck/ │   (Inputs/   │
│   Latents)    │  Innovations) │ Supervision)  │ Aggregations)│ Conditioning)│
└───────────────┴───────────────┴───────────────┴──────────────┴──────────────┘
```

| Functional Role | Fill (Hex) | Stroke (Hex) | Light Tint (Fill) | Dark Text (WCAG) | Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Encoders / Latent Features** | `#52a0c8` | `#1e293b` | `#eef4fa` | `#0f3d5e` | Backbones, feature maps, latent projections |
| **Proposed / Novel Blocks** | `#87a256` | `#3d5548` | `#ddebe1` | `#233d29` | Core novelty (State-Space, De-tilt, Champion model) |
| **Losses / Supervision** | `#c46b2e` | `#8c2d19` | `#fdf3ef` | `#7c2d12` | Objective math, coordinate heads, failure modes |
| **Bottlenecks / Heads** | `#c2a8c4` | `#5f1e9a` | `#f6f0f6` | `#4a1578` | Transformers, multi-task decoders, Soft-Argmax |
| **Inputs / Conditioning** | `#cabd9e` | `#7a716b` | `#fcf8ed` | `#4a4238` | Raw OCT slabs, geometry priors, templates |
| **Accents / Highlights** | `#cea62a` | `#854d0e` | `#fef9c3` | `#713f12` | Multiplier gates, key annotations, callouts |

---

## 6. Typography Hierarchy & CSS Font Stacks

In SVG `<defs>`, define the standard typography stack:
```xml
<style>
  .sans {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; fill: #0f172a; }}
  .sans-bold {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 700; fill: #0f172a; }}
  .sans-semi {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 600; fill: #334155; }}
  .math {{ font-family: 'Times New Roman', Times, Georgia, serif; font-style: italic; fill: #0f172a; }}
  .math-bold {{ font-family: 'Times New Roman', Times, Georgia, serif; font-style: italic; font-weight: 700; fill: #0f172a; }}
  .mono {{ font-family: 'Courier New', Courier, monospace; font-weight: 600; fill: #0f172a; }}
</style>
```

| Element | Size | Weight | Font Class | Baseline Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Panel Titles** | $13\text{--}13.5\,\text{pt}$ | 700 | `.sans-bold` | Top title for `(a)`, `(b)`, `(c)` |
| **Card Header Banners** | $10.8\text{--}11.5\,\text{pt}$ | 700 | `.sans-bold` | Centered or left-aligned card titles |
| **Section Subheaders** | $10\text{--}10.5\,\text{pt}$ | 700 | `.sans-bold` | Group labels inside cards |
| **Body Bullets / Text** | $9.5\text{--}10\,\text{pt}$ | 400 | `.sans` | Metric lists, physical parameters |
| **Equations & Variables** | $9.5\text{--}10.5\,\text{pt}$ | Italic / 700 | `.math`, `.math-bold` | Formulas ($z(y)$, $\nabla_{\mathbf{h}} \mathcal{L}$) |
| **Tensor Shapes / Code** | $9.0\text{--}9.5\,\text{pt}$ | 600 | `.mono` | `(B, K, 768, 320)`, `Conv3d(...)` |

---

## 7. Automated PyMuPDF Vector PDF & 600-DPI PNG Pipeline

All SVG diagrams are compiled to vector PDF and high-res PNG using PyMuPDF:
```python
import fitz  # PyMuPDF
from pathlib import Path

def render_svg_to_pdf_and_png(svg_path: Path, pdf_path: Path, png_path: Path, scale: float = 3.0):
    """
    Renders SVG to vector PDF and 600-DPI-equivalent PNG.
    scale=3.0 on 1400x640 yields 4200x1920 px (crystal-clear print quality).
    """
    doc = fitz.open(str(svg_path))
    pdf_bytes = doc.convert_to_pdf()
    pdf_doc = fitz.open("pdf", pdf_bytes)
    pdf_doc.save(str(pdf_path))
    page = pdf_doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    pix.save(str(png_path))
    doc.close()
    pdf_doc.close()
```

---

## 8. Pre-Flight Checklist Before Submission

Before accepting any figure:
- [ ] **No Matplotlib Box Flowcharts:** Composite methodology diagrams are authored in Programmatic SVG, not Matplotlib boxes.
- [ ] **Zero Text Collisions:** Text baselines are strictly computed; no multi-line labels overlap each other or panel borders.
- [ ] **WCAG Contrast:** Zero dark-on-dark text (no dark red text on black backgrounds). White text only on saturated header banners.
- [ ] **Functional Truth:** No cartoon metaphors (hourglasses, pinched waists, cartoon targets). Curves represent real physical or mathematical functions on calibrated coordinate axes.
- [ ] **Data Grounding:** Qualitative figures feature authentic medical scans with real continuous layer boundaries.
- [ ] **Width & Aspect Ratio:** Aspect ratio is strictly in $[1.9, 2.5]$ (standard $1400 \times 640 = 2.19$). Canvas width scales to $122.0\,\text{mm}$ textwidth.
- [ ] **Background Check:** Outer canvas is pure `#ffffff`.
- [ ] **Resolution:** Vector PDF is direct native vector; raster PNG is strictly $600\,\text{DPI}$ equivalent ($4200 \times 1920\,\text{px}$).
- [ ] **Visual Verification:** Always visually verify generated images via `read_file` on PNG outputs before presentation.
