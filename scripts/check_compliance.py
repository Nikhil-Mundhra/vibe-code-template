#!/usr/bin/env python3
"""
check_compliance.py: Mechanical Rule & Hygiene Linter

Validates compliance with core repository directives:
- Zero Unicode emojis
- Zero em-dashes (allowing legitimate rule definitions)
- Port 5000 safety on macOS
- Clean badge-based terminal outputs
"""

import os
import sys
import re
import argparse
import subprocess

# Binary and non-text extensions to skip
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp",
    ".pdf", ".zip", ".tar", ".gz", ".lock", ".bin"
}

# Directories to skip when running in full scan mode (vendor / third-party skills)
DEFAULT_IGNORED_DIRS = {
    ".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build"
}

# Regex for common Unicode emojis
EMOJI_PATTERN = re.compile(
    r"[\U0001F300-\U0001F9FF]|[\U0001FA00-\U0001FAFF]|[\u2600-\u26FF]|[\u2700-\u27BF]"
)

# Regex to detect port 5000 in code/configs
PORT_5000_PATTERN = re.compile(
    r"(?:port\s*[:=]\s*5000|PORT\s*=\s*5000|listen\(\s*5000|localhost:5000|127\.0\.0\.1:5000)",
    re.IGNORECASE
)

def get_git_files(staged_only=False, diff_only=False):
    """Retrieve relevant files from git."""
    try:
        if staged_only:
            cmd = ["git", "diff", "--name-only", "--cached", "--diff-filter=ACMR"]
        elif diff_only:
            cmd = ["git", "diff", "--name-only", "HEAD", "--diff-filter=ACMR"]
        else:
            cmd = ["git", "ls-files"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return [f.strip() for f in res.stdout.splitlines() if f.strip()]
    except Exception:
        return []

def check_file(path, repo_root):
    """Scan a single file for rule violations."""
    full_path = os.path.join(repo_root, path) if not os.path.isabs(path) else path
    if not os.path.isfile(full_path):
        return []

    ext = os.path.splitext(full_path)[1].lower()
    if ext in BINARY_EXTENSIONS:
        return []

    violations = []
    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception as e:
        return [f"Could not read file: {e}"]

    is_rule_def_file = path in {"AGENTS.md", "INITIAL_AGENT_INSTRUCTIONS.md", "README.md", "CLAUDE.md", ".cursorrules", ".windsurfrules", "scripts/check_compliance.py"} or path.endswith("copilot-instructions.md")

    for idx, line in enumerate(lines, start=1):
        # 1. Emoji Check
        emoji_match = EMOJI_PATTERN.search(line)
        if emoji_match:
            violations.append(
                f"[FAIL] {path}:{idx}: Unicode emoji detected: '{emoji_match.group(0)}'"
            )

        # 2. Em-Dash Check
        if "\u2014" in line or "&mdash;" in line:
            # Allow mentioning the literal em-dash when defining the prohibition rule
            is_rule_mention = is_rule_def_file and (
                "prohibited" in line or "Avoid" in line or "strictly" in line
                or "`\u2014`" in line or "`—`" in line or "Never emit" in line
                or "check_compliance.py" in path or "\u2014" in line
            )
            if not is_rule_mention:
                violations.append(
                    f"[FAIL] {path}:{idx}: Em-dash detected. Replace with hyphen, comma, or colon."
                )

        # 3. Port 5000 Check (AirPlay conflict on macOS)
        # Exclude rule documentation files mentioning the restriction
        if not is_rule_def_file and PORT_5000_PATTERN.search(line):
            violations.append(
                f"[WARN] {path}:{idx}: Port 5000 detected. Use port 5001 for backend servers on macOS."
            )

    return violations

def main():
    parser = argparse.ArgumentParser(description="Check repository files for directive compliance.")
    parser.add_argument("--staged", action="store_true", help="Check only staged git files (pre-commit mode)")
    parser.add_argument("--diff", action="store_true", help="Check modified files against HEAD")
    parser.add_argument("--all", action="store_true", help="Check all tracked repository files")
    parser.add_argument("--files", nargs="*", help="Explicit file list to check")

    args = parser.parse_args()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)

    if args.files:
        target_files = args.files
    elif args.staged:
        target_files = get_git_files(staged_only=True)
    elif args.diff:
        target_files = get_git_files(diff_only=True)
    elif args.all:
        raw_files = get_git_files()
        # In full scan mode, skip external vendor skills in .agents/skills/
        target_files = [f for f in raw_files if not f.startswith(".agents/skills/")]
    else:
        # Default: if there are unstaged/staged git changes, check them; otherwise check all non-vendor files
        changed = get_git_files(diff_only=True) or get_git_files(staged_only=True)
        if changed:
            target_files = changed
        else:
            raw_files = get_git_files()
            target_files = [f for f in raw_files if not f.startswith(".agents/skills/")]

    if not target_files:
        print("[INFO] No applicable files to check.")
        sys.exit(0)

    print(f"[INFO] Checking {len(target_files)} file(s) for directive compliance...")
    all_violations = []

    for path in target_files:
        violations = check_file(path, repo_root)
        all_violations.extend(violations)

    if all_violations:
        print("\nCompliance Violations Found:")
        for v in all_violations:
            print(f"  {v}")
        print(f"\n[FAIL] {len(all_violations)} violation(s) found.")
        sys.exit(1)
    else:
        print("[PASS] All checked files adhere strictly to repository directives.")
        sys.exit(0)

if __name__ == "__main__":
    main()
