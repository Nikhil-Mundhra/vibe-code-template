"""
IPMI Color Palette & Visual Style Utilities
International Conference on Information Processing in Medical Imaging (Springer LNCS)
"""

import matplotlib.pyplot as plt
from contextlib import contextmanager

# Springer LNCS Page Geometry Constants
LNCS_TEXTWIDTH_PT = 348.4       # Points
LNCS_PAGEWIDTH_PT = 439.4       # Points
LNCS_PAGEHEIGHT_PT = 666.1      # Points
LNCS_TEXTWIDTH_IN = 348.4 / 72  # ~4.838 inches

# Canonical IPMI Color Palette (Muted Pastels & Earth Mid-Tones)
IPMI_COLORS = {
    # 1. Encoders, Feature Backbones, Latent Representations
    'blue_fill': '#52a0c8',
    'blue_stroke': '#1e293b',
    'blue_tint': '#b4c3de',
    
    # 2. Proposed Novel Modules, Attention Blocks, Student Networks
    'green_fill': '#87a256',
    'green_stroke': '#3d5548',
    'green_tint': '#ddebe1',
    'green_accent': '#9ec16d',
    
    # 3. Objective Math, Supervision, Teacher Networks, Loss Constraints
    'terracotta_fill': '#c46b2e',
    'terracotta_stroke': '#8c2d19',
    'terracotta_tint': '#eac9be',
    'terracotta_accent': '#ed9a54',
    
    # 4. Transformers, Cross-Attention, Bottlenecks, Hypernetworks
    'mauve_fill': '#c2a8c4',
    'mauve_stroke': '#5f1e9a',
    'mauve_tint': '#ddcddd',
    'mauve_accent': '#af65bc',
    
    # 5. Anatomical Priors, Inputs, Baseline Conditioning, SDFs
    'sand_fill': '#cabd9e',
    'sand_stroke': '#7a716b',
    'sand_tint': '#deddc0',
    'sand_light': '#fcf8ed',
    
    # 6. Highlights, Key-Points, ROI Callout Frames, Overlays
    'gold_fill': '#cea62a',
    'gold_stroke': '#854d0e',
    'gold_tint': '#fef9c3',
    'cyan_box': '#06b6d4',
    'yellow_box': '#eab308',
    'coral_box': '#ef4444',
    'green_box': '#10b981',
    
    # 7. Neutrals
    'canvas_bg': '#ffffff',
    'card_bg': '#f8fafc',
    'border_subtle': '#cbd5e1',
    'text_primary': '#0f172a',
    'text_secondary': '#475569',
    'text_muted': '#64748b',
}

# Standard Matplotlib Configuration Dictionary
IPMI_RC_PARAMS = {
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans', 'Liberation Sans'],
    'font.size': 8.5,
    'axes.labelsize': 8.5,
    'axes.titlesize': 9.0,
    'xtick.labelsize': 7.5,
    'ytick.labelsize': 7.5,
    'legend.fontsize': 7.5,
    'figure.titlesize': 10.0,
    'lines.linewidth': 1.2,
    'lines.markersize': 4.5,
    'figure.dpi': 600,
    'savefig.dpi': 600,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.02,
    'axes.edgecolor': '#475569',
    'axes.linewidth': 0.8,
    'axes.facecolor': '#ffffff',
    'figure.facecolor': '#ffffff',
    'grid.color': '#e2e8f0',
    'grid.linewidth': 0.6,
    'grid.alpha': 0.8,
}

@contextmanager
def ipmi_style():
    """Context manager applying canonical IPMI publication rcParams."""
    old_rc = dict(plt.rcParams)
    plt.rcParams.update(IPMI_RC_PARAMS)
    try:
        yield
    finally:
        plt.rcParams.clear()
        plt.rcParams.update(old_rc)

def add_metric_badge(ax, text, loc='lower left', color='#ffffff', bg_color='#0f172a', alpha=0.75):
    """Adds a clinical metric badge in the corner of an image axes."""
    coords = {
        'lower left': (0.04, 0.04, 'left', 'bottom'),
        'lower right': (0.96, 0.04, 'right', 'bottom'),
        'upper left': (0.04, 0.96, 'left', 'top'),
        'upper right': (0.96, 0.96, 'right', 'top')
    }
    x, y, ha, va = coords.get(loc, coords['lower left'])
    ax.text(x, y, text, transform=ax.transAxes, fontsize=7.5, fontweight='bold',
            color=color, ha=ha, va=va,
            bbox=dict(boxstyle='round,pad=0.25', facecolor=bg_color, edgecolor='none', alpha=alpha))

def draw_roi_box(ax, xy, width, height, color=IPMI_COLORS['yellow_box'], linewidth=1.5, linestyle='-'):
    """Draws a highlighted ROI callout box on an image."""
    from matplotlib.patches import Rectangle
    rect = Rectangle(xy, width, height, fill=False, edgecolor=color,
                     linewidth=linewidth, linestyle=linestyle)
    ax.add_patch(rect)
    return rect
