#!/usr/bin/env python3
"""
issue-auditor.py: Precise agent toolkit to inspect, audit, verify, and close GitHub issues.
Rules: Zero external dependencies beyond python3, git, and gh CLI. No emojis.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Set, Tuple


def run_cmd(cmd: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    """Execute command returning exit code, stdout, stderr."""
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def check_prerequisites() -> None:
    """Ensure gh and git are available."""
    code, _, _ = run_cmd(["gh", "--version"])
    if code != 0:
        sys.stderr.write("Error: 'gh' CLI is not installed or not in PATH.\n")
        sys.exit(1)
    code, _, _ = run_cmd(["git", "--version"])
    if code != 0:
        sys.stderr.write("Error: 'git' is not installed or not in PATH.\n")
        sys.exit(1)


def get_issue(issue_id: int) -> Dict[str, Any]:
    """Fetch issue details as JSON."""
    code, stdout, stderr = run_cmd([
        "gh", "issue", "view", str(issue_id),
        "--json", "number,title,body,state,labels,assignees,url"
    ])
    if code != 0:
        sys.stderr.write(f"Error fetching issue #{issue_id}: {stderr}\n")
        sys.exit(1)
    return json.loads(stdout)


def list_issues(state: str = "open", limit: int = 50) -> List[Dict[str, Any]]:
    """List issues from repository."""
    code, stdout, stderr = run_cmd([
        "gh", "issue", "list",
        "--state", state,
        "--limit", str(limit),
        "--json", "number,title,state,labels,updatedAt"
    ])
    if code != 0:
        sys.stderr.write(f"Error listing issues: {stderr}\n")
        sys.exit(1)
    return json.loads(stdout)


def extract_referenced_files(text: str) -> List[str]:
    """Extract code/doc file paths mentioned in issue text."""
    # Matches backticked paths, words ending in common code extensions, or path patterns
    patterns = [
        r"`([a-zA-Z0-9_\-\./]+\.[a-zA-Z0-9]+)`",
        r"`([a-zA-Z0-9_\-\./]+/)`",
        r"\b([a-zA-Z0-9_\-\.]+(?:/[a-zA-Z0-9_\-\.]+)+\.[a-zA-Z0-9]+)\b",
        r"\b((?:rules|contracts|backend|frontend|infra|docs|agents)/[a-zA-Z0-9_\-\./]*)\b",
    ]
    files: Set[str] = set()
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            cleaned = m.strip().rstrip(".,:;)")
            # Avoid URLs, git branches, or generic version strings
            if not cleaned.startswith("http") and not cleaned.startswith("git@"):
                files.add(cleaned)
    return sorted(list(files))


def extract_checkboxes(text: str) -> Dict[str, List[str]]:
    """Extract markdown task checklist items."""
    completed = []
    uncompleted = []
    for line in text.splitlines():
        line_clean = line.strip()
        if re.match(r"^[-*]\s+\[x\]\s+", line_clean, re.IGNORECASE):
            completed.append(re.sub(r"^[-*]\s+\[x\]\s+", "", line_clean, flags=re.IGNORECASE))
        elif re.match(r"^[-*]\s+\[\s*\]\s+", line_clean):
            uncompleted.append(re.sub(r"^[-*]\s+\[\s*\]\s+", "", line_clean))
    return {"completed": completed, "uncompleted": uncompleted}


def scan_git_history(issue_id: int, title: str) -> List[Dict[str, str]]:
    """Search git commits mentioning issue id or key terms."""
    query = f"#{issue_id}"
    code, stdout, _ = run_cmd([
        "git", "log", f"--grep={query}", "-n", "10",
        "--pretty=format:%h|%ad|%an|%s", "--date=short"
    ])
    commits = []
    if code == 0 and stdout:
        for line in stdout.splitlines():
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append({
                    "hash": parts[0],
                    "date": parts[1],
                    "author": parts[2],
                    "message": parts[3],
                })

    # Also search keywords from title if no direct issue number commit is found
    if not commits:
        words = [w.lower() for w in re.findall(r"[a-zA-Z]{4,}", title)
                 if w.lower() not in {"from", "with", "that", "this", "what", "which", "into", "every"}]
        for word in words[:2]:
            c, out, _ = run_cmd([
                "git", "log", f"--grep={word}", "-n", "5",
                "--pretty=format:%h|%ad|%an|%s", "--date=short"
            ])
            if c == 0 and out:
                for line in out.splitlines():
                    parts = line.split("|", 3)
                    if len(parts) == 4 and parts[0] not in [x["hash"] for x in commits]:
                        commits.append({
                            "hash": parts[0],
                            "date": parts[1],
                            "author": parts[2],
                            "message": parts[3],
                        })
    return commits


def parse_tracks_from_issue(meta_issue_id: int) -> Dict[str, List[int]]:
    """Extract tracks and member issue IDs from an orchestration issue."""
    issue = get_issue(meta_issue_id)
    body = issue.get("body", "")
    lines = body.splitlines()

    tracks: Dict[str, List[int]] = {}
    current_track: Optional[str] = None

    for line in lines:
        track_match = re.search(r"##\s+(Track\s+\d+[^\n]*)", line, re.IGNORECASE)
        if track_match:
            current_track = track_match.group(1).strip()
            tracks[current_track] = []
            continue

        if current_track:
            # Look for bullet points or references like #8, #12
            issue_matches = re.findall(r"#(\d+)", line)
            for m in issue_matches:
                num = int(m)
                if num != meta_issue_id and num not in tracks[current_track]:
                    tracks[current_track].append(num)

    return tracks


def audit_issue(
    issue_id: int,
    run_typecheck: bool = False,
    run_tests: bool = False,
) -> Dict[str, Any]:
    """Perform a comprehensive audit of an issue against git and local tree."""
    issue = get_issue(issue_id)
    title = issue.get("title", "")
    body = issue.get("body", "")
    state = issue.get("state", "UNKNOWN")

    files = extract_referenced_files(body)
    file_status: List[Dict[str, Any]] = []
    for f in files:
        # Check relative to cwd
        clean_f = f.rstrip("/")
        exists = os.path.exists(clean_f)
        file_status.append({"path": f, "exists": exists})

    checkboxes = extract_checkboxes(body)
    commits = scan_git_history(issue_id, title)

    # Optional verification runs
    typecheck_passed: Optional[bool] = None
    if run_typecheck:
        code, _, _ = run_cmd(["npm", "run", "typecheck"])
        typecheck_passed = (code == 0)

    tests_passed: Optional[bool] = None
    if run_tests:
        code, _, _ = run_cmd(["make", "test"])
        if code != 0:
            code, _, _ = run_cmd(["npm", "test"])
        tests_passed = (code == 0)

    # Determine verdict
    # Criteria:
    # 1. State must not already be closed (if closed, status is CLOSED)
    # 2. Key files mentioned in issue should exist
    # 3. Checkboxes (if any) should be checked
    # 4. Relevant commits exist
    # 5. Tests pass (if run)
    existing_files_ratio = (
        sum(1 for f in file_status if f["exists"]) / len(file_status)
        if file_status else 1.0
    )

    ready_to_close = False
    verdict_reasons: List[str] = []

    if state == "CLOSED":
        verdict = "ALREADY_CLOSED"
        verdict_reasons.append("Issue is already closed on GitHub.")
    else:
        has_commits = len(commits) > 0
        all_uncompleted_empty = len(checkboxes["uncompleted"]) == 0
        files_mostly_exist = existing_files_ratio >= 0.75

        if files_mostly_exist and (has_commits or all_uncompleted_empty):
            if tests_passed is False or typecheck_passed is False:
                verdict = "INCOMPLETE"
                verdict_reasons.append("Automated test or typecheck failed.")
            else:
                verdict = "READY_TO_CLOSE"
                ready_to_close = True
                verdict_reasons.append("Referenced files exist and matching commit records found.")
                if tests_passed:
                    verdict_reasons.append("Automated test suite passed.")
        else:
            verdict = "INCOMPLETE"
            if not files_mostly_exist:
                verdict_reasons.append("Key files referenced in issue description do not exist.")
            if not has_commits:
                verdict_reasons.append("No git commits found addressing this issue.")
            if checkboxes["uncompleted"]:
                verdict_reasons.append(f"{len(checkboxes['uncompleted'])} open task checklist items.")

    return {
        "issue_id": issue_id,
        "title": title,
        "state": state,
        "verdict": verdict,
        "ready_to_close": ready_to_close,
        "reasons": verdict_reasons,
        "referenced_files": file_status,
        "checkboxes": checkboxes,
        "commits": commits,
        "typecheck_passed": typecheck_passed,
        "tests_passed": tests_passed,
    }


def close_issue(issue_id: int, comment: str) -> bool:
    """Close an issue using gh CLI with required comment."""
    code, stdout, stderr = run_cmd([
        "gh", "issue", "close", str(issue_id),
        "--comment", comment
    ])
    if code != 0:
        sys.stderr.write(f"Error closing issue #{issue_id}: {stderr}\n")
        return False
    print(f"Closed issue #{issue_id}: {stdout}")
    return True


def format_audit_report(res: Dict[str, Any]) -> str:
    """Format audit result into GitHub-flavored markdown."""
    lines = [
        f"### Issue #{res['issue_id']}: {res['title']}",
        f"- **Current State**: `{res['state']}`",
        f"- **Audit Verdict**: `{res['verdict']}`",
        f"- **Ready to Close**: `{'YES' if res['ready_to_close'] else 'NO'}`",
        "",
        "#### Findings & Rationale",
    ]
    for r in res["reasons"]:
        lines.append(f"- {r}")

    if res["referenced_files"]:
        lines.append("")
        lines.append("#### Referenced Artifacts")
        for f in res["referenced_files"]:
            status_text = "EXISTS" if f["exists"] else "MISSING"
            lines.append(f"- [{status_text}] `{f['path']}`")

    if res["commits"]:
        lines.append("")
        lines.append("#### Relevant Git Commits")
        for c in res["commits"][:5]:
            lines.append(f"- `{c['hash']}` ({c['date']}): {c['message']}")

    if res["typecheck_passed"] is not None or res["tests_passed"] is not None:
        lines.append("")
        lines.append("#### Automated Checks")
        if res["typecheck_passed"] is not None:
            lines.append(f"- Typecheck: `{'PASS' if res['typecheck_passed'] else 'FAIL'}`")
        if res["tests_passed"] is not None:
            lines.append(f"- Test Suite: `{'PASS' if res['tests_passed'] else 'FAIL'}`")

    return "\n".join(lines)


def main() -> None:
    check_prerequisites()

    parser = argparse.ArgumentParser(
        description="Precise toolkit to inspect, audit, verify, and close GitHub issues."
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # Subcommand: list
    list_p = subparsers.add_parser("list", help="List issues from the repository")
    list_p.add_argument("--state", default="open", choices=["open", "closed", "all"])
    list_p.add_argument("--limit", type=int, default=30)

    # Subcommand: inspect
    inspect_p = subparsers.add_parser("inspect", help="Inspect an issue and extract metadata")
    inspect_p.add_argument("issue_id", type=int)

    # Subcommand: tracks
    tracks_p = subparsers.add_parser("tracks", help="Extract tracks and issue mappings from a meta issue")
    tracks_p.add_argument("meta_issue_id", type=int)

    # Subcommand: audit
    audit_p = subparsers.add_parser("audit", help="Audit issue completion against code and git")
    audit_p.add_argument("issue_id", type=int)
    audit_p.add_argument("--run-typecheck", action="store_true")
    audit_p.add_argument("--run-tests", action="store_true")
    audit_p.add_argument("--json", action="store_true", help="Output raw JSON")

    # Subcommand: close
    close_p = subparsers.add_parser("close", help="Close an issue with an audit comment")
    close_p.add_argument("issue_id", type=int)
    close_p.add_argument("--comment", required=True, help="Resolution comment")

    args = parser.parse_args()

    if args.subcommand == "list":
        issues = list_issues(state=args.state, limit=args.limit)
        print(f"Showing {len(issues)} issues (state: {args.state}):\n")
        print(f"{'ID':<6} {'STATE':<8} {'TITLE'}")
        print("-" * 70)
        for iss in issues:
            print(f"#{iss['number']:<5} {iss['state']:<8} {iss['title']}")

    elif args.subcommand == "inspect":
        issue = get_issue(args.issue_id)
        files = extract_referenced_files(issue.get("body", ""))
        checkboxes = extract_checkboxes(issue.get("body", ""))
        print(f"Issue #{issue['number']}: {issue['title']}")
        print(f"State: {issue['state']}")
        print(f"URL: {issue['url']}")
        print("\nReferenced Files/Paths:")
        for f in files:
            print(f"  - {f}")
        print("\nChecklist Tasks:")
        print(f"  Completed: {len(checkboxes['completed'])}")
        for c in checkboxes["completed"]:
            print(f"    [x] {c}")
        print(f"  Uncompleted: {len(checkboxes['uncompleted'])}")
        for u in checkboxes["uncompleted"]:
            print(f"    [ ] {u}")

    elif args.subcommand == "tracks":
        tracks = parse_tracks_from_issue(args.meta_issue_id)
        print(f"Tracks extracted from meta issue #{args.meta_issue_id}:\n")
        for track_name, issue_ids in tracks.items():
            print(f"{track_name}:")
            for iid in issue_ids:
                iss = get_issue(iid)
                print(f"  - #{iid} ({iss['state']}): {iss['title']}")
            print()

    elif args.subcommand == "audit":
        audit_res = audit_issue(
            args.issue_id,
            run_typecheck=args.run_typecheck,
            run_tests=args.run_tests,
        )
        if args.json:
            print(json.dumps(audit_res, indent=2))
        else:
            print(format_audit_report(audit_res))

    elif args.subcommand == "close":
        success = close_issue(args.issue_id, args.comment)
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
