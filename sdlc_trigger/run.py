#!/usr/bin/env python3
"""
run.py

Main entry point for the SDLC TODO trigger pipeline.

Usage:
  python run.py --mode cron              # Full repo scan (used by cron job)
  python run.py --mode git               # Git diff scan (used by post-receive hook)
  python run.py --mode cron --dry-run    # Print TODOs found without calling API
"""

import argparse
import os
import sys
from datetime import datetime

# Ensure local imports work
sys.path.insert(0, os.path.dirname(__file__))

from todo_scanner import scan_full_repo, scan_git_diff, deduplicate
from experiment_architect import process_todos

DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "experiment_briefs")


def get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.")
        sys.exit(1)
    return key


def main():
    parser = argparse.ArgumentParser(description="SDLC TODO → Experiment Architect pipeline")
    parser.add_argument("--mode", choices=["cron", "git"], required=True,
                        help="cron = full repo scan, git = changed files only")
    parser.add_argument("--repo", default=".", help="Path to the git repository root")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR,
                        help="Directory to write experiment briefs into")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print TODOs found without calling the API")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  SDLC Trigger — Experiment Architect Pipeline")
    print(f"  Mode: {args.mode.upper()} | {datetime.utcnow().isoformat()}Z")
    print(f"{'='*60}\n")

    # Step 1: Scan for TODOs
    print(f"[1/3] Scanning repository for #TODO annotations...")
    if args.mode == "git":
        todos = scan_git_diff(repo_root=args.repo)
        print(f"      Scanning git diff (changed files only)")
    else:
        todos = scan_full_repo(repo_root=args.repo)
        print(f"      Scanning full repository")

    todos = deduplicate(todos)

    if not todos:
        print("      No #TODO items found. Pipeline complete.\n")
        sys.exit(0)

    print(f"\n      Found {len(todos)} unique #TODO item(s):")
    for t in todos:
        print(f"        • {t}")

    # Step 2: Dry run — stop here
    if args.dry_run:
        print("\n[DRY RUN] Skipping API calls. Exiting.\n")
        sys.exit(0)

    # Step 3: Call Experiment Architect for each TODO
    print(f"\n[2/3] Sending TODO(s) to Experiment Architect agent...")
    api_key = get_api_key()
    generated = process_todos(todos, api_key=api_key, output_dir=args.output_dir)

    # Step 4: Summary
    print(f"\n[3/3] Pipeline complete.")
    print(f"      {len(generated)} experiment brief(s) generated:")
    for f in generated:
        print(f"        • {f}")
    print()


if __name__ == "__main__":
    main()
