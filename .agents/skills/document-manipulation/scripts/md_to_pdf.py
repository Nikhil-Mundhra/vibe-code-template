import os
import subprocess
import argparse
import sys
import tempfile
import re
import glob
import shutil


ALERT_ICONS = {
    'NOTE': '<svg class="octicon" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8Zm8-6.5a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13ZM6.5 7.75A.75.75 0 0 1 7.25 7h1a.75.75 0 0 1 .75.75v2.75h.25a.75.75 0 0 1 0 1.5h-2a.75.75 0 0 1 0-1.5h.25v-2h-.25a.75.75 0 0 1-.75-.75ZM8 6a1 1 0 1 1 0-2 1 1 0 0 1 0 2Z"></path></svg>',
    'TIP': '<svg class="octicon" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M8 1.5c-2.363 0-4 1.69-4 3.75 0 .984.424 1.625.984 2.304l.214.253c.223.264.47.556.673.848.284.411.537.896.621 1.49a.75.75 0 0 1-1.484.211c-.04-.282-.163-.547-.37-.847a8.456 8.456 0 0 0-.542-.68c-.084-.1-.173-.205-.268-.32C3.201 7.75 2.5 6.766 2.5 5.25 2.5 2.31 4.863 0 8 0s5.5 2.31 5.5 5.25c0 1.516-.701 2.5-1.328 3.259-.095.115-.184.22-.268.319-.18.213-.362.43-.542.681-.207.3-.33.565-.37.847a.751.751 0 0 1-1.485-.212c.084-.593.337-1.078.621-1.489.203-.292.45-.584.673-.848.075-.088.147-.173.213-.253.561-.679.985-1.32.985-2.304 0-2.06-1.637-3.75-4-3.75ZM5.75 12h4.5a.75.75 0 0 1 0 1.5h-4.5a.75.75 0 0 1 0-1.5ZM6.25 15h3.5a.75.75 0 0 1 0 1.5h-3.5a.75.75 0 0 1 0-1.5Z"></path></svg>',
    'IMPORTANT': '<svg class="octicon" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M0 1.75C0 .784.784 0 1.75 0h12.5C15.216 0 16 .784 16 1.75v9.5A1.75 1.75 0 0 1 14.25 13H8.06l-2.573 2.573A1.458 1.458 0 0 1 3 14.543V13H1.75A1.75 1.75 0 0 1 0 11.25Zm1.75-.25a.25.25 0 0 0-.25.25v9.5c0 .138.112.25.25.25h2a.75.75 0 0 1 .75.75v2.19l2.72-2.72a.749.749 0 0 1 .53-.22h6.5a.25.25 0 0 0 .25-.25v-9.5a.25.25 0 0 0-.25-.25Zm7 2.25v2.5a.75.75 0 0 1-1.5 0v-2.5a.75.75 0 0 1 1.5 0ZM9 9a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"></path></svg>',
    'WARNING': '<svg class="octicon" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M6.457 1.047c.659-1.234 2.427-1.234 3.086 0l6.082 11.378A1.75 1.75 0 0 1 14.082 15H1.918a1.75 1.75 0 0 1-1.543-2.575Zm1.763.707a.25.25 0 0 0-.44 0L1.698 13.132a.25.25 0 0 0 .22.368h12.164a.25.25 0 0 0 .22-.368Zm.53 3.996v2.5a.75.75 0 0 1-1.5 0v-2.5a.75.75 0 0 1 1.5 0ZM9 11a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"></path></svg>',
    'CAUTION': '<svg class="octicon" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M4.47.047A.75.75 0 0 1 5 0h6a.75.75 0 0 1 .53.22l4.25 4.25c.141.14.22.331.22.53v6a.75.75 0 0 1-.22.53l-4.25 4.25A.75.75 0 0 1 11 16H5a.75.75 0 0 1-.53-.22L.22 11.53A.75.75 0 0 1 0 11V5a.75.75 0 0 1 .22-.53Zm.84 1.28L1.5 5.13v5.74l3.81 3.81h5.74l3.81-3.82V5.13L11.05 1.32Zm4.69 3.43v3.5a.75.75 0 0 1-1.5 0v-3.5a.75.75 0 0 1 1.5 0ZM9 11a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"></path></svg>'
}


def preprocess_github_alerts(md_text: str) -> str:
    lines = md_text.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.match(r'^\s*>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\](?:\s*(.*))?$', line, re.IGNORECASE)
        if match:
            alert_type = match.group(1).upper()
            alert_lines = []
            if match.group(2) and match.group(2).strip():
                alert_lines.append(match.group(2).strip())
            i += 1
            while i < len(lines):
                curr = lines[i]
                if re.match(r'^\s*>', curr):
                    stripped = re.sub(r'^\s*>\s?', '', curr)
                    alert_lines.append(stripped)
                    i += 1
                elif curr.strip() == '':
                    if i + 1 < len(lines) and re.match(r'^\s*>', lines[i + 1]):
                        alert_lines.append('')
                        i += 1
                    else:
                        break
                else:
                    break

            inner_content = '\n'.join(alert_lines)
            icon_svg = ALERT_ICONS.get(alert_type, '')
            new_lines.append(f'<div class="markdown-alert markdown-alert-{alert_type.lower()}" markdown="1">')
            new_lines.append(f'<p class="markdown-alert-title">{icon_svg}<span>{alert_type.capitalize()}</span></p>')
            new_lines.append('')
            new_lines.append(inner_content)
            new_lines.append('')
            new_lines.append('</div>')
        else:
            new_lines.append(line)
            i += 1
    return '\n'.join(new_lines)


def optimize_reporting_assets(md_text: str, base_dir: str, theme: str = "light") -> str:
    """
    Optimizes asset links for clinical/scientific reports when matching files exist:
    1. Selects light-theme chart derivatives (_light.png) if requested.
    2. Switches high-res panel PNGs to optimized print JPEG derivatives (_pdf.jpg) to avoid bloated PDFs.
    Falls back gracefully to the original file if optimized variants do not exist on disk.
    """
    if theme == "light":
        # 1. Light-theme analytical charts
        for chart_base in [
            "cohort_raincloud_distributions",
            "cohort_per_scan_forest_plot",
            "baseline_vs_unet_head_to_head",
            "cohort_summary_chart"
        ]:
            def replace_chart(match):
                prefix = match.group(1)
                ext = match.group(2)
                candidate_rel = f"{prefix}_light{ext}"
                candidate_full = os.path.join(base_dir, candidate_rel)
                # If relative or absolute candidate exists, substitute it
                if os.path.exists(candidate_full) or os.path.exists(f"{prefix}_light{ext}"):
                    return f"{prefix}_light{ext}"
                return match.group(0)

            md_text = re.sub(rf"([^\s\)\"']*{re.escape(chart_base)})(\.png)", replace_chart, md_text)

        # 2. Clinical panels compact JPEG derivatives
        def replace_panel(match):
            prefix = match.group(1)
            candidate_rel = f"{prefix}_pdf.jpg"
            candidate_full = os.path.join(base_dir, candidate_rel)
            if os.path.exists(candidate_full) or os.path.exists(f"{prefix}_pdf.jpg"):
                return f"{prefix}_pdf.jpg"
            return match.group(0)

        md_text = re.sub(
            r"((?:[^\s\)\"']*/)?(?:gallery|deep_dive)[^\s\)\"']+)\.png",
            replace_panel,
            md_text,
        )

    return md_text


def clean_clinical_text(text: str) -> str:
    """
    Sanitizes LaTeX fragments, malformed math delimiters, and legacy entity leaks
    into clean, publication-grade UTF-8 text for Markdown, HTML, and PDF engines.
    """
    if not text:
        return ""

    # 1. Clean existing double-escaped or raw entity leaks
    text = text.replace('&amp;#177;', '±').replace('&#177;', '±').replace('&plusmn;', '±')
    text = text.replace('&amp;#181;', 'µ').replace('&#181;', 'µ').replace('&mu;', 'µ')
    text = text.replace('&amp;nbsp;', ' ')

    # 2. Convert LaTeX and math-wrapped units to standard Unicode
    text = re.sub(r'\\?\$?\\mu(?:\s*\\text\{\{?m\}\}?|\s*m)?\\?\$?', 'µm', text)
    text = re.sub(r'\$\s*\\mu\s*\$\s*m', 'µm', text)
    text = re.sub(r'\\mu\\text\{m\}', 'µm', text)
    text = re.sub(r'\\mu m', 'µm', text)

    # 3. Plus-minus signs: $\pm$, \pm
    text = re.sub(r'\\?\$?\\pm\\?\$?', '±', text)

    # 4. Percentile notations: $P_{95}$, P_{95}, P_{{95}}, $P95$
    text = re.sub(r'\\?\$?P_?\{?95\}?\\?\$?', 'P95', text)

    # 5. Common mathematical operators
    # Clean isolated operators in math dollars or text without consuming un-paired dollars
    text = re.sub(r'\$\s*\\le\s*\$', '≤', text)
    text = re.sub(r'\$\s*\\ge\s*\$', '≥', text)
    text = re.sub(r'\$\s*\\times\s*\$', '×', text)
    text = re.sub(r'\$\s*\\to\s*\$', '→', text)
    text = re.sub(r'\$\s*\\approx\s*\$', '≈', text)
    text = re.sub(r'\$\s*\\Delta\s*\$', 'Δ', text)
    text = re.sub(r'(?<![\\a-zA-Z])\\times(?![a-zA-Z])', '×', text)
    text = re.sub(r'(?<![\\a-zA-Z])\\le(?![a-zA-Z])', '≤', text)
    text = re.sub(r'(?<![\\a-zA-Z])\\ge(?![a-zA-Z])', '≥', text)
    text = re.sub(r'(?<![\\a-zA-Z])\\to(?![a-zA-Z])', '→', text)
    text = re.sub(r'(?<![\\a-zA-Z])\\approx(?![a-zA-Z])', '≈', text)
    text = re.sub(r'(?<![\\a-zA-Z])\\Delta(?![a-zA-Z])', 'Δ', text)

    # Clean numbers with times inside dollars: $3.1×$, $3×3$, $3×3×3$
    text = re.sub(r'\$\s*([0-9\.]+)\s*×\s*\$', r'\1×', text)
    text = re.sub(r'\$\s*([0-9\.]+)\s*×\s*([0-9\.]+)\s*\$', r'\1×\2', text)
    text = re.sub(r'\$\s*([0-9\.]+)\s*×\s*([0-9\.]+)\s*×\s*([0-9\.]+)\s*\$', r'\1×\2×\3', text)

    # 6. Clean stray dollar signs and backslashes around units and symbols
    text = re.sub(r'\$\s*µm', 'µm', text)
    text = re.sub(r'µm\s*\$', 'µm', text)
    text = re.sub(r'\$\s*±', '±', text)
    text = re.sub(r'±\s*\$', '±', text)
    text = re.sub(r'\$\s*P95', 'P95', text)
    text = re.sub(r'P95\s*\$', 'P95', text)

    # Solitary numbers wrapped in single dollars: $0.9441$ -> 0.9441
    text = re.sub(r'(?<!\w)\$\s*([0-9\.]+)\s*\$(?!\w)', r'\1', text)

    # 7. Normalize whitespace around operators and units
    text = re.sub(r'\s*±\s*', ' ± ', text)
    text = re.sub(r'([0-9])\s*µm', r'\1 µm', text)

    return text


def protect_and_convert_markdown(md_text: str, base_dir: str = "", theme: str = "light", optimize_assets: bool = True) -> str:
    # 0. Convert pagebreak markers to explicit HTML break containers
    md_text = re.sub(
        r"(?:<!--\s*(?:pagebreak|page-break|newpage)\s*-->|\\pagebreak)",
        r'<div class="page-break" style="page-break-before: always !important; break-before: page !important;"></div>',
        md_text,
        flags=re.IGNORECASE
    )

    # 1. Protect code blocks and inlines so KaTeX and Markdown do not clash
    code_blocks = []
    code_inlines = []

    def save_code_block(m):
        idx = len(code_blocks)
        code_blocks.append(m.group(0))
        return f"@@CODE_BLOCK_{idx}@@"

    def save_code_inline(m):
        idx = len(code_inlines)
        code_inlines.append(m.group(0))
        return f"@@CODE_INLINE_{idx}@@"

    md_text = re.sub(r"(```[\s\S]*?```)", save_code_block, md_text)
    md_text = re.sub(r"(`[^`\n]+?`)", save_code_inline, md_text)

    # 2. Protect LaTeX and math expressions BEFORE text sanitization or markdown mangling
    math_blocks = []
    math_inlines = []

    def save_math_block(m):
        idx = len(math_blocks)
        math_blocks.append(m.group(0))
        return f"@@MATH_BLOCK_{idx}@@"

    def save_math_inline(m):
        idx = len(math_inlines)
        math_inlines.append(m.group(0))
        return f"@@MATH_INLINE_{idx}@@"

    # Block math: $$...$$ or \[...\]
    md_text = re.sub(r"(?<!\\)\$\$([\s\S]+?)(?<!\\)\$\$", save_math_block, md_text)
    md_text = re.sub(r"(?<!\\)\\\[([\s\S]+?)(?<!\\)\\\]", save_math_block, md_text)
    # Inline math: \(...\) or $...$
    md_text = re.sub(r"(?<!\\)\\\(([\s\S]+?)(?<!\\)\\\)", save_math_inline, md_text)
    md_text = re.sub(r"(?<![\$\\])\$(?!\s)([^\$\n]+?)(?<!\s)(?<!\\)\$", save_math_inline, md_text)

    # 3. Clean and sanitize clinical LaTeX fragments, legacy entity leaks, and units on regular text
    md_text = clean_clinical_text(md_text)

    # 4. Preprocess GitHub-style alerts (> [!NOTE], > [!IMPORTANT], etc.)
    md_text = preprocess_github_alerts(md_text)

    # Automated Defensive List Normalization:
    # Guarantees that any list item following a non-blank line gets an injected blank line
    # so CommonMark and sane_lists never collapse list items into run-on paragraph text.
    lines = md_text.split('\n')
    fixed_lines = []
    in_code = False
    list_pattern = re.compile(r'^\s*([*\-+]|\d+\.)\s+')
    for line in lines:
        if line.strip().startswith('```'):
            in_code = not in_code
            fixed_lines.append(line)
            continue
        if not in_code and list_pattern.match(line):
            if fixed_lines:
                prev_line = fixed_lines[-1].strip()
                if prev_line and not list_pattern.match(prev_line):
                    fixed_lines.append('')
        fixed_lines.append(line)
    md_text = '\n'.join(fixed_lines)

    # 5. Restore code blocks and inlines so markdown processes code syntax
    for i, c in enumerate(code_blocks):
        md_text = md_text.replace(f"@@CODE_BLOCK_{i}@@", c)
    for i, c in enumerate(code_inlines):
        md_text = md_text.replace(f"@@CODE_INLINE_{i}@@", c)

    # 5.5. Asset optimizations (report-specific derivatives if available)
    if optimize_assets:
        md_text = optimize_reporting_assets(md_text, base_dir=base_dir, theme=theme)

    # 6. Convert markdown to HTML
    try:
        import markdown
        html_body = markdown.markdown(md_text, extensions=['extra', 'sane_lists', 'md_in_html'])
    except ImportError:
        print("Error: The 'markdown' Python package is not installed. Please run: pip install markdown")
        sys.exit(1)

    # 7. Restore math expressions into HTML
    for i, m in enumerate(math_blocks):
        clean_m = re.sub(r'\\\\([a-zA-Z])', r'\\\1', m)
        html_body = html_body.replace(f"@@MATH_BLOCK_{i}@@", clean_m)
    for i, m in enumerate(math_inlines):
        clean_m = re.sub(r'\\\\([a-zA-Z])', r'\\\1', m)
        html_body = html_body.replace(f"@@MATH_INLINE_{i}@@", clean_m)

    return html_body


def find_browser() -> str | None:
    if sys.platform == 'darwin':
        # Prioritize Playwright chrome-headless-shell to bypass macOS display link latency/hangs
        playwright_candidates = glob.glob(
            os.path.expanduser("~/Library/Caches/ms-playwright/**/chrome-headless-shell"),
            recursive=True
        )
        mac_candidates = playwright_candidates + [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
        for c in mac_candidates:
            if os.path.exists(c) and os.access(c, os.X_OK):
                return c
    elif sys.platform == 'win32':
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            os.path.expandvars(r"%PROGRAMFILES%\Microsoft\Edge\Application\msedge.exe"),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
    else:
        for c in ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"]:
            found = shutil.which(c)
            if found:
                return found
    return None


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to PDF using Headless Chrome with KaTeX math support")
    parser.add_argument('-i', '--input', required=True, help="Path to the input Markdown file")
    parser.add_argument('-o', '--output', required=True, help="Path to the output PDF file")
    parser.add_argument('--title', default=None, help="Custom document title for header/footer (default: filename)")
    parser.add_argument('--theme', default="light", choices=["light", "dark", "raw"], help="Visual theme and asset selection (default: light)")
    parser.add_argument('--no-optimize-assets', action='store_true', help="Disable automated reporting asset optimizations")
    parser.add_argument('--timeout', type=int, default=60, help="Timeout in seconds for PDF generation (default: 60)")
    args = parser.parse_args()

    md_path = os.path.abspath(args.input)
    pdf_path = os.path.abspath(args.output)
    md_dir = os.path.dirname(md_path)

    if not os.path.exists(md_path):
        print(f"Error: Input file '{md_path}' does not exist.")
        sys.exit(1)

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    doc_title = args.title if args.title else os.path.basename(md_path)
    html_body = protect_and_convert_markdown(
        md_text,
        base_dir=md_dir,
        theme=args.theme,
        optimize_assets=(not args.no_optimize_assets)
    )

    md_dir_uri = 'file:///' + md_dir.replace(os.sep, '/') + '/'

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <base href="{md_dir_uri}">
    <title>{os.path.basename(md_path)}</title>
    <!-- KaTeX CSS & JS for Math Typesetting -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
    <script>
        window.addEventListener("load", function() {{
            if (typeof renderMathInElement === "function") {{
                renderMathInElement(document.body, {{
                    delimiters: [
                        {{left: "$$", right: "$$", display: true}},
                        {{left: "\\\\[", right: "\\\\]", display: true}},
                        {{left: "$", right: "$", display: false}},
                        {{left: "\\\\(", right: "\\\\)", display: false}}
                    ],
                    output: 'html',
                    throwOnError: false
                }});
            }}
        }});
    </script>
    <style>
        @page {{
            margin: 0.5in 0.5in;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            color: #24292f;
            line-height: 1.4;
            padding: 0;
            padding-bottom: 15px;
            max-width: 960px;
            margin: 0 auto;
        }}
        ul, ol {{
            margin: 8px 0;
            padding-left: 24px;
        }}
        li {{
            margin-bottom: 4px;
            page-break-inside: avoid;
            break-inside: avoid;
        }}
        p {{
            margin-top: 0;
            margin-bottom: 6px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #1f2328;
            page-break-after: avoid;
            break-after: avoid;
        }}
        h1 {{
            color: #0969da;
            border-bottom: 1px solid #d0d7de;
            padding-bottom: 0.25em;
            margin-top: 0;
            margin-bottom: 12px;
        }}
        h2 {{
            color: #1a7f37;
            border-bottom: 1px solid #d8dee4;
            padding-bottom: 0.25em;
            margin-top: 16px;
            margin-bottom: 8px;
            page-break-inside: avoid;
            break-inside: avoid;
        }}
        .page-break {{
            page-break-before: always !important;
            break-before: page !important;
        }}
        h3 {{
            color: #24292f;
            margin-top: 16px;
            margin-bottom: 8px;
        }}
        code {{
            background-color: rgba(175, 184, 193, 0.2);
            padding: 0.2em 0.4em;
            border-radius: 6px;
            font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
            font-size: 85%;
        }}
        pre {{
            background-color: #f6f8fa;
            padding: 12px 14px;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 83%;
            line-height: 1.4;
            white-space: pre-wrap !important;
            word-break: break-word !important;
            overflow-wrap: break-word !important;
            page-break-inside: avoid;
            break-inside: avoid;
            margin: 12px 0;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
            border-radius: 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0;
            font-size: 10.5px;
            line-height: 1.35;
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }}
        thead {{
            display: table-header-group;
        }}
        tfoot {{
            display: table-footer-group;
        }}
        tr {{
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }}
        th, td {{
            border: 1px solid #d0d7de;
            padding: 4px 7px;
            text-align: left;
            vertical-align: middle;
            word-break: normal;
        }}
        th {{
            background-color: #f6f8fa;
            font-weight: 600;
            color: #1f2328;
            white-space: nowrap;
        }}
        tr:nth-child(2n) {{
            background-color: #f8fafc;
        }}
        .compact-table, table.compact {{
            font-size: 10.5px;
        }}
        .compact-table th, .compact-table td, table.compact th, table.compact td {{
            padding: 3.5px 6px;
            line-height: 1.3;
        }}
        /* KPI Metric Cards & Challenge Grids */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin: 16px 0 20px 0;
            page-break-inside: avoid;
            break-inside: avoid;
        }}
        .kpi-card {{
            background: #0f172a;
            color: white;
            border-radius: 8px;
            padding: 12px 14px;
            border-left: 4px solid #10b981;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            page-break-inside: avoid;
            break-inside: avoid;
        }}
        .kpi-card.amber {{ border-left-color: #f59e0b; }}
        .kpi-card.cyan {{ border-left-color: #06b6d4; }}
        .kpi-card.purple {{ border-left-color: #a855f7; }}
        .kpi-card.blue {{ border-left-color: #3b82f6; }}
        .kpi-title {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            font-weight: 700;
            margin-bottom: 3px;
        }}
        .kpi-value {{
            font-size: 22px;
            font-weight: 800;
            color: #ffffff;
            line-height: 1.1;
            margin-bottom: 3px;
        }}
        .kpi-sub {{
            font-size: 9.5px;
            color: #cbd5e1;
        }}
        .challenge-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin: 14px 0;
            page-break-inside: avoid;
            break-inside: avoid;
        }}
        .challenge-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px;
            page-break-inside: avoid;
            break-inside: avoid;
        }}
        .challenge-title {{
            font-size: 12px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 8px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 4px;
        }}
        .challenge-row {{
            font-size: 10.5px;
            margin-bottom: 5px;
            line-height: 1.4;
        }}
        .badge-red {{
            background: #fee2e2;
            color: #dc2626;
            font-weight: 700;
            padding: 1px 5px;
            border-radius: 3px;
            font-size: 9.5px;
        }}
        .badge-green {{
            background: #dcfce7;
            color: #16a34a;
            font-weight: 700;
            padding: 1px 5px;
            border-radius: 3px;
            font-size: 9.5px;
        }}
        .badge-cyan {{
            background: #e0f2fe;
            color: #0284c7;
            font-weight: 700;
            padding: 1px 5px;
            border-radius: 3px;
            font-size: 9.5px;
        }}
        .badge {{
            display: inline-block;
            padding: 2px 7px;
            font-size: 10.5px;
            font-weight: 600;
            border-radius: 12px;
            line-height: 1.3;
            margin-bottom: 3px;
        }}
        .badge-challenge {{ background-color: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; }}
        .badge-commercial {{ background-color: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }}
        .badge-unet {{ background-color: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }}
        img {{
            max-width: 100%;
            max-height: 5.0in;
            object-fit: contain;
            border: 1px solid #d0d7de;
            border-radius: 6px;
            margin: 10px auto;
            display: block;
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }}
        img + p, p:has(> em:first-child) {{
            font-size: 9.5px;
            line-height: 1.35;
            color: #57606a;
            margin-top: -4px;
            margin-bottom: 12px;
            page-break-before: avoid !important;
            break-before: avoid !important;
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }}
        hr {{
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #d0d7de;
            border: 0;
        }}
        blockquote {{
            margin: 16px 0;
            padding: 0 1em;
            color: #57606a;
            border-left: 0.25em solid #d0d7de;
        }}
        .katex-display {{
            margin: 1em 0;
            overflow-x: auto;
            overflow-y: hidden;
        }}
        /* GitHub Alert Callouts */
        .markdown-alert {{
            padding: 12px 16px;
            margin: 16px 0;
            border-left: 4px solid;
            border-radius: 6px;
            page-break-inside: avoid;
            break-inside: avoid;
        }}
        .markdown-alert-title {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
            font-size: 13.5px;
            line-height: 1.25;
            margin-top: 0;
            margin-bottom: 8px;
        }}
        .markdown-alert-title svg {{
            fill: currentColor;
            flex-shrink: 0;
        }}
        .markdown-alert p:last-child,
        .markdown-alert ul:last-child,
        .markdown-alert ol:last-child {{
            margin-bottom: 0;
        }}
        .markdown-alert ul, .markdown-alert ol {{
            margin-top: 6px;
            margin-bottom: 8px;
            padding-left: 20px;
        }}
        .markdown-alert li {{
            margin-bottom: 4px;
        }}

        /* Alert Variants */
        .markdown-alert-note {{
            border-color: #0969da;
            background-color: #f0f7fe;
            border-top: 1px solid #d0e6fd;
            border-right: 1px solid #d0e6fd;
            border-bottom: 1px solid #d0e6fd;
        }}
        .markdown-alert-note .markdown-alert-title {{
            color: #0969da;
        }}

        .markdown-alert-tip {{
            border-color: #1a7f37;
            background-color: #f0faf2;
            border-top: 1px solid #d1f3d9;
            border-right: 1px solid #d1f3d9;
            border-bottom: 1px solid #d1f3d9;
        }}
        .markdown-alert-tip .markdown-alert-title {{
            color: #1a7f37;
        }}

        .markdown-alert-important {{
            border-color: #8250df;
            background-color: #fbf5fe;
            border-top: 1px solid #eddffc;
            border-right: 1px solid #eddffc;
            border-bottom: 1px solid #eddffc;
        }}
        .markdown-alert-important .markdown-alert-title {{
            color: #8250df;
        }}

        .markdown-alert-warning {{
            border-color: #9a6700;
            background-color: #fffbeb;
            border-top: 1px solid #fef0cd;
            border-right: 1px solid #fef0cd;
            border-bottom: 1px solid #fef0cd;
        }}
        .markdown-alert-warning .markdown-alert-title {{
            color: #9a6700;
        }}

        .markdown-alert-caution {{
            border-color: #cf222e;
            background-color: #fff2f1;
            border-top: 1px solid #fedcdb;
            border-right: 1px solid #fedcdb;
            border-bottom: 1px solid #fedcdb;
        }}
        .markdown-alert-caution .markdown-alert-title {{
            color: #cf222e;
        }}
    </style>
</head>
<body>
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; font-size: 9pt; color: #6e7781; padding-bottom: 5px; background: white;">
        {doc_title} | Nikhil Mundhra
    </div>
    {html_body}
</body>
</html>
"""

    fd, html_path = tempfile.mkstemp(suffix=".html", text=True)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(html_content)

    chrome_path = find_browser()
    if not chrome_path:
        print("Error: No Chromium, Chrome, or Edge executable found.")
        os.remove(html_path)
        sys.exit(1)

    print(f"Browser : {chrome_path}")
    print(f"Input   : {md_path}")
    print(f"Output  : {pdf_path}")
    print("Generating PDF with KaTeX math typesetting...")

    try:
        result = subprocess.run([
            chrome_path,
            '--headless',
            '--disable-gpu',
            '--no-pdf-header-footer',
            '--virtual-time-budget=5000',
            '--run-all-compositor-stages-before-draw',
            f'--print-to-pdf={pdf_path}',
            html_path
        ], capture_output=True, text=True, timeout=args.timeout)

        if result.returncode == 0 and os.path.exists(pdf_path):
            size_kb = os.path.getsize(pdf_path) // 1024
            print(f"\nSUCCESS: {pdf_path} ({size_kb} KB)")
        else:
            print(f"FAIL: Browser exited with code {result.returncode}")
            if result.stderr.strip():
                print(f"       {result.stderr.strip()}")
            sys.exit(1)

    except subprocess.TimeoutExpired:
        print(f"Error: Browser timed out after {args.timeout}s.")
        sys.exit(1)
    except Exception as exc:
        print(f"Exception while generating PDF: {exc}")
        sys.exit(1)
    finally:
        if os.path.exists(html_path):
            os.remove(html_path)


if __name__ == "__main__":
    main()
