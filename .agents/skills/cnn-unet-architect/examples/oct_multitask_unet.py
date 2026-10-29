"""Reference modular implementation for CNN/U-Net architectures tailored to ophthalmic OCT.

Demonstrates:
1. Aspect-ratio-aware anisotropic 2.5D Residual U-Net backbone
2. Attention Gate (AG) skip connections
3. Multi-task heads (Dense 2D voxel mask + Continuous 1D ILM/NFL boundary regression)
4. Anatomical surface order constraint assertion
"""

from typing import Dict, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F


class AttentionGate(nn.Module):
    """Attention Gate for filtering skip-connection features using coarser gating signals."""

    def __init__(self, in_channels_x: int, in_channels_g: int, inter_channels: int):
        super().__init__()
        self.wx = nn.Sequential(
            nn.Conv2d(in_channels_x, inter_channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(inter_channels),
        )
        self.wg = nn.Sequential(
            nn.Conv2d(in_channels_g, inter_channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(inter_channels),
        )
        self.psi = nn.Sequential(
            nn.Conv2d(inter_channels, 1, kernel_size=1, bias=True),
            nn.BatchNorm2d(1),
            nn.Sigmoid(),
        )
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x: torch.Tensor, g: torch.Tensor) -> torch.Tensor:
        # Match spatial resolution of gating signal to x
        if g.shape[2:] != x.shape[2:]:
            g = F.interpolate(g, size=x.shape[2:], mode="bilinear", align_corners=False)
        theta = self.wx(x)
        phi = self.wg(g)
        f = self.relu(theta + phi)
        alpha = self.psi(f)
        return x * alpha


class ResBlock(nn.Module):
    """Residual unit with 2 convolution layers."""

    def __init__(self, in_ch: int, out_ch: int):
        super().__init__()
        self.conv1 = nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_ch)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_ch)

        self.shortcut = nn.Sequential()
        if in_ch != out_ch:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_ch, out_ch, kernel_size=1, bias=False),
                nn.BatchNorm2d(out_ch),
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        res = self.shortcut(x)
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        return self.relu(out + res)


class OCTMultiTaskUNet(nn.Module):
    """Multi-task Attention U-Net designed for 768 x 320 OCT B-scans."""

    def __init__(self, in_channels: int = 5, base_channels: int = 16):
        super().__init__()
        c = base_channels

        # Encoder Stages
        self.enc1 = ResBlock(in_channels, c)
        self.pool1 = nn.MaxPool2d(2)  # 384 x 160

        self.enc2 = ResBlock(c, c * 2)
        self.pool2 = nn.MaxPool2d(2)  # 192 x 80

        self.enc3 = ResBlock(c * 2, c * 4)
        self.pool3 = nn.MaxPool2d(2)  # 96 x 40

        self.enc4 = ResBlock(c * 4, c * 8)
        self.pool4 = nn.MaxPool2d(2)  # 48 x 20

        # Bottleneck
        self.bottleneck = ResBlock(c * 8, c * 16)  # 48 x 20

        # Decoders + Attention Gates
        self.up4 = nn.ConvTranspose2d(c * 16, c * 8, kernel_size=2, stride=2)
        self.ag4 = AttentionGate(in_channels_x=c * 8, in_channels_g=c * 16, inter_channels=c * 4)
        self.dec4 = ResBlock(c * 16, c * 8)

        self.up3 = nn.ConvTranspose2d(c * 8, c * 4, kernel_size=2, stride=2)
        self.ag3 = AttentionGate(in_channels_x=c * 4, in_channels_g=c * 8, inter_channels=c * 2)
        self.dec3 = ResBlock(c * 8, c * 4)

        self.up2 = nn.ConvTranspose2d(c * 4, c * 2, kernel_size=2, stride=2)
        self.ag2 = AttentionGate(in_channels_x=c * 2, in_channels_g=c * 4, inter_channels=c)
        self.dec2 = ResBlock(c * 4, c * 2)

        self.up1 = nn.ConvTranspose2d(c * 2, c, kernel_size=2, stride=2)
        self.ag1 = AttentionGate(in_channels_x=c, in_channels_g=c * 2, inter_channels=c // 2)
        self.dec1 = ResBlock(c * 2, c)

        # Head 1: Dense Voxel Mask
        self.mask_head = nn.Conv2d(c, 1, kernel_size=1)

        # Head 2: 1D Boundary Regression (ILM & NFL depth in [0, 768] px + Cup logit)
        self.curve_pool = nn.AdaptiveAvgPool2d((1, 320))
        self.curve_conv = nn.Sequential(
            nn.Conv1d(c, c, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.Conv1d(c, 3, kernel_size=1),  # Channel 0: ILM, 1: NFL, 2: Cup Logit
        )

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        b, _, h, w = x.shape

        # Encoding
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool1(e1))
        e3 = self.enc3(self.pool2(e2))
        e4 = self.enc4(self.pool3(e3))
        btn = self.bottleneck(self.pool4(e4))

        # Decoding with Attention Gating
        d4 = self.dec4(torch.cat([self.up4(btn), self.ag4(e4, btn)], dim=1))
        d3 = self.dec3(torch.cat([self.up3(d4), self.ag3(e3, d4)], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), self.ag2(e2, d3)], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), self.ag1(e1, d2)], dim=1))

        # Head 1: Mask
        mask_logits = self.mask_head(d1)

        # Head 2: 1D Continuous Curve Coordinates
        curve_feat = self.curve_pool(d1).squeeze(2)  # (B, C, 320)
        curve_out = self.curve_conv(curve_feat)  # (B, 3, 320)

        # Normalize depth to [0, H]
        ilm_depth = torch.sigmoid(curve_out[:, 0, :]) * float(h)
        nfl_depth = torch.sigmoid(curve_out[:, 1, :]) * float(h)
        cup_logits = curve_out[:, 2, :]

        return {
            "mask_logits": mask_logits,
            "mask_prob": torch.sigmoid(mask_logits),
            "ilm_depth": ilm_depth,
            "nfl_depth": nfl_depth,
            "cup_logits": cup_logits,
        }


def compute_composite_loss(
    preds: Dict[str, torch.Tensor],
    target_mask: torch.Tensor,
    target_ilm: torch.Tensor,
    target_nfl: torch.Tensor,
    target_cup: torch.Tensor,
    w_dice: float = 1.0,
    w_bce: float = 1.0,
    w_surf: float = 0.5,
    w_cup: float = 0.2,
    w_order: float = 0.1,
) -> Tuple[torch.Tensor, Dict[str, float]]:
    """Computes composite multi-task loss with anatomical ordering constraint."""
    mask_prob = preds["mask_prob"]
    mask_logits = preds["mask_logits"]

    # 1. Soft Dice
    inter = (mask_prob * target_mask).sum(dim=(2, 3))
    union = (mask_prob**2).sum(dim=(2, 3)) + (target_mask**2).sum(dim=(2, 3))
    dice_loss = 1.0 - (2.0 * inter + 1e-6) / (union + 1e-6)
    dice_loss = dice_loss.mean()

    # 2. BCE
    bce_loss = F.binary_cross_entropy_with_logits(mask_logits, target_mask)

    # 3. Continuous Surface Huber
    valid_cup_mask = (target_cup > 0.5).float()  # evaluate where cup is not excavated
    ilm_loss = (F.smooth_l1_loss(preds["ilm_depth"], target_ilm, reduction="none") * valid_cup_mask).sum() / (
        valid_cup_mask.sum() + 1e-6
    )
    nfl_loss = (F.smooth_l1_loss(preds["nfl_depth"], target_nfl, reduction="none") * valid_cup_mask).sum() / (
        valid_cup_mask.sum() + 1e-6
    )
    surf_loss = (ilm_loss + nfl_loss) * 0.5

    # 4. Cup Logits BCE
    cup_loss = F.binary_cross_entropy_with_logits(preds["cup_logits"], target_cup)

    # 5. Anatomical ordering constraint (ILM must be anterior to NFL: ilm_depth <= nfl_depth)
    order_violation = F.relu(preds["ilm_depth"] - preds["nfl_depth"]).mean()

    total_loss = (
        w_dice * dice_loss
        + w_bce * bce_loss
        + w_surf * surf_loss
        + w_cup * cup_loss
        + w_order * order_violation
    )

    losses = {
        "total": float(total_loss.item()),
        "dice": float(dice_loss.item()),
        "bce": float(bce_loss.item()),
        "surface": float(surf_loss.item()),
        "cup": float(cup_loss.item()),
        "order_violation": float(order_violation.item()),
    }
    return total_loss, losses


if __name__ == "__main__":
    model = OCTMultiTaskUNet(in_channels=5, base_channels=16)
    dummy_input = torch.randn(2, 5, 768, 320)
    preds = model(dummy_input)

    assert preds["mask_logits"].shape == (2, 1, 768, 320)
    assert preds["ilm_depth"].shape == (2, 320)
    assert preds["nfl_depth"].shape == (2, 320)
    assert preds["cup_logits"].shape == (2, 320)
    print("Contract verification passed successfully! All tensor shapes conform to specification.")
