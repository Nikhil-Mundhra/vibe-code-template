---
name: cohort-dataset-splitting
description: Clinical ophthalmic OCT dataset auditing, QC outlier filtering, and zero-leakage stratified train/validation cohort splitting.
---

# Cohort Dataset Splitting Skill

This skill provides an automated, clinically grounded toolchain for auditing OCT DICOM volumes and curve XML segmentations, applying Quality Control (QC) outlier rules, and generating frozen, zero-leakage stratified train/validation/test manifests.

## Clinical QC Rules & Ground Truth Tiers

When partitioning Optovue Solix cohorts (e.g. from `Solix_Outliers.xlsx` and `deidentified-new`):

1. **`Verified` (`Result == Good`)**: Machine segmentation algorithm accepted without manual edits. High quality; suitable for both Phase 1 broad pre-training and validation.
2. **`Corrected` (`Result == Good`)**: Scans where expert human boundary corrections took place at the peripapillary optic disc margin (`tsv/bad` paired with `tsv/good`). Essential for Phase 2 audited fine-tuning and gold-standard clinical validation.
3. **`Pending`**: Scans with macula-specific issues. Can only be used for post-validation over non-optic-disc regions; excluded from optic disc training.
4. **`Excluded` or `Result == Bad`**: Poor contrast, severe motion artifacts, or failed acquisitions. Automatically excluded from training and validation.

## Strict Zero-Leakage Policy

- **Subject-Level Isolation**: All scans of a subject (OD, OS, repeat acquisitions) must reside exclusively in ONE split.
- **Audited Subject Partitioning**: Any human-audited subjects allocated to the validation split must **never** be used for fine-tuning or training.
- **Fair Benchmark Evaluation**: Candidate architectures (e.g. BiPlanar vs. 3D U-Net) must be benchmarked on identical, mutually held-out validation sets.

---

## Available Script

### `scripts/split_cohort.py`

Performs end-to-end dataset discovery, resolves duplicate acquisitions, cross-references QC records, stratifies by clinical tier and thickness extremes, and generates frozen JSON manifests.

#### Usage

```bash
python .agents/skills/cohort-dataset-splitting/scripts/split_cohort.py \
    --dataset_root "/Users/nikhilmundhra/Library/CloudStorage/Box-Box/OCT_Segmentations_Solix/deidentified-new" \
    --qc_excel "Solix_Outliers.xlsx" \
    --protocol "Disc Cube" \
    --val_count 20 \
    --test_count 20 \
    --must_include_val "BEH0174,BEH0310,BEH0314,BEH0335,BEH0352,BEH0354,BEH0090,BEH0284,BEH0259,BEH0084,BEH0264,BEH0343,BEH0303" \
    --output_dir "model_training/train_rnfl_3d/manifests_3way" \
    --seed 42
```

#### On NYUAD Jubail HPC

```bash
/scratch/nm4358/envs/oct-env/bin/python .agents/skills/cohort-dataset-splitting/scripts/split_cohort.py \
    --dataset_root "/scratch/nm4358/deidentified-new" \
    --val_count 20 \
    --test_count 20 \
    --output_dir "manifests_3way"
```

#### Generated Manifests

1. **`validation_manifest.json`**: Stratified held-out validation subjects for checkpoint and hyperparameter selection.
2. **`test_manifest.json`**: Stratified, completely untouched test cohort reserved for final unbiased benchmark comparison.
3. **`phase1_train_manifest.json`**: Broad pre-training cohort ($N_{\text{matched}} - N_{\text{val}} - N_{\text{test}}$).
4. **`phase2_audited_train_manifest.json`**: Targeted human-audited training subjects ($N_{\text{audited}} - N_{\text{val\_audited}} - N_{\text{test\_audited}}$).
5. **`cohort_orphans.json`**: Discrepancies, missing pairs, and QC-excluded subjects with reasons.
6. **`cohort_split_summary.json`**: Complete machine-readable audit report.
