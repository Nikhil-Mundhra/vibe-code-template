#!/usr/bin/env python3
"""
rasterize_svg.py
================
CLI utility for validating, dimension-fixing, and rasterizing scientific SVG
diagrams into high-resolution Retina PNGs using PyMuPDF (fitz).

Guarantees:
- Direct vector-to-raster rendering with zero heuristic letterboxing
- Zero blind canvas cropping (preserves headers, footers, and margins intact)
- Exact aspect ratio preservation matching the SVG's viewBox
- Automated XML validation and root dimension checks

Usage:
  python3 rasterize_svg.py rasterize path/to/diagram.svg [--width 3200]
  python3 rasterize_svg.py rasterize path/to/svg_dir/ [--width 3200]
  python3 rasterize_svg.py validate path/to/diagram.svg
  python3 rasterize_svg.py fix-dimensions path/to/diagram.svg
"""

import argparse
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def parse_viewbox(viewbox_str):
    """Extract (min_x, min_y, width, height) from a viewBox attribute string."""
    if not viewbox_str:
        return None
    parts = [float(p) for p in re.split(r"[\s,]+", viewbox_str.strip()) if p]
    if len(parts) == 4:
        return parts
    return None


def validate_svg(svg_path):
    """
    Validates an SVG file:
    1. Valid XML syntax
    2. Presence of viewBox
    3. Explicit pixel width and height matching viewBox
    4. Warning if width="100%" or height="100%"
    """
    errors = []
    warnings = []

    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except Exception as e:
        return False, [f"Invalid XML syntax: {e}"], []

    tag = root.tag
    if not tag.endswith("svg"):
        return False, [f"Root element is <{tag}>, expected <svg>"], []

    viewbox = root.get("viewBox")
    width = root.get("width")
    height = root.get("height")

    if not viewbox:
        errors.append("Missing 'viewBox' attribute on root <svg> element.")
    else:
        vb_parts = parse_viewbox(viewbox)
        if not vb_parts:
            errors.append(f"Invalid 'viewBox' format: '{viewbox}'")
        else:
            _, _, vb_w, vb_h = vb_parts
            if width in ("100%", None) or height in ("100%", None):
                warnings.append(
                    f"Root <svg> has relative or missing dimensions (width='{width}', height='{height}'). "
                    f"PyMuPDF and third-party renderers will fall back to default letter paper (612x792 pt). "
                    f"Set explicit dimensions: width='{int(vb_w)}' height='{int(vb_h)}'."
                )
            else:
                try:
                    w_num = float(re.sub(r"[^\d.]", "", width))
                    h_num = float(re.sub(r"[^\d.]", "", height))
                    if abs(w_num - vb_w) > 1.0 or abs(h_num - vb_h) > 1.0:
                        warnings.append(
                            f"Dimension mismatch: width='{width}'/height='{height}' vs viewBox '{viewbox}'. "
                            "May cause distortion or padding in some renderers."
                        )
                except ValueError:
                    warnings.append(f"Non-numeric dimension values: width='{width}', height='{height}'.")

    # Scan for long single-line text that might overflow containers
    for elem in root.iter():
        if elem.tag.endswith("text") and elem.text:
            text = elem.text.strip()
            font_size = elem.get("font-size")
            font_family = elem.get("font-family", "")
            if len(text) > 65 and ("monospace" in font_family or "Mono" in font_family):
                warnings.append(
                    f"Potential text overflow: text '{text[:35]}...' has {len(text)} monospace characters. "
                    "Ensure container width is sufficient or wrap across multiple lines."
                )

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def fix_dimensions(svg_path):
    """
    Ensures root <svg> has explicit width and height matching its viewBox.
    """
    with open(svg_path, "r", encoding="utf-8") as f:
        content = f.read()

    vb_match = re.search(r'viewBox=["\']([^"\']+)["\']', content)
    if not vb_match:
        print(f"[-] Cannot fix {svg_path}: No viewBox attribute found.", file=sys.stderr)
        return False

    vb_parts = parse_viewbox(vb_match.group(1))
    if not vb_parts:
        print(f"[-] Cannot fix {svg_path}: Invalid viewBox format '{vb_match.group(1)}'.", file=sys.stderr)
        return False

    _, _, vb_w, vb_h = vb_parts
    w_str = f"{int(vb_w)}" if vb_w.is_integer() else f"{vb_w}"
    h_str = f"{int(vb_h)}" if vb_h.is_integer() else f"{vb_h}"

    # Replace width and height attributes in root <svg ...> tag
    svg_tag_match = re.search(r"<svg\b[^>]*>", content)
    if not svg_tag_match:
        print(f"[-] Cannot fix {svg_path}: <svg> tag not found.", file=sys.stderr)
        return False

    old_tag = svg_tag_match.group(0)
    new_tag = old_tag

    # Update or add width
    if re.search(r'\bwidth=["\'][^"\']*["\']', new_tag):
        new_tag = re.sub(r'\bwidth=["\'][^"\']*["\']', f'width="{w_str}"', new_tag)
    else:
        new_tag = re.sub(r"<svg\b", f'<svg width="{w_str}"', new_tag)

    # Update or add height
    if re.search(r'\bheight=["\'][^"\']*["\']', new_tag):
        new_tag = re.sub(r'\bheight=["\'][^"\']*["\']', f'height="{h_str}"', new_tag)
    else:
        new_tag = re.sub(r"<svg\b", f'<svg height="{h_str}"', new_tag)

    if new_tag != old_tag:
        content = content[: svg_tag_match.start()] + new_tag + content[svg_tag_match.end() :]
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[+] Fixed dimensions for {svg_path}: width='{w_str}' height='{h_str}'")
        return True
    else:
        print(f"[*] Dimensions already match viewBox for {svg_path}.")
        return False


def rasterize_single(svg_path, out_png_path=None, target_width=3200):
    """
    Renders an SVG to a high-resolution Retina PNG via PyMuPDF.
    """
    if fitz is None:
        raise RuntimeError("PyMuPDF (fitz) is not installed. Please install with: pip install pymupdf")

    if out_png_path is None:
        out_png_path = os.path.splitext(svg_path)[0] + ".png"

    # Pre-check dimensions
    _, errors, warnings = validate_svg(svg_path)
    for w in warnings:
        if "relative or missing dimensions" in w:
            print(f"[!] Warning for {svg_path}: {w}", file=sys.stderr)
            print("[*] Automatically fixing dimensions to match viewBox...", file=sys.stderr)
            fix_dimensions(svg_path)

    doc = fitz.open(svg_path)
    page = doc[0]
    rect = page.rect

    if rect.width <= 0 or rect.height <= 0:
        raise ValueError(f"Invalid page rectangle {rect} for {svg_path}")

    scale = float(target_width) / float(rect.width)
    mat = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=mat)

    os.makedirs(os.path.dirname(os.path.abspath(out_png_path)), exist_ok=True)
    pix.save(out_png_path)
    print(f"[+] Rendered Retina PNG: {out_png_path} ({pix.width}x{pix.height} px, scale={scale:.2f}x)")
    return out_png_path


def main():
    parser = argparse.ArgumentParser(
        description="Scientific SVG Validator and High-Resolution PyMuPDF Rasterizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # rasterize
    p_rast = subparsers.add_parser("rasterize", help="Rasterize SVG(s) to crisp Retina PNG(s)")
    p_rast.add_argument("target", help="Path to an SVG file or directory containing SVGs")
    p_rast.add_argument("--width", type=int, default=3200, help="Target PNG width in pixels (default: 3200)")
    p_rast.add_argument("--out", "-o", help="Optional output PNG path (or directory if target is a directory)")

    # validate
    p_val = subparsers.add_parser("validate", help="Validate SVG XML, dimensions, and potential text overflows")
    p_val.add_argument("target", help="Path to an SVG file or directory containing SVGs")

    # fix-dimensions
    p_fix = subparsers.add_parser("fix-dimensions", help="Ensure root <svg> has explicit width/height matching viewBox")
    p_fix.add_argument("target", help="Path to an SVG file or directory containing SVGs")

    args = parser.parse_args()

    # Collect target files
    if os.path.isdir(args.target):
        svg_files = sorted(glob.glob(os.path.join(args.target, "*.svg")))
        if not svg_files:
            print(f"[-] No .svg files found in directory: {args.target}", file=sys.stderr)
            sys.exit(1)
    elif os.path.isfile(args.target):
        svg_files = [args.target]
    else:
        print(f"[-] Target does not exist: {args.target}", file=sys.stderr)
        sys.exit(1)

    if args.command == "validate":
        total = len(svg_files)
        valid_count = 0
        for f in svg_files:
            ok, errors, warnings = validate_svg(f)
            if ok and not warnings:
                print(f"[✓ PASS] {f}")
                valid_count += 1
            else:
                status = "[✓ PASS w/ WARNINGS]" if ok else "[✗ FAIL]"
                print(f"{status} {f}")
                for e in errors:
                    print(f"    ERROR: {e}")
                for w in warnings:
                    print(f"    WARN:  {w}")
                if ok:
                    valid_count += 1
        print(f"\nValidation complete: {valid_count}/{total} files valid.")
        if valid_count < total:
            sys.exit(1)

    elif args.command == "fix-dimensions":
        for f in svg_files:
            fix_dimensions(f)

    elif args.command == "rasterize":
        for f in svg_files:
            if args.out and len(svg_files) == 1 and not os.path.isdir(args.out):
                out_path = args.out
            elif args.out and os.path.isdir(args.out):
                out_path = os.path.join(args.out, os.path.splitext(os.path.basename(f))[0] + ".png")
            else:
                out_path = None
            rasterize_single(f, out_png_path=out_path, target_width=args.width)


if __name__ == "__main__":
    main()
