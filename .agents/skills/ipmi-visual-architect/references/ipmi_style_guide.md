# IPMI Visual Style Guide & Empirical Analysis Reference

This reference document compiles empirical data and design principles extracted directly from the canonical proceedings volume:
**Information Processing in Medical Imaging (IPMI 2026)**  
*Lecture Notes in Computer Science (LNCS)*, Vol. 14644  
ISBN: `978-3-031-96628-6` · Springer Nature Switzerland

---

## 1. Empirical Volume Statistics

* **Total Pages:** 401
* **Total Papers Analyzed:** 29 peer-reviewed publications
* **Total Figures Detected:** 115 figures
* **Total Embedded Raster Placements:** 138 image placements
* **Page Dimensions:** $152 \times 235\,\text{mm}$ ($439.4 \times 666.1\,\text{pt}$)
* **Single-Column Text Width (`\textwidth`):** $122.0\,\text{mm}$ ($348.4\,\text{pt}$)

### Raster Resolution Distribution (DPI)
```
DPI Range               Image Placements      Percentage
────────────────────────────────────────────────────────
500 – 1000 DPI (600 DPI target)    115 images       83.3%
250 – 500 DPI                      23 images       16.7%
0 – 250 DPI                         0 images        0.0%
────────────────────────────────────────────────────────
Median DPI: 599.3 DPI | Mean DPI: 552.3 DPI | Max: 600.0 DPI
```

### Figure Width Distribution
```
Span Relative to \textwidth        Figure Count     Percentage
────────────────────────────────────────────────────────
95% – 100% (330 – 348.4 pt)         82 figures       71.3%
80% – 95%  (280 – 330 pt)           28 figures       24.3%
< 80% (Narrow/half-width)            5 figures        4.4%
────────────────────────────────────────────────────────
Median Width: 311.4 pt (~89.4% of textwidth)
```

---

## 2. Dominant Architectural Color Palette Clusters

K-Means clustering across chromatic elements in prominent architecture figures:

| Cluster Role | Hex Code | RGB | % Colored Pixels | Benchmark Reference Paper |
| :--- | :--- | :--- | :---: | :--- |
| **Encoder / Latent State** | `#52a0c8` | $(82, 160, 200)$ | $18.4\%$ | *Cor2Vox Brownian Bridge* (p. 203) |
| **Proposed Novelty / Student** | `#87a256` | $(135, 162, 86)$ | $15.1\%$ | *Vascular Topology Learning* (p. 112) |
| **Proposed Attention Block** | `#8dc256` | $(141, 194, 86)$ | $24.3\%$ | *Cor2Vox Brownian Bridge* (p. 203) |
| **Loss / Gradient Surgery** | `#c46b2e` | $(196, 107, 46)$ | $21.5\%$ | *Cor2Vox Brownian Bridge* (p. 203) |
| **Distillation / Teacher Net** | `#c48e7c` | $(196, 142, 124)$ | $33.9\%$ | *SpectMamba* (p. 24) |
| **Cellular State / Bottleneck** | `#c2a8c4` | $(194, 168, 196)$ | $42.7\%$ | *Hierarchical NCA (hNCA)* (p. 39) |
| **Anchor Weights / Matchings** | `#cea62a` | $(206, 166, 42)$ | $24.4\%$ | *Vascular Topology Learning* (p. 112) |
| **Conditioning Priors / SDF** | `#cabd9e` | $(202, 189, 158)$ | $30.2\%$ | *GSSD Registration* (p. 82) |

---

## 3. Typology Benchmark Index in `978-3-031-96628-6.pdf`

| Typology | Representative Figure | Page | Key Visual Attributes |
| :--- | :--- | :--- | :--- |
| **Macro/Micro Architecture** | SpectMamba (Fig. 1) | p. 24 | Panel (a) macro flow, panels (b)-(e) micro frequency/Mamba blocks, rounded cards, isometric slabs. |
| **Macro/Micro Architecture** | hNCA (Fig. 1) | p. 39 | Multi-scale cellular automata stages, pooling connectors, neighborhood perception loops. |
| **Teacher-Student Pipeline** | GSSD (Fig. 1 & 2) | p. 82–83 | Teacher network cascade, gradient surgery projection diagrams with vector dot products. |
| **Vascular Graph Matching** | Deep Structure Matching (Fig. 3) | p. 113 | 2D DSA and 3D CTA point cloud matching, topology-aware branch trimming, colored correspondence lines. |
| **Continuous Reconstruction** | Ground-Truth-Free Flow Matching (Fig. 1) | p. 144 | Commutative inference diagram, continuous de-aliasing paths, probabilistic variable nodes. |
| **Shape Diffusion** | Cor2Vox Brownian Bridge (Fig. 1 & 3) | p. 201, 204 | 3D cortical SDF priors, forward/reverse diffusion bridge, 3D UNet backbone. |
| **Manifold / Lie Geometry** | Bi-invariant Geodesics on SE(3) (Fig. 1) | p. 74 | 3D reference paper airplane undergoing rigid Euclidean and Riemannian actions. |
| **Qualitative Registration** | SAM-assisted Registration (Fig. 3) | p. 106 | Cardiac MRI & Abdomen CT multi-class contour overlays (LV, Myo, RV) with boundary zoom. |
| **Qualitative Registration** | Nonparametric Smoothing (Fig. 4) | p. 133 | Inferno (fixed) and Viridis (moving) dual-colormap overlay, deformation vector fields. |
| **Reconstruction Zoom-Ins** | Accelerated MRI Recon (Fig. 2 & 4) | p. 152–153 | Full slice with colored bounding box, magnified ROI panel, residual error difference maps. |
| **Statistical Boxplots** | Anatomical Structure Errors (Fig. 4) | p. 88 | Grouped boxplots ranked by structure voxel volume, median line, whisker spreads. |
