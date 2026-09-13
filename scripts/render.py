#!/usr/bin/env python3
"""Render a read-only Git snapshot as a self-contained Codex visualization."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def git(repo, *args):
    """Read Git data using literal arguments, never a shell."""
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repo), *args],
        capture_output=True, check=False,
    )
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", "replace").strip())
    return result.stdout.decode("utf-8", "replace").rstrip("\n")


def snapshot(repo, limit):
    """Read a consistent first-parent history pinned to the current HEAD."""
    root = git(repo, "rev-parse", "--show-toplevel")
    head = git(root, "rev-parse", "--verify", "HEAD")
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD")
    records = git(root, "log", head, "--first-parent", f"--max-count={limit + 1}",
                  "--format=%H%x00%P%x00%aI%x00%s%x00").split("\0\n")
    commits = []
    for record in records:
        if not record:
            continue
        sha, parents, date, subject, *_ = record.split("\0")
        commits.append({"hash": sha, "parents": parents.split(), "date": date,
                        "subject": subject})
    if git(root, "rev-parse", "HEAD") != head or git(root, "rev-parse", "--abbrev-ref", "HEAD") != branch:
        raise ValueError("Repository changed while loading. Run Ravel again.")
    return {"repository": root, "name": Path(root).name, "branch": branch,
            "head": head, "commits": commits[:limit], "hasMore": len(commits) > limit}


def render(data, output):
    """Embed repository data and the UI into one offline HTML file."""
    assets = Path(__file__).resolve().parent.parent / "assets"
    serialized = json.dumps(data, ensure_ascii=True).replace("<", "\\u003c")
    html = (assets / "ravel.html").read_text(encoding="utf-8")
    html = html.replace("/* RAVEL_MODEL */", (assets / "model.js").read_text(encoding="utf-8"))
    html = html.replace("/* RAVEL_DATA */ null", serialized)
    output = Path(os.path.abspath(Path(output).expanduser()))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    print(str(output))


def main():
    """Create the commit picker for a repository supplied by the user."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()
    if not 2 <= args.limit <= 5000:
        parser.error("--limit must be between 2 and 5000")
    try:
        render(snapshot(args.repository.expanduser().resolve(), args.limit), args.output)
    except (ValueError, OSError) as error:
        print(f"Ravel: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
