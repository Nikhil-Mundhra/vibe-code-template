#!/usr/bin/env python3
"""
trim_skills.py — Skill Suite Trimmer & README Synchronizer

Trims the .agents/skills/ suite down to only the skills relevant to the current
project type, and synchronizes the active vs. removed skill lists in README.md.
"""

import os
import sys
import json
import shutil
import argparse
from datetime import datetime

PRESETS = {
    "minimal": [
        "refactor",
        "quality-assurance",
        "document-manipulation",
        "graphify",
        "docmancer",
    ],
    "web-app": [
        "refactor",
        "quality-assurance",
        "document-manipulation",
        "graphify",
        "docmancer",
        "rest-api-caller",
        "glassmorphism-ui",
        "wealth-advisor-ui",
        "humanizer",
        "github-issues",
    ],
    "deep-learning": [
        "refactor",
        "quality-assurance",
        "document-manipulation",
        "graphify",
        "docmancer",
        "diagnose-model-health",
        "kaggle",
        "macbook-cnn-training",
        "cnn-unet-architect",
        "cohort-dataset-splitting",
        "run-segmentation-training",
        "totalsegmentator",
        "scientific-diagram-architect",
    ],
    "data-engineering": [
        "refactor",
        "quality-assurance",
        "document-manipulation",
        "graphify",
        "docmancer",
        "data-lake-and-zone-architecture",
        "data-quality-and-contract-testing",
        "data-reconciliation-and-financial-controls",
        "duckdb-local-analytics-and-dev",
        "feature-store-and-ml-data-pipelines",
        "file-and-partner-feed-ingestion",
        "master-data-and-entity-resolution",
        "notebook-to-production-hardening",
        "python-data-engineering-and-pipeline-packaging",
        "semantic-layer-and-metric-governance",
        "warehouse-and-schema-design",
    ],
}

def load_manifest(repo_root):
    manifest_path = os.path.join(repo_root, "skills-manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def update_readme(repo_root, retained_skills, removed_skills, reason=""):
    readme_path = os.path.join(repo_root, "README.md")
    if not os.path.exists(readme_path):
        return

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Build markdown table for retained skills
    manifest = load_manifest(repo_root)
    retained_rows = []
    for s in sorted(retained_skills):
        desc = manifest.get(s, {}).get("description", "Active skill")[:100]
        cat = manifest.get(s, {}).get("category", "General")
        retained_rows.append(f"| `{s}` | {cat} | {desc} |")
    
    retained_table = (
        "| Skill Name | Category | Description |\n"
        "| :--- | :--- | :--- |\n" +
        "\n".join(retained_rows)
    )

    # Build markdown list for removed skills
    removed_items = []
    for s in sorted(removed_skills):
        cat = manifest.get(s, {}).get("category", "General")
        removed_items.append(f"- `{s}` ({cat})")
    
    removed_list = "\n".join(removed_items) if removed_items else "_No skills removed yet. Full suite intact._"

    # Replace markers if present
    start_active = "<!-- BEGIN_ACTIVE_SKILLS -->"
    end_active = "<!-- END_ACTIVE_SKILLS -->"
    start_removed = "<!-- BEGIN_REMOVED_SKILLS -->"
    end_removed = "<!-- END_REMOVED_SKILLS -->"

    if start_active in content and end_active in content:
        prefix = content.split(start_active)[0]
        suffix = content.split(end_active)[1]
        content = f"{prefix}{start_active}\n\n{retained_table}\n\n{end_active}{suffix}"

    if start_removed in content and end_removed in content:
        prefix = content.split(start_removed)[0]
        suffix = content.split(end_removed)[1]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        annotation = f"\n_Last trimmed on {timestamp}. Reason: {reason}_\n\n" if reason else "\n\n"
        content = f"{prefix}{start_removed}{annotation}{removed_list}\n\n{end_removed}{suffix}"

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description="Trim skill suite to project-relevant skills and update README.")
    parser.add_argument("--preset", choices=list(PRESETS.keys()), help="Apply a predefined project preset")
    parser.add_argument("--keep", help="Comma-separated list of skill names to retain")
    parser.add_argument("--remove", help="Comma-separated list of skill names to delete")
    parser.add_argument("--list", action="store_true", help="List all available skills")
    parser.add_argument("--reason", default="", help="Reason for trimming (recorded in README)")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without deleting files")

    args = parser.parse_args()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    skills_dir = os.path.join(repo_root, ".agents", "skills")

    if not os.path.exists(skills_dir):
        print(f"Error: {skills_dir} not found.")
        sys.exit(1)

    existing_skills = sorted([
        d for d in os.listdir(skills_dir)
        if os.path.isdir(os.path.join(skills_dir, d))
    ])

    if args.list:
        manifest = load_manifest(repo_root)
        print(f"Total existing skills ({len(existing_skills)}):")
        for s in existing_skills:
            cat = manifest.get(s, {}).get("category", "General")
            print(f"  - {s} [{cat}]")
        print("\nAvailable Presets:")
        for p, p_skills in PRESETS.items():
            print(f"  - {p}: {len(p_skills)} skills ({', '.join(p_skills[:4])}...)")
        return

    to_keep = set()
    to_remove = set()

    if args.preset:
        preset_skills = set(PRESETS[args.preset])
        to_keep = preset_skills.intersection(existing_skills)
        to_remove = set(existing_skills) - to_keep
        reason = args.reason or f"Applied preset '{args.preset}'"
    elif args.keep:
        requested_keep = set([s.strip() for s in args.keep.split(",") if s.strip()])
        to_keep = requested_keep.intersection(existing_skills)
        to_remove = set(existing_skills) - to_keep
        reason = args.reason or f"Explicitly kept {len(to_keep)} skills"
    elif args.remove:
        to_remove = set([s.strip() for s in args.remove.split(",") if s.strip()]).intersection(existing_skills)
        to_keep = set(existing_skills) - to_remove
        reason = args.reason or f"Explicitly removed {len(to_remove)} skills"
    else:
        print("Please specify --preset, --keep, --remove, or --list.")
        sys.exit(1)

    print(f"Trimming Plan:")
    print(f"  Retaining ({len(to_keep)}): {', '.join(sorted(to_keep))}")
    print(f"  Removing ({len(to_remove)}): {', '.join(sorted(to_remove))}")

    if args.dry_run:
        print("\n[DRY RUN] No files deleted or modified.")
        return

    # Delete unneeded skills
    for s in to_remove:
        s_path = os.path.join(skills_dir, s)
        if os.path.exists(s_path):
            shutil.rmtree(s_path)
            print(f"  [DELETED] .agents/skills/{s}")

    # Synchronize README
    update_readme(repo_root, to_keep, to_remove, reason)
    print("README.md successfully updated with retained and removed skills.")

if __name__ == "__main__":
    main()
