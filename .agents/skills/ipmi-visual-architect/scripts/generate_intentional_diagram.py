#!/usr/bin/env python3
"""
Generate a truly INTENTIONAL, MINIMALIST, PUBLICATION-GRADE IPMI Diagram for Theorem 1.
Core Principle:
  "A diagram is a visualization. If there's math that could be visualized, the diagram fails."
  - Replaces equations in boxes with physical forces, geometric membranes, and visual evaporation.
  - Sized to exact Springer LNCS single-column textwidth: 122.0 mm (348.4 pt)
  - Pure SVG vector primitives rendered via PyMuPDF to 600 DPI PDF and PNG.
"""

import os
import pymupdf

def build_intentional_svg():
    # Width: 1000 px, Height: 480 px (Aspect ratio ~ 2.08 : 1, ideal for ~24% page budget)
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 480" width="1000" height="480">
  <defs>
    <!-- Gradients -->
    <!-- Evaporation Gradient: Green fill that fades out into transparent void as lamina thins -->
    <linearGradient id="evaporate-mask" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#22c55e" stop-opacity="0.70" />
      <stop offset="42%" stop-color="#22c55e" stop-opacity="0.65" />
      <stop offset="58%" stop-color="#4ade80" stop-opacity="0.35" />
      <stop offset="72%" stop-color="#ef4444" stop-opacity="0.10" />
      <stop offset="85%" stop-color="#ef4444" stop-opacity="0.0" />
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.0" />
    </linearGradient>

    <!-- Outward Gradient Force Arrow (Terracotta) -->
    <linearGradient id="grad-pull" x1="0%" y1="100%" x2="0%" y2="0%">
      <stop offset="0%" stop-color="#ea580c" />
      <stop offset="100%" stop-color="#c2410c" />
    </linearGradient>

    <!-- Depleted Core Gradient -->
    <radialGradient id="depleted-core" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="1.0" />
      <stop offset="60%" stop-color="#f8fafc" stop-opacity="0.8" />
      <stop offset="100%" stop-color="#e2e8f0" stop-opacity="0.2" />
    </radialGradient>

    <!-- Arrowhead Markers -->
    <marker id="arrow-pull" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#c2410c" />
    </marker>
    <marker id="arrow-faint" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#16a34a" />
    </marker>
    <marker id="arrow-neutral" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
      <path d="M 0 2 L 8 5 L 0 8 z" fill="#64748b" />
    </marker>
  </defs>

  <style>
    .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 13.5px; font-weight: 700; fill: #0f172a; }
    .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 10.5px; font-weight: 500; fill: #64748b; }
    .label-bold { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 11px; font-weight: 700; }
    .label-reg { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 10px; font-weight: 500; fill: #334155; }
    .metric-value { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 11.5px; font-weight: 700; }
    .callout-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 9.5px; font-weight: 600; }
  </style>

  <!-- Canvas Background -->
  <rect width="1000" height="480" fill="#ffffff" />

  <!-- Subtle Center Dividing Hairline -->
  <line x1="485" y1="35" x2="485" y2="445" stroke="#f1f5f9" stroke-width="1.5" stroke-dasharray="4 4" />


  <!-- ========================================================================= -->
  <!-- LEFT PANEL: THE CAUSE — OUTWARD TENSION ON THE FEATURE MEMBRANE           -->
  <!-- ========================================================================= -->

  <!-- Panel Title -->
  <text x="35" y="45" class="title">(a) Force Dynamics on Shared Decoder Features</text>
  <text x="35" y="62" class="subtitle">Boundary loss pulls outward with 50× force, stretching the center into hollow depletion</text>

  <!-- The Stretched Feature Column (Membrane) -->
  <!-- Outer Column Boundary -->
  <g transform="translate(140, 95)">
    <!-- Stretched Column Envelope: Narrow pinched waist in center -->
    <path d="M 40 40 
             C 40 90, 75 125, 75 160 
             C 75 195, 40 230, 40 280 
             L 160 280 
             C 160 230, 125 195, 125 160 
             C 125 125, 160 90, 160 40 Z" 
          fill="url(#depleted-core)" stroke="#cbd5e1" stroke-width="1.2" />

    <!-- Top Boundary Anchor (ILM) -->
    <rect x="25" y="32" width="150" height="8" rx="3" fill="#dc2626" />
    <circle cx="100" cy="36" r="4.5" fill="#ffffff" stroke="#dc2626" stroke-width="2" />
    <text x="185" y="40" class="label-bold" fill="#dc2626">ILM Boundary Surface</text>

    <!-- Bottom Boundary Anchor (NFL) -->
    <rect x="25" y="280" width="150" height="8" rx="3" fill="#ea580c" />
    <circle cx="100" cy="284" r="4.5" fill="#ffffff" stroke="#ea580c" stroke-width="2" />
    <text x="185" y="288" class="label-bold" fill="#ea580c">NFL Boundary Surface</text>

    <!-- OUTWARD FORCE ARROWS (Massive Pull of L_coord) -->
    <!-- Top Outward Pull -->
    <line x1="100" y1="30" x2="100" y2="-12" stroke="#c2410c" stroke-width="4.5" marker-end="url(#arrow-pull)" />
    <text x="100" y="-20" class="label-bold" fill="#c2410c" text-anchor="middle">50× Boundary Tension (L_coord ∝ 768 px)</text>

    <!-- Bottom Outward Pull -->
    <line x1="100" y1="290" x2="100" y2="332" stroke="#c2410c" stroke-width="4.5" marker-end="url(#arrow-pull)" />
    <text x="100" y="350" class="label-bold" fill="#c2410c" text-anchor="middle">Outward Boundary Tension</text>

    <!-- INWARD INFLATION ARROWS (Tiny Faint Force of L_mask) -->
    <line x1="100" y1="130" x2="100" y2="150" stroke="#16a34a" stroke-width="1.4" stroke-dasharray="2 2" marker-end="url(#arrow-faint)" />
    <line x1="100" y1="190" x2="100" y2="170" stroke="#16a34a" stroke-width="1.4" stroke-dasharray="2 2" marker-end="url(#arrow-faint)" />

    <!-- Center Depleted Void Callout -->
    <circle cx="100" cy="160" r="16" fill="none" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="3 3" />
    <text x="100" y="157" class="label-bold" fill="#b91c1c" text-anchor="middle" font-size="9px">Interior Void</text>
    <text x="100" y="169" class="callout-text" fill="#b91c1c" text-anchor="middle" font-size="8px">Logits &lt; 0.5</text>
    <text x="-80" y="164" class="label-reg" fill="#64748b" text-anchor="start">Weak Voxel Fill (≤ 1.0)</text>
    <line x1="38" y1="160" x2="72" y2="160" stroke="#94a3b8" stroke-width="0.8" marker-end="url(#arrow-neutral)" />
  </g>

  <!-- Bottom Explanatory Summary Tag for Left -->
  <g transform="translate(45, 415)">
    <rect width="400" height="34" rx="6" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1" />
    <text x="15" y="21" class="label-reg" fill="#334155">
      <tspan font-weight="700" fill="#0f172a">Geometric Polarization:</tspan> Surface loss overpowers voxel loss, depleting the core.
    </text>
  </g>


  <!-- ========================================================================= -->
  <!-- RIGHT PANEL: THE EFFECT — TAPERING RETINAL WEDGE & VOXEL EVAPORATION      -->
  <!-- ========================================================================= -->

  <!-- Panel Title -->
  <text x="515" y="45" class="title">(b) Consequence: Peripheral Mask Evaporation</text>
  <text x="515" y="62" class="subtitle">Boundary lines track with sub-micron precision, but voxel mask vanishes in thin columns</text>

  <!-- The Tapering Anatomical Retinal Slab -->
  <g transform="translate(515, 115)">
    <!-- Underlying Realistic Retinal Speckle Silhouette -->
    <!-- Retinal Slab Path: Thick at left (y: 30 to 180 = 150px), Tapering to right (y: 95 to 115 = 20px) -->
    
    <!-- 1. The Voxel Probability Fill (Uses Evaporation Gradient) -->
    <path d="M 20 40 
             C 120 45, 240 75, 420 98
             L 420 114
             C 240 145, 120 185, 20 190 Z" 
          fill="url(#evaporate-mask)" />

    <!-- 2. Top Continuous Boundary Curve (ILM) — Crisp Solid Red -->
    <path d="M 20 40 C 120 45, 240 75, 420 98" 
          fill="none" stroke="#dc2626" stroke-width="2.6" stroke-linecap="round" />

    <!-- 3. Bottom Continuous Boundary Curve (NFL) — Crisp Dashed Orange -->
    <path d="M 20 190 C 120 185, 240 145, 420 114" 
          fill="none" stroke="#ea580c" stroke-width="2.6" stroke-dasharray="5 3" stroke-linecap="round" />

    <!-- Region Indicators -->
    <!-- Thick Region Indicator (Left) -->
    <line x1="80" y1="205" x2="80" y2="235" stroke="#94a3b8" stroke-width="1" />
    <text x="80" y="248" class="label-bold" fill="#15803d" text-anchor="middle">Thick Lamina (50 µm)</text>
    <text x="80" y="260" class="callout-text" fill="#64748b" text-anchor="middle">Mask Intact (Dice = 0.95)</text>

    <!-- Thin Dropout Zone Indicator (Right) -->
    <line x1="360" y1="125" x2="360" y2="215" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="2 2" />
    <circle cx="360" cy="106" r="14" fill="none" stroke="#ef4444" stroke-width="1.5" />
    <text x="360" y="230" class="label-bold" fill="#dc2626" text-anchor="middle">Thin Lamina (&lt; 15 µm)</text>
    <text x="360" y="244" class="label-bold" fill="#b91c1c" text-anchor="middle">77.1% Column Dropout</text>
    <text x="360" y="258" class="callout-text" fill="#64748b" text-anchor="middle">Mask Evaporates (Dice = 0.26)</text>

    <!-- Caliper Inspection on Thin Zone: Pinpoint Precision -->
    <path d="M 435 96 L 442 96 L 442 116 L 435 116" fill="none" stroke="#dc2626" stroke-width="1.2" />
    <line x1="442" y1="106" x2="455" y2="106" stroke="#dc2626" stroke-width="1" />
    <text x="458" y="103" class="label-bold" fill="#dc2626" font-size="9px">Boundaries Locked</text>
    <text x="458" y="113" class="callout-text" fill="#15803d" font-size="8.5px">MABE &lt; 2.5 µm</text>
  </g>

  <!-- The Discrepancy Scoreboard at Bottom Right -->
  <g transform="translate(515, 415)">
    <rect width="445" height="34" rx="6" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1" />
    
    <text x="18" y="21" class="label-bold" fill="#0f172a">The Paradox:</text>
    
    <!-- Surface Dice -->
    <text x="110" y="21" class="label-reg" fill="#475569">Surface Caliper Dice:</text>
    <text x="218" y="21" class="metric-value" fill="#15803d">0.9252</text>
    
    <!-- Voxel Dice -->
    <text x="282" y="21" class="label-reg" fill="#475569">Voxel Fill Dice:</text>
    <text x="362" y="21" class="metric-value" fill="#dc2626">0.2645</text>
  </g>

</svg>
"""
    return svg

def save_diagram():
    out_dir = "/Users/nikhilmundhra/Documents/Github/Capstone/ML-Research-OCT/ipmi2027"
    svg_str = build_intentional_svg()
    
    # 1. Save SVG
    svg_path = os.path.join(out_dir, "fig_theorem1_intentional.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_str)
        
    # 2. Compile directly to Vector PDF via PyMuPDF
    doc = pymupdf.open("svg", svg_str.encode("utf-8"))
    pdf_bytes = doc.convert_to_pdf()
    pdf_path = os.path.join(out_dir, "fig_theorem1_intentional.pdf")
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
        
    # 3. Render directly to 600 DPI Retina PNG
    doc_pdf = pymupdf.open("pdf", pdf_bytes)
    page = doc_pdf[0]
    # Standard LNCS textwidth is 348.4 pt (~4.838 in)
    # The SVG viewBox is 1000 x 480.
    # At 600 DPI, target width is 4.838 * 600 = 2902 px.
    # Scale factor = 2902 / 1000 = 2.902
    mat = pymupdf.Matrix(2.902, 2.902)
    pix = page.get_pixmap(matrix=mat)
    png_path = os.path.join(out_dir, "fig_theorem1_intentional.png")
    pix.save(png_path)
    
    print(f"Generated truly intentional publication-grade diagram:")
    print(f"  - SVG: {svg_path}")
    print(f"  - PDF: {pdf_path}")
    print(f"  - PNG: {png_path} ({pix.width}x{pix.height} at 600 DPI)")

if __name__ == '__main__':
    save_diagram()
