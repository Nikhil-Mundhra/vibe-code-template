---
name: cnn-unet-architect
description: Architectural specifications, tensor dimension contracts, mathematical loss formulations, and design rules for building medical CNN and U-Net models for ophthalmic OCT layer segmentation.
---

# CNN / U-Net Architect Skill for Ophthalmic OCT

This skill provides design patterns, physical coordinate contracts, tensor shape conventions, and loss formulation standards for building and iterating on deep neural network architectures (2D, 2.5D, and 3D U-Nets / CNNs) specifically tailored for retinal and optic nerve head (ONH) Optical Coherence Tomography (OCT).

---

## 1. Physical Grid & Coordinate Mapping Contracts

Retinal OCT volumes possess extreme physical anisotropy between the axial (depth) axis and transverse lateral axes:

| Axis | Physiological Direction | Typical Solix Physical Dimension | Voxel Count ($N$) | Physical Spacing ($\Delta$) | Sampling Nature |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$X$ (Fast)** | Temporal $\longleftrightarrow$ Nasal | $6.00\,\text{mm}$ | $320$ pixels | $\Delta x = 18.750\,\mu\text{m}$ | Transverse lateral |
| **$Y$ (Slow)** | Superior $\longleftrightarrow$ Inferior | $6.02\,\text{mm}$ | $320$ B-scans | $\Delta y = 18.809\,\mu\text{m}$ | Inter-B-scan lateral |
| **$Z$ (Axial)** | Anterior $\longleftrightarrow$ Posterior | $2.40\,\text{mm}$ | $768$ rows | $\Delta z = 3.124\,\mu\text{m}$ | Optical depth |

### Core Architectural Implications
1. **Aspect Ratio Anisotropy**: The axial resolution ($Z=768$) is $\sim 6\times$ higher than the lateral resolution ($X=320$). Never apply aggressive downsampling (e.g. pooling factors $> 16\times$) along $X$ without preserving vertical localization, otherwise fine layer boundaries like the Inner Limiting Membrane (ILM) and Nerve Fiber Layer (NFL) will blur.
2. **Lossless Transpose for Bi-Planar Fusion**: Because $\Delta x \approx \Delta y \approx 18.8\,\mu\text{m}$, transverse orthogonal volumes are mutually interchangeable via:
   $$\mathbf{V}_{\text{vert}} = \text{transpose}(\mathbf{V}_{\text{horiz}}, (2, 1, 0))$$
   This enables 2.5D models to process orthogonal planes with identical spatial kernels.

---

## 2. Supported Architecture Paradigms

### Paradigm A: 2.5D Multi-Slice Residual U-Net (Recommended Default)
- **Input Shape**: $(B, 2K+1, 768, 320)$ where $K=2$ gives a 5-slice adjacent sliding context window.
- **Why**: Captures inter-slice continuity across the slow axis without the heavy computational and memory burden of full 3D convolutions.
- **Encoder**: 4–5 stages of Residual Units (`ResidualBlock(C_in, C_out, stride)`), doubling channels ($16 \to 32 \to 64 \to 128 \to 256$).
- **Bottleneck**: Feature map size $(B, 256, 48, 20)$.
- **Decoder**: Transposed convolutions or bilinear upsampling with concatenated residual skip connections.

### Paradigm B: Canonicalizer-Equipped U-Net (STN-UNet)
- **Why**: Clinical OCT scans exhibit variable head tilt ($\pm 12^\circ$) and vertical eye positioning.
- **Component**: `ConstrainedSpatialTransformer` inserted before the encoder.
- **Constraint**: Rigid transformation only (2 degrees of freedom: in-plane rotation $\theta$ and vertical shift $t_y$).
- **Initialization**: Identity matrix ($W_{\text{last}} = 0$, $b_{\text{last}} = 0$) so training begins as a standard U-Net.
- **Coordinate Inverse**: Must provide `invert_coordinates(y_canon, theta, t_y)` to project predicted boundaries back into native unaligned coordinates.

### Paradigm C: Multi-Task Voxel + Boundary Regression Heads
Pure voxel mask classification produces noisy boundaries and isolated voxel islands. Always equip the U-Net with coupled heads:
1. **Dense Voxel Head**: `Conv2d(C_dec, 1, 1x1)` $\to (B, 1, 768, 320)$ followed by Sigmoid.
2. **Continuous 1D Boundary Regression Head**:
   - Apply `AdaptiveAvgPool2d((1, 320))` across feature height to collapse depth into lateral columns $(B, C, 320)$.
   - Pass through 1D residual convs to predict:
     - $\hat{y}_{\text{ILM}} \in [0, 768]$ (anterior boundary depth in pixels)
     - $\hat{y}_{\text{NFL}} \in [0, 768]$ (posterior boundary depth in pixels)
     - $\hat{y}_{\text{cup}} \in \mathbb{R}^{320}$ (optic cup absence/presence logits)

### Paradigm D: Attention-Gated U-Net (AG-UNet)
For thin membranes or pathology localization, place an **Attention Gate** on every skip connection:
$$\alpha = \sigma\left(\text{BN}\left(W_\psi \cdot \text{ReLU}(\text{BN}(W_g \cdot \mathbf{g}) + \text{BN}(W_x \cdot \mathbf{x}))\right)\right)$$
$$\mathbf{x}_{\text{attributed}} = \mathbf{x} \odot \alpha$$
where $\mathbf{g}$ is the gating signal from the coarser decoder level, and $\mathbf{x}$ is the skip feature from the encoder.

---

## 3. Loss Formulations & Multi-Objective Balancing

Medical OCT layer segmentation must not rely on single cross-entropy. Use the composite clinical loss:

$$\mathcal{L}_{\text{total}} = w_{\text{dice}} \mathcal{L}_{\text{Dice}} + w_{\text{bce}} \mathcal{L}_{\text{BCE}} + w_{\text{surf}} \mathcal{L}_{\text{surface}} + w_{\text{edge}} \mathcal{L}_{\text{edge}} + w_{\text{cup}} \mathcal{L}_{\text{cup}}$$

### 1. Soft Dice + Binary Cross-Entropy
$$\mathcal{L}_{\text{Dice}} = 1 - \frac{2 \sum p_i g_i + \epsilon}{\sum p_i^2 + \sum g_i^2 + \epsilon}$$

### 2. Smooth L1 Surface Huber Loss
$$\mathcal{L}_{\text{surface}} = \text{SmoothL1}(\hat{y}_{\text{ILM}}, y_{\text{ILM}}) + \text{SmoothL1}(\hat{y}_{\text{NFL}}, y_{\text{NFL}})$$
- Masks out Optic Cup regions where the RNFL converges to zero thickness.

### 3. Optical Gradient Alignment Loss ($\mathcal{L}_{\text{edge}}$)
Encourages predicted boundary depth to snap onto physical high-contrast tissue interfaces (Sobel axial gradient $|G_z|$ of the raw OCT scan):
$$\mathcal{L}_{\text{edge}} = -\frac{1}{W} \sum_{x=1}^{W} |G_z(\hat{y}_{\text{boundary}}(x), x)|$$

### 4. Surface Order Violation Penalty
Retinal layers are anatomically strictly ordered. Penalize cases where posterior layers cross anterior layers:
$$\mathcal{L}_{\text{order}} = \text{ReLU}(\hat{y}_{\text{ILM}} - \hat{y}_{\text{NFL}})$$

---

## 4. Eye Laterality Standardization (OD vs. OS)

To avoid forcing networks to learn symmetric representations for left and right eyes:
- **Left Eyes (OS)**:
  - Horizontal B-scans: Horizontally flipped (`torch.flip(x, dims=[-1])`) so the Nasal quadrant is always oriented on the same side as Right Eyes (OD).
  - Vertical B-scans: Slice order is reversed ($a \to N_{\text{slices}} - 1 - a$).
- **Inference Inversion**: Restore predictions back into native coordinate space before computing clinical metrics or rendering.

---

## 5. Pre-Submission Architecture Checklist for Agents

Before submitting training jobs to Jubail HPC or launching experiments, verify:

1. **Tensor Shape Verification**:
   - Run a 1-batch dummy forward pass:
     ```python
     x = torch.randn(2, in_channels, 768, 320)
     out = model(x)
     assert out["mask"].shape == (2, 1, 768, 320)
     assert out["ilm_curve"].shape == (2, 320)
     ```
2. **GPU Memory Footprint**:
   - 2.5D models with batch size 16 require $\sim 14\,\text{GB}$ VRAM.
   - For A100 (40GB/80GB) or H200 (141GB), batch size 32 or 64 is optimal with gradient accumulation.
3. **Identity Initialization**:
   - If using STN or attention modules, assert that outputs at initialization equal unmodified base features ($\theta \approx 0, t_y \approx 0, \alpha \approx 1$).
4. **Zero-Leakage Compliance**:
   - Ensure subject IDs in validation sets are strictly isolated from training sets.
