#!/usr/bin/env python3
"""
Canonical IPMI / Springer LNCS Vector SVG Figure Template
International Conference on Information Processing in Medical Imaging (IPMI)
"""
import math
from pathlib import Path
import fitz  # PyMuPDF

PALETTE = {
    "canvas_bg": "#ffffff",
    "panel_bg": "#f8fafc",
    "panel_border": "#cbd5e1",
    "text_main": "#0f172a",
    "text_sub": "#334155",
    "text_muted": "#64748b",
    "charcoal": "#1e293b",
    "blue_fill": "#52a0c8",
    "blue_light": "#b4c3de",
    "blue_tint": "#eef4fa",
    "blue_stroke": "#1e293b",
    "blue_text": "#0f3d5e",
    "green_fill": "#87a256",
    "green_light": "#b5cba8",
    "green_tint": "#ddebe1",
    "green_stroke": "#3d5548",
    "green_text": "#233d29",
    "terra_fill": "#c46b2e",
    "terra_light": "#eac9be",
    "terra_tint": "#fdf3ef",
    "terra_stroke": "#8c2d19",
    "terra_text": "#7c2d12",
    "mauve_fill": "#c2a8c4",
    "mauve_light": "#ddcddd",
    "mauve_tint": "#f6f0f6",
    "mauve_stroke": "#5f1e9a",
    "mauve_text": "#4a1578",
    "cream_fill": "#cabd9e",
    "cream_light": "#efe6d5",
    "cream_tint": "#fcf8ed",
    "cream_stroke": "#7a716b",
    "cream_text": "#4a4238",
    "gold_fill": "#cea62a",
    "gold_light": "#fef9c3",
    "gold_stroke": "#854d0e",
    "gold_text": "#713f12",
}

def svg_header(width: int = 1400, height: int = 640) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <style>
      .sans {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; fill: {PALETTE['text_main']}; }}
      .sans-bold {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 700; fill: {PALETTE['text_main']}; }}
      .sans-semi {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 600; fill: {PALETTE['text_sub']}; }}
      .math {{ font-family: 'Times New Roman', Times, Georgia, serif; font-style: italic; fill: {PALETTE['text_main']}; }}
      .math-bold {{ font-family: 'Times New Roman', Times, Georgia, serif; font-style: italic; font-weight: 700; fill: {PALETTE['text_main']}; }}
      .mono {{ font-family: 'Courier New', Courier, monospace; font-weight: 600; fill: {PALETTE['text_main']}; }}
    </style>
  </defs>
  <rect width="{width}" height="{height}" fill="{PALETTE['canvas_bg']}"/>
"""

def arrow_line(x1: float, y1: float, x2: float, y2: float, color: str = "#1e293b", width: float = 1.5, dashed: bool = False, head_len: float = 7.5, head_w: float = 4.2) -> str:
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
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{lx2:.1f}" y2="{ly2:.1f}" stroke="{color}" stroke-width="{width}"{dash}/>\n<polygon points="{x2:.1f},{y2:.1f} {p1x:.1f},{p1y:.1f} {p2x:.1f},{p2y:.1f}" fill="{color}"/>'

def iso_cuboid(x: float, y: float, w: float, h: float, dx: float, dy: float, front_fill: str, top_fill: str, side_fill: str, stroke: str, stroke_w: float = 1.2) -> str:
    front = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{front_fill}" stroke="{stroke}" stroke-width="{stroke_w}" stroke-linejoin="round"/>'
    top = f'<polygon points="{x},{y} {x+dx},{y-dy} {x+w+dx},{y-dy} {x+w},{y}" fill="{top_fill}" stroke="{stroke}" stroke-width="{stroke_w}" stroke-linejoin="round"/>'
    side = f'<polygon points="{x+w},{y} {x+w+dx},{y-dy} {x+w+dx},{y+h-dy} {x+w},{y+h}" fill="{side_fill}" stroke="{stroke}" stroke-width="{stroke_w}" stroke-linejoin="round"/>'
    return f"<g>{top}{side}{front}</g>"

def math_op_node(cx: float, cy: float, r: float, symbol: str, stroke: str = "#1e293b", fill: str = "#ffffff") -> str:
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

def render_svg_to_pdf_and_png(svg_path: Path, pdf_path: Path, png_path: Path, scale: float = 3.0):
    doc = fitz.open(str(svg_path))
    pdf_bytes = doc.convert_to_pdf()
    pdf_doc = fitz.open("pdf", pdf_bytes)
    pdf_doc.save(str(pdf_path))
    page = pdf_doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    pix.save(str(png_path))
    doc.close()
    pdf_doc.close()
    print(f"[+] Rendered vector PDF ({pdf_path.name}) & 600-DPI PNG ({png_path.name})")
