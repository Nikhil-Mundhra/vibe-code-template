#!/usr/bin/env python3
"""Autonomous clinical dataset auditor and stratified cohort splitter for OCT RNFL volumes.

Audits DICOM and curve XML pairings, integrates QC outlier annotations, enforces
strict zero-leakage rules, and outputs deterministic training, validation, and
fine-tuning manifests.
"""

import argparse
import glob
import json
import os
import random
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple


def extract_acquisition_time(filename: str) -> str:
    m = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})-(\d{2})", filename)
    if m:
        return f"{m.group(1)} {m.group(2)}:{m.group(3)}:{m.group(4)}"
    return ""


def find_matching_curve_xml(
    tsv_dir: str, subj: str, eye: str, dcm_fname: str, protocol: str = "Disc Cube"
) -> Optional[str]:
    subj_tsv = os.path.join(tsv_dir, subj)
    if not os.path.exists(subj_tsv):
        return None
    xmls = glob.glob(os.path.join(subj_tsv, "curve", f"*{eye}*{protocol}*.xml"))
    if not xmls:
        xmls = glob.glob(os.path.join(subj_tsv, "curve", f"*{protocol}*{eye}*.xml"))
    if len(xmls) == 1:
        return xmls[0]
    xmls = sorted(xmls)
    return xmls[0] if xmls else None


@dataclass
class ScanRecord:
    subject: str
    eye: str
    dcm_path: str
    dcm_filename: str
    good_xml_path: Optional[str] = None
    bad_xml_path: Optional[str] = None
    is_opt: bool = False
    acquisition_time: str = ""
    is_duplicate_acquisition: bool = False
    selection_reason: str = ""


@dataclass
class SubjectAudit:
    subject: str
    in_dicom_dir: bool = False
    in_good_dir: bool = False
    in_bad_dir: bool = False
    qc_seg_status: Optional[str] = None
    qc_result: Optional[str] = None
    qc_comments: Optional[str] = None
    scans: List[ScanRecord] = field(default_factory=list)
    has_matched_od: bool = False
    has_matched_os: bool = False
    matched_scan_count: int = 0
    is_eligible: bool = False
    is_audited: bool = False
    split: str = "unassigned"
    orphan_reason: str = ""


def parse_qc_sheet(qc_excel_path: Optional[Path]) -> Dict[str, dict]:
    if not qc_excel_path or not qc_excel_path.exists():
        return {}
    try:
        import openpyxl
    except ImportError:
        print("[Notice] openpyxl not installed. Skipping Excel QC parsing.")
        return {}

    wb = openpyxl.load_workbook(str(qc_excel_path), data_only=True)
    if "QC" not in wb.sheetnames:
        return {}

    ws = wb["QC"]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return {}

    qc_map = {}
    for r in rows[1:]:
        if not r or len(r) < 8:
            continue
        subj, loc, seg_status, result = r[0], r[3], r[6], r[7]
        if subj and loc == "Disc":
            qc_map[str(subj).strip()] = {
                "seg_status": str(seg_status).strip() if seg_status else None,
                "result": str(result).strip() if result else None,
                "comments": str(r[8]).strip() if len(r) > 8 and r[8] else None,
            }
    return qc_map


def audit_cohort(
    dataset_root: Path,
    qc_excel_path: Optional[Path] = None,
    protocol: str = "Disc Cube",
) -> Dict[str, SubjectAudit]:
    qc_map = parse_qc_sheet(qc_excel_path)
    dicom_dir = dataset_root / "dicom"
    good_dir = dataset_root / "tsv" / "good"
    bad_dir = dataset_root / "tsv" / "bad"

    dicom_subjs = {d.name for d in dicom_dir.iterdir() if d.is_dir() and not d.name.startswith(".")} if dicom_dir.exists() else set()
    good_subjs = {d.name for d in good_dir.iterdir() if d.is_dir() and not d.name.startswith(".")} if good_dir.exists() else set()
    bad_subjs = {d.name for d in bad_dir.iterdir() if d.is_dir() and not d.name.startswith(".")} if bad_dir.exists() else set()

    all_subjects = sorted(dicom_subjs | good_subjs | bad_subjs)
    audits: Dict[str, SubjectAudit] = {}

    for subj in all_subjects:
        in_dicom = subj in dicom_subjs
        in_good = subj in good_subjs
        in_bad = subj in bad_subjs

        qc_info = qc_map.get(subj, {})
        audit = SubjectAudit(
            subject=subj,
            in_dicom_dir=in_dicom,
            in_good_dir=in_good,
            in_bad_dir=in_bad,
            qc_seg_status=qc_info.get("seg_status"),
            qc_result=qc_info.get("result"),
            qc_comments=qc_info.get("comments"),
        )

        # QC check: Result == 'Bad' or Segmentation_Status == 'Excluded'
        if audit.qc_result == "Bad" or audit.qc_seg_status == "Excluded":
            audit.orphan_reason = f"Excluded by QC sheet ({audit.qc_seg_status}, {audit.qc_result}): {audit.qc_comments}"
            audits[subj] = audit
            continue

        if not in_dicom:
            audit.orphan_reason = "Missing DICOM directory"
            audits[subj] = audit
            continue

        dcm_subj_dir = dicom_dir / subj
        all_dcms = sorted(dcm_subj_dir.glob("*.dcm"))
        disc_dcms = [p for p in all_dcms if protocol.lower() in p.name.lower()]

        if not disc_dcms:
            audit.orphan_reason = f"No {protocol} DICOM acquisitions found (e.g. Retina Cube only)"
            audits[subj] = audit
            continue

        by_eye: Dict[str, List[Path]] = {"OD": [], "OS": []}
        for p in disc_dcms:
            name_upper = p.name.upper()
            if "_OS_" in name_upper or name_upper.endswith("_OS.DCM") or " OS " in name_upper:
                by_eye["OS"].append(p)
            elif "_OD_" in name_upper or name_upper.endswith("_OD.DCM") or " OD " in name_upper:
                by_eye["OD"].append(p)

        for eye in ["OD", "OS"]:
            candidates = by_eye[eye]
            if not candidates:
                continue

            is_dup = len(candidates) > 1
            # Sort: prefer _OPT.dcm, then latest acquisition time
            def sort_key(p: Path):
                is_opt = 1 if "_opt.dcm" in p.name.lower() else 0
                time_str = extract_acquisition_time(p.name)
                return (is_opt, time_str, p.name)

            sorted_candidates = sorted(candidates, key=sort_key, reverse=True)
            canonical_dcm = sorted_candidates[0]

            good_xml = find_matching_curve_xml(str(good_dir), subj, eye, canonical_dcm.name, protocol) if in_good else None
            bad_xml = find_matching_curve_xml(str(bad_dir), subj, eye, canonical_dcm.name, protocol) if in_bad else None

            if not good_xml or not os.path.exists(good_xml):
                continue

            rec = ScanRecord(
                subject=subj,
                eye=eye,
                dcm_path=str(canonical_dcm),
                dcm_filename=canonical_dcm.name,
                good_xml_path=good_xml,
                bad_xml_path=bad_xml,
                is_opt="_opt.dcm" in canonical_dcm.name.lower(),
                acquisition_time=extract_acquisition_time(canonical_dcm.name),
                is_duplicate_acquisition=is_dup,
                selection_reason=f"Selected from {len(candidates)} candidates" if is_dup else "Single acquisition",
            )
            audit.scans.append(rec)
            if eye == "OD":
                audit.has_matched_od = True
            elif eye == "OS":
                audit.has_matched_os = True

        audit.matched_scan_count = len(audit.scans)
        audit.is_eligible = audit.matched_scan_count > 0
        audit.is_audited = any(s.bad_xml_path is not None for s in audit.scans)
        if not audit.is_eligible:
            audit.orphan_reason = f"No matched {protocol} DICOM/XML pairs"

        audits[subj] = audit

    return audits


def split_cohort(
    audits: Dict[str, SubjectAudit],
    val_count: int = 20,
    test_count: int = 0,
    must_include_val: Sequence[str] = (),
    must_include_test: Sequence[str] = (),
    must_include_train: Sequence[str] = (),
    seed: int = 42,
) -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
    """Partitions cohort into Train, Validation, and Test sets with zero-leakage guarantees.

    Returns:
        (val_subjects, test_subjects, train_subjects, phase2_train_audited, orphans)
    """
    random.seed(seed)
    eligible = [s for s, a in audits.items() if a.is_eligible]
    audited = [s for s in eligible if audits[s].is_audited]
    verified = [s for s in eligible if not audits[s].is_audited]

    must_val_set = set(must_include_val)
    must_test_set = set(must_include_test)
    must_train_set = set(must_include_train)

    overlap_vt = must_val_set & must_train_set
    assert not overlap_vt, f"Conflict: subjects {overlap_vt} appear in both must_include_val and must_include_train!"
    overlap_vte = must_val_set & must_test_set
    assert not overlap_vte, f"Conflict: subjects {overlap_vte} appear in both must_include_val and must_include_test!"
    overlap_tte = must_test_set & must_train_set
    assert not overlap_tte, f"Conflict: subjects {overlap_tte} appear in both must_include_test and must_include_train!"

    # Target ~30% audited in validation and test
    target_audited_val = min(len(audited) // 4, max(4, round(val_count * 0.30))) if val_count > 0 else 0
    target_verified_val = val_count - target_audited_val

    val_audited = [s for s in must_include_val if s in audited]
    val_verified = [s for s in must_include_val if s in verified]

    pinned_all = must_val_set | must_test_set | must_train_set
    remaining_audited = [s for s in audited if s not in pinned_all]
    remaining_verified = [s for s in verified if s not in pinned_all]

    random.shuffle(remaining_audited)
    random.shuffle(remaining_verified)

    while len(val_audited) < target_audited_val and remaining_audited:
        val_audited.append(remaining_audited.pop())

    while len(val_verified) < target_verified_val and remaining_verified:
        val_verified.append(remaining_verified.pop())

    val_subjects = sorted(set(val_audited + val_verified))

    # Test cohort selection
    test_audited = [s for s in must_include_test if s in audited]
    test_verified = [s for s in must_include_test if s in verified]

    if test_count > 0:
        target_audited_test = min(len(audited) // 4, max(4, round(test_count * 0.30)))
        target_verified_test = test_count - target_audited_test

        while len(test_audited) < target_audited_test and remaining_audited:
            test_audited.append(remaining_audited.pop())

        while len(test_verified) < target_verified_test and remaining_verified:
            test_verified.append(remaining_verified.pop())

    test_subjects = sorted(set(test_audited + test_verified))

    assigned_eval = set(val_subjects) | set(test_subjects)
    train_subjects = sorted([s for s in eligible if s not in assigned_eval])
    phase2_train_audited = sorted([s for s in train_subjects if audits[s].is_audited])
    orphans = sorted([s for s, a in audits.items() if not a.is_eligible])

    # Strict Zero-leakage assertions
    assert not (set(val_subjects) & set(train_subjects)), f"FATAL LEAKAGE Val & Train: {set(val_subjects) & set(train_subjects)}"
    assert not (set(test_subjects) & set(train_subjects)), f"FATAL LEAKAGE Test & Train: {set(test_subjects) & set(train_subjects)}"
    assert not (set(val_subjects) & set(test_subjects)), f"FATAL LEAKAGE Val & Test: {set(val_subjects) & set(test_subjects)}"

    return val_subjects, test_subjects, train_subjects, phase2_train_audited, orphans


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset_root", type=Path, required=True, help="Path to deidentified-new")
    parser.add_argument("--qc_excel", type=Path, default=None, help="Path to Solix_Outliers.xlsx")
    parser.add_argument("--protocol", type=str, default="Disc Cube", help="Scan protocol")
    parser.add_argument("--val_count", type=int, default=20, help="Number of validation subjects")
    parser.add_argument("--test_count", type=int, default=0, help="Number of test subjects (0 for 2-way split)")
    parser.add_argument(
        "--must_include_val",
        type=str,
        default="BEH0174,BEH0310,BEH0314,BEH0335,BEH0352,BEH0354,BEH0090,BEH0284,BEH0259,BEH0084,BEH0264,BEH0343,BEH0303",
        help="Comma-separated subjects pinned in validation",
    )
    parser.add_argument(
        "--must_include_test",
        type=str,
        default="",
        help="Comma-separated subjects pinned in test",
    )
    parser.add_argument("--output_dir", type=Path, default=Path("manifests"), help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    audits = audit_cohort(args.dataset_root, args.qc_excel, protocol=args.protocol)
    must_val = [s.strip() for s in args.must_include_val.split(",") if s.strip()]
    must_test = [s.strip() for s in args.must_include_test.split(",") if s.strip()]

    val_subjs, test_subjs, train_subjs, p2_audited, orphans = split_cohort(
        audits,
        val_count=args.val_count,
        test_count=args.test_count,
        must_include_val=must_val,
        must_include_test=must_test,
        seed=args.seed,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "cohort_split_summary.json"
    val_path = args.output_dir / "validation_manifest.json"
    test_path = args.output_dir / "test_manifest.json"
    p1_path = args.output_dir / "phase1_train_manifest.json"
    p2_path = args.output_dir / "phase2_audited_train_manifest.json"
    orphans_path = args.output_dir / "cohort_orphans.json"

    val_scans = [asdict(s) for subj in val_subjs for s in audits[subj].scans]
    test_scans = [asdict(s) for subj in test_subjs for s in audits[subj].scans]
    p1_scans = [asdict(s) for subj in train_subjs for s in audits[subj].scans]
    p2_scans = [asdict(s) for subj in p2_audited for s in audits[subj].scans if s.bad_xml_path]

    summary = {
        "dataset_root": str(args.dataset_root),
        "protocol": args.protocol,
        "total_matched_subjects": len(train_subjs) + len(val_subjs) + len(test_subjs),
        "validation": {
            "count": len(val_subjs),
            "scan_count": len(val_scans),
            "audited_count": sum(1 for s in val_subjs if audits[s].is_audited),
            "verified_count": sum(1 for s in val_subjs if not audits[s].is_audited),
            "subjects": val_subjs,
        },
        "test": {
            "count": len(test_subjs),
            "scan_count": len(test_scans),
            "audited_count": sum(1 for s in test_subjs if audits[s].is_audited),
            "verified_count": sum(1 for s in test_subjs if not audits[s].is_audited),
            "subjects": test_subjs,
        },
        "phase1_train": {
            "count": len(train_subjs),
            "scan_count": len(p1_scans),
            "subjects": train_subjs,
        },
        "phase2_audited_train": {
            "count": len(p2_audited),
            "scan_count": len(p2_scans),
            "subjects": p2_audited,
        },
        "orphans": {
            "count": len(orphans),
            "subjects": orphans,
            "reasons": {s: audits[s].orphan_reason for s in orphans},
        },
    }

    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    val_path.write_text(json.dumps({"subjects": val_subjs, "scans": val_scans}, indent=2) + "\n", encoding="utf-8")
    if args.test_count > 0:
        test_path.write_text(json.dumps({"subjects": test_subjs, "scans": test_scans}, indent=2) + "\n", encoding="utf-8")
    p1_path.write_text(json.dumps({"subjects": train_subjs, "scans": p1_scans}, indent=2) + "\n", encoding="utf-8")
    p2_path.write_text(json.dumps({"subjects": p2_audited, "scans": p2_scans}, indent=2) + "\n", encoding="utf-8")
    orphans_path.write_text(json.dumps({"orphans": orphans, "reasons": summary["orphans"]["reasons"]}, indent=2) + "\n", encoding="utf-8")

    print("\n" + "=" * 70)
    print("=== COHORT SPLIT COMPLETE ===")
    print("=" * 70)
    print(f"Total Matched Subjects:       {summary['total_matched_subjects']}")
    print(f"Validation Cohort:            {len(val_subjs)} subjects ({len(val_scans)} scans)")
    print(f"  - Audited (Corrected):      {summary['validation']['audited_count']}")
    print(f"  - Machine (Verified):       {summary['validation']['verified_count']}")
    if args.test_count > 0:
        print(f"Test Cohort (Untouched):      {len(test_subjs)} subjects ({len(test_scans)} scans)")
        print(f"  - Audited (Corrected):      {summary['test']['audited_count']}")
        print(f"  - Machine (Verified):       {summary['test']['verified_count']}")
    print(f"Phase 1 Broad Train Cohort:   {len(train_subjs)} subjects ({len(p1_scans)} scans)")
    print(f"Phase 2 Audited Train Cohort: {len(p2_audited)} subjects ({len(p2_scans)} paired scans)")
    print(f"Orphan / Excluded Subjects:   {len(orphans)}")
    print(f"Zero-Leakage Status:          VERIFIED (0 overlap between Train, Val, Test)")
    print("=" * 70)
    print(f"Artifacts written to: {args.output_dir}")


if __name__ == "__main__":
    main()
