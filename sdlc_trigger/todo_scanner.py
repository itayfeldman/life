"""
todo_scanner.py

Scans for #TODO: [Description] patterns in the repository.

Two modes:
  - git_diff: only scan files changed in the latest push (used by git hook)
  - full_scan: scan all tracked files (used by cron job)
"""

import re
import subprocess
import os
from dataclasses import dataclass
from typing import List

TODO_PATTERN = re.compile(r"#TODO:\s*(.+)", re.IGNORECASE)

@dataclass
class TodoItem:
    file: str
    line_number: int
    description: str
    raw_line: str

    def __str__(self):
        return f"[{self.file}:{self.line_number}] {self.description}"


def _scan_file(filepath: str) -> List[TodoItem]:
    todos = []
    try:
        with open(filepath, "r", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                match = TODO_PATTERN.search(line)
                if match:
                    todos.append(TodoItem(
                        file=filepath,
                        line_number=i,
                        description=match.group(1).strip(),
                        raw_line=line.strip(),
                    ))
    except (OSError, PermissionError):
        pass
    return todos


def scan_git_diff(repo_root: str = ".") -> List[TodoItem]:
    """Scan only files changed in the latest commit."""
    try:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", "HEAD"],
            capture_output=True, text=True, cwd=repo_root
        )
        changed_files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except Exception:
        changed_files = []

    todos = []
    for rel_path in changed_files:
        abs_path = os.path.join(repo_root, rel_path)
        if os.path.isfile(abs_path):
            todos.extend(_scan_file(abs_path))
    return todos


def scan_full_repo(repo_root: str = ".") -> List[TodoItem]:
    """Scan all git-tracked files in the repository."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True, text=True, cwd=repo_root
        )
        all_files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except Exception:
        all_files = []

    todos = []
    for rel_path in all_files:
        abs_path = os.path.join(repo_root, rel_path)
        if os.path.isfile(abs_path):
            todos.extend(_scan_file(abs_path))
    return todos


def deduplicate(todos: List[TodoItem]) -> List[TodoItem]:
    """Remove duplicate descriptions (same text, different location)."""
    seen = set()
    unique = []
    for t in todos:
        key = t.description.lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(t)
    return unique
