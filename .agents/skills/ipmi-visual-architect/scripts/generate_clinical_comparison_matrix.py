#!/usr/bin/env python3
"""
Generate Publication-Grade IPMI Clinical Comparison Matrix
Demonstrates:
  1. Columnar Benchmark: [Input Scan] -> [Baseline 1] -> [Baseline 2] -> [Ours] -> [Ground Truth]
  2. Dual-Pane Insets: Full B-Scan with ROI bounding box + Magnified Callout Panel below
  3. Residual Error Heatmaps: Absolute difference in 'inferno' with physical scale
  4. In-Situ Metric Badges: Local MABE and Dice in corner badges
  5. Exact Springer LNCS Text Width: 122 mm (348.4 pt) at 600 DPI
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# Add parent directory for ipmi_palette import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ipmi_palette import (
    ipmi_style, IPMI_COLORS, LNCS_TEXTWIDTH_IN,
    add_metric_badge, draw_roi_box
)

def synthesize_mock_oct_bscan(seed=42):
    """Synthesize realistic mock OCT retinal B-scan with laminar layers."""
    np.random.seed(seed)
    H, W = 250, 400
    x = np.linspace(0, 4 * np.pi, W)
    
    # Base retinal curves (ILM and RNFL posterior boundary)
    ilm = 70 + 15 * np.sin(x * 0.5) + 5 * np.cos(x * 1.5)
    rnfl_thick = 25 + 12 * np.exp(-((np.arange(W) - 150) / 45)**2) + 8 * np.sin(x * 0.8)
    rnfl_bot = ilm + rnfl_thick
    rpe = rnfl_bot + 65 + 8 * np.sin(x * 0.4)
    
    img = np.random.normal(25, 8, (H, W)) # Background speckle
    
    # Render hyperreflective retinal nerve fiber layer (RNFL)
    for col in range(W):
        y_ilm = int(ilm[col])
        y_rnfl = int(rnfl_bot[col])
        y_rpe = int(rpe[col])
        if 0 <= y_ilm < H and 0 <= y_rnfl < H:
            img[y_ilm:y_rnfl, col] += np.random.normal(140, 15, y_rnfl - y_ilm)
        if 0 <= y_rpe < H:
            img[y_rpe:min(H, y_rpe + 12), col] += np.random.normal(160, 20, min(H, y_rpe + 12) - y_rpe)
            
    img = np.clip(img, 0, 255).astype(np.uint8)
    return img, ilm, rnfl_bot

def create_clinical_matrix(output_path="ipmi_clinical_comparison.pdf"):
    """Creates the 5-column, 3-row IPMI comparison matrix."""
    with ipmi_style():
        # Setup Figure sized to exact LNCS textwidth
        # 4.838 in width, aspect ratio ~1.3 -> 3.75 in height
        fig = plt.figure(figsize=(LNCS_TEXTWIDTH_IN, 3.65), dpi=600)
        
        # 3 Rows x 5 Columns
        # Row 0: Full B-Scans with ROI Box
        # Row 1: Zoomed ROI Inset
        # Row 2: Error Residuals (|Pred - GT|)
        gs = fig.add_gridspec(3, 5, height_ratios=[1.0, 0.85, 0.85],
                               left=0.01, right=0.91, top=0.93, bottom=0.03,
                               wspace=0.06, hspace=0.12)
        
        img, ilm_gt, rnfl_gt = synthesize_mock_oct_bscan()
        
        # Define simulation models
        models = [
            ("Raw Input", None, None),
            ("Standard 2D U-Net", 6.8, 0.892),
            ("TransUNet 20M", 5.4, 0.925),
            ("Bi-Planar (Ours)", 2.4, 0.968),
            ("Ground Truth", 0.0, 1.000)
        ]
        
        # ROI Callout Coordinates (around challenging RNFL bundle)
        roi_x, roi_y, roi_w, roi_h = 115, 65, 80, 50
        box_color = IPMI_COLORS['yellow_box']
        
        axes_row0 = [fig.add_subplot(gs[0, c]) for c in range(5)]
        axes_row1 = [fig.add_subplot(gs[1, c]) for c in range(5)]
        axes_row2 = [fig.add_subplot(gs[2, c]) for c in range(5)]
        
        # Perturbation variations for simulated model outputs
        error_offsets = [0, 5.2, 3.8, 1.2, 0]
        
        for col_idx, (name, mabe, dice) in enumerate(models):
            ax0 = axes_row0[col_idx]
            ax1 = axes_row1[col_idx]
            ax2 = axes_row2[col_idx]
            
            # --- ROW 0: FULL B-SCAN ---
            ax0.imshow(img, cmap='gray', aspect='auto', vmin=0, vmax=255)
            ax0.set_title(name, fontsize=8.0, fontweight='bold', pad=3,
                          color=IPMI_COLORS['green_stroke'] if "Ours" in name else IPMI_COLORS['text_primary'])
            draw_roi_box(ax0, (roi_x, roi_y), roi_w, roi_h, color=box_color, linewidth=1.2)
            ax0.axis('off')
            
            # Draw boundary overlays on row 0
            x_pts = np.arange(img.shape[1])
            y_pred = rnfl_gt + error_offsets[col_idx] * np.sin(x_pts * 0.1)
            if col_idx > 0 and col_idx < 4:
                ax0.plot(x_pts, y_pred, color=IPMI_COLORS['blue_fill'], linewidth=0.9, linestyle='--')
            if col_idx == 4:
                ax0.plot(x_pts, rnfl_gt, color=IPMI_COLORS['terracotta_fill'], linewidth=1.0)
                
            # --- ROW 1: MAGNIFIED ROI CALLOUT ---
            roi_crop = img[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
            ax1.imshow(roi_crop, cmap='gray', aspect='auto', vmin=0, vmax=255)
            # Matching border around zoom box
            for spine in ax1.spines.values():
                spine.set_edgecolor(box_color)
                spine.set_linewidth(1.2)
                spine.set_visible(True)
            ax1.set_xticks([])
            ax1.set_yticks([])
            
            # Plot magnified boundary insets
            x_roi = np.arange(roi_w)
            y_roi_gt = rnfl_gt[roi_x:roi_x+roi_w] - roi_y
            y_roi_pred = y_pred[roi_x:roi_x+roi_w] - roi_y
            
            if col_idx == 0:
                ax1.text(0.5, 0.08, "ROI Zoom", transform=ax1.transAxes,
                         fontsize=7.0, color='#fef08a', ha='center', fontweight='bold')
            elif col_idx < 4:
                ax1.plot(x_roi, y_roi_pred, color=IPMI_COLORS['blue_fill'], linewidth=1.2, label='Pred')
                ax1.plot(x_roi, y_roi_gt, color=IPMI_COLORS['terracotta_fill'], linewidth=1.0, linestyle=':', label='GT')
                add_metric_badge(ax1, f"{mabe:.1f}µm", loc='lower right', alpha=0.8)
            else:
                ax1.plot(x_roi, y_roi_gt, color=IPMI_COLORS['terracotta_fill'], linewidth=1.2)
                add_metric_badge(ax1, "Target", loc='lower right', alpha=0.8)
                
            # --- ROW 2: RESIDUAL ERROR MAPS ---
            if col_idx == 0:
                # Raw input difference is not applicable
                ax2.imshow(np.zeros_like(roi_crop), cmap='inferno', vmin=0, vmax=35)
                ax2.text(0.5, 0.5, "N/A\n(Input)", transform=ax2.transAxes,
                         fontsize=7.5, color='#94a3b8', ha='center', va='center')
                ax2.axis('off')
            elif col_idx < 4:
                # Synthesize realistic error residual
                err_map = np.abs(error_offsets[col_idx] * 4.2 * np.random.exponential(1.0, roi_crop.shape))
                im_err = ax2.imshow(err_map, cmap='inferno', aspect='auto', vmin=0, vmax=35)
                add_metric_badge(ax2, f"Dice {dice:.3f}", loc='lower right', alpha=0.8)
                ax2.axis('off')
            else:
                # Ground Truth zero error
                im_err = ax2.imshow(np.zeros_like(roi_crop), cmap='inferno', aspect='auto', vmin=0, vmax=35)
                add_metric_badge(ax2, "0.0 µm", loc='lower right', alpha=0.8)
                ax2.axis('off')
                
        # Vertical Sub-panel Row Labels on Left
        fig.text(0.005, 0.78, "Full Slice", fontsize=7.5, fontweight='bold', rotation='vertical', va='center')
        fig.text(0.005, 0.46, "ROI Zoom", fontsize=7.5, fontweight='bold', rotation='vertical', va='center')
        fig.text(0.005, 0.16, "Error Map", fontsize=7.5, fontweight='bold', rotation='vertical', va='center')
        
        # Dedicated Calibrated Colorbar on Far Right
        cbar_ax = fig.add_axes([0.925, 0.05, 0.018, 0.22])
        cbar = fig.colorbar(im_err, cax=cbar_ax)
        cbar.set_label("Residual (µm)", fontsize=7.0, labelpad=2)
        cbar.ax.tick_params(labelsize=6.5)
        
        # Save output in vector PDF and companion PNG
        fig.savefig(output_path, dpi=600)
        png_path = os.path.splitext(output_path)[0] + ".png"
        fig.savefig(png_path, dpi=600)
        plt.close(fig)
        print(f"Generated IPMI clinical comparison matrix: {output_path} & {png_path}")

if __name__ == '__main__':
    out = "ipmi_clinical_comparison_sample.pdf"
    create_clinical_matrix(out)
