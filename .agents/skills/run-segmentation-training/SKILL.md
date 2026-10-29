---
name: run-segmentation-training
description: Executes the advanced fine-tuning training loop for the Hierarchical U-Net segmentation model on the OCT5K and Base datasets. Trigger this when asked to start or run the segmentation model training.
---

# Run Segmentation Model Training

This skill provides instructions for executing the advanced fine-tuning training loop for the OCT image segmentation model. 

The segmentation training pipeline is located in the `image-segmentation-model-training` directory and relies on a sophisticated mix of Focal Loss, Asymmetric Freezing, and stratified Virtual Epoch sampling between a massive Base dataset and a smaller OCT5K fine-tuning dataset.

## Execution Steps

### 1. Prerequisites
Ensure you have the paths to the dataset directories available. You must provide two paths:
- **Base Dataset**: The large proprietary dataset (e.g., 90k images).
- **OCT5K Dataset**: The specialized dataset containing precise Drusen boundaries.

If the user has not provided these paths, ask them to clarify where the datasets are located.

### 2. Prepare the Environment
Ensure the terminal is properly configured to run PyTorch and the training scripts.
```bash
cd image-segmentation-model-training
```

### 3. Run the Training Command
Use the `run_command` tool to execute the `train.py` script. The script requires the datasets to be passed explicitly. 

If the user wants to resume from a previous checkpoint (e.g., the pre-trained base model weights), include the `--resume` flag. Note: It is highly recommended to start the fine-tuning phase by resuming ONLY from the base pre-trained weights (before OCT5K was ever introduced) to avoid gradient shock.

```bash
python training/train.py \
  --base-data "/path/to/base_dataset" \
  --oct5k-data "/path/to/oct5k_dataset" \
  --resume "checkpoints/unet_hierarchical_best_base.pth" \
  --epochs 100 \
  --batch-size 16 \
  --lr 1e-4 \
  --amp 
```

**Key Arguments:**
- `--base-data`: Path to the Base dataset directory.
- `--oct5k-data`: Path to the OCT5K dataset directory.
- `--resume`: Path to a `.pth` checkpoint to load weights from.
- `--amp`: Enables Automatic Mixed Precision for faster, lower-VRAM training.
- `--batch-size`: Modify this based on the available GPU VRAM (16 is a good starting point).

### 4. Monitoring
After launching the script, advise the user that they can monitor the independent validation metrics (Base vs OCT5K Granular Dice) by opening a separate terminal, navigating to `image-segmentation-model-training`, and running TensorBoard:
```bash
tensorboard --logdir=logs
```
