#!/usr/bin/env python3
"""
Generate Publication-Grade IPMI Multi-Structure Anatomical Boxplots
Demonstrates:
  1. Multi-Region Stratification (e.g., TSNT Quadrants / Anatomical Regions)
  2. Jittered Scatter Outliers overlaid on IQR boxes (translucent data density)
  3. Canonical IPMI Palette: Steel Blue (Baseline), Mauve (ViT), Sage Green (Ours)
  4. Statistical Significance Brackets (p-values / asterisks)
  5. Exact Springer LNCS Text Width: 122 mm (348.4 pt)
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Add parent directory for ipmi_palette import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ipmi_palette import ipmi_style, IPMI_COLORS, LNCS_TEXTWIDTH_IN

def generate_boxplots(output_path="ipmi_anatomical_boxplots.pdf"):
    """Generates the multi-region anatomical boxplot chart."""
    with ipmi_style():
        # Setup Figure sized to exact LNCS textwidth
        # 4.838 in width, height ~2.4 in (Aspect ratio ~2.0)
        fig, ax = plt.subplots(figsize=(LNCS_TEXTWIDTH_IN, 2.35), dpi=600)
        
        np.random.seed(101)
        regions = ['Temporal', 'Superior', 'Nasal', 'Inferior']
        methods = [
            ('Standard 2D U-Net', IPMI_COLORS['blue_fill'], IPMI_COLORS['blue_stroke']),
            ('TransUNet 20M', IPMI_COLORS['mauve_fill'], IPMI_COLORS['mauve_stroke']),
            ('Bi-Planar 2.5D (Ours)', IPMI_COLORS['green_fill'], IPMI_COLORS['green_stroke'])
        ]
        
        n_regions = len(regions)
        n_methods = len(methods)
        bar_width = 0.22
        group_gap = 0.85
        
        # Base error distributions per quadrant (MABE in um)
        base_means = {
            'Temporal': [6.2, 5.1, 3.2],
            'Superior': [5.8, 4.9, 2.8],
            'Nasal':    [7.4, 6.2, 3.6],
            'Inferior': [5.5, 4.8, 2.7]
        }
        
        legend_handles = []
        
        for m_idx, (m_name, fill_color, stroke_color) in enumerate(methods):
            all_positions = []
            all_data = []
            
            for r_idx, r_name in enumerate(regions):
                pos = r_idx * group_gap + (m_idx - 1) * bar_width
                all_positions.append(pos)
                
                mean_val = base_means[r_name][m_idx]
                # Log-normal distribution to simulate real medical boundary errors
                data = np.random.lognormal(mean=np.log(mean_val), sigma=0.28, size=35)
                all_data.append(data)
                
                # Overlay Jittered Scatter Points (raw clinical subject values)
                jitter = np.random.normal(0, 0.035, size=len(data))
                ax.scatter(pos + jitter, data, color=stroke_color, alpha=0.35,
                           s=6, zorder=3, edgecolors='none')
                
            # Draw Boxplots
            bp = ax.boxplot(all_data, positions=all_positions, widths=bar_width * 0.82,
                            patch_artist=True, showfliers=False, zorder=4,
                            medianprops=dict(color='#ffffff', linewidth=1.2),
                            whiskerprops=dict(color=stroke_color, linewidth=0.9),
                            capprops=dict(color=stroke_color, linewidth=0.9),
                            boxprops=dict(facecolor=fill_color, edgecolor=stroke_color,
                                          linewidth=1.0, alpha=0.88))
            
            legend_handles.append(bp['boxes'][0])
            
        # Statistical Significance Annotation (Superior Quadrant: Ours vs Baselines)
        x_base = 1 * group_gap - bar_width
        x_ours = 1 * group_gap + bar_width
        y_bar = 9.8
        ax.plot([x_base, x_base, x_ours, x_ours], [y_bar - 0.3, y_bar, y_bar, y_bar - 0.3],
                color='#1e293b', linewidth=0.8)
        ax.text((x_base + x_ours) / 2, y_bar + 0.1, r"$p = 3.6 \times 10^{-11}$",
                ha='center', va='bottom', fontsize=6.8, fontweight='bold', color='#1e293b')
        
        # Formatting X and Y axes
        group_centers = [r_idx * group_gap for r_idx in range(n_regions)]
        ax.set_xticks(group_centers)
        ax.set_xticklabels(regions, fontsize=8.0, fontweight='bold')
        ax.set_ylabel(r"Laminar MABE ($\mu$m)", fontsize=8.0, fontweight='bold')
        ax.set_ylim(0, 12.0)
        
        # Gridlines (Subtle horizontal reference lines)
        ax.yaxis.grid(True, linestyle='--', alpha=0.6, color='#cbd5e1')
        ax.xaxis.grid(False)
        ax.set_axisbelow(True)
        
        # Clean Spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#475569')
        ax.spines['bottom'].set_color('#475569')
        
        # Legend placed above top or inside
        ax.legend(legend_handles, [m[0] for m in methods], loc='upper right',
                  frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1',
                  framealpha=0.95, fontsize=7.0, ncol=1)
        
        # Save output in vector PDF and companion PNG
        fig.tight_layout()
        fig.savefig(output_path, dpi=600)
        png_path = os.path.splitext(output_path)[0] + ".png"
        fig.savefig(png_path, dpi=600)
        plt.close(fig)
        print(f"Generated IPMI anatomical boxplots: {output_path} & {png_path}")

if __name__ == '__main__':
    out = "ipmi_anatomical_boxplots_sample.pdf"
    generate_boxplots(out)
