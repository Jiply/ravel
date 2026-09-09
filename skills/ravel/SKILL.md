---
name: ravel
description: Open an interactive Git commit picker inside Codex when the user invokes /ravel or asks to visually select commits to squash in a target repository. Confirm sends the selected groups back into the same task.
---

# Ravel

Use the bundled renderer; do not rebuild the interface or rewrite Git history when opening it.

1. Resolve the user's target repository. Use the current working directory only if it is the clearly intended repository. If a workspace contains multiple repositories and no target is specified, ask which repository to open.
2. Run `python3 <plugin-root>/scripts/render.py <repository> --output <absolute-visualization-path>/ravel.html`. Resolve `<plugin-root>` two directories above this SKILL.md's containing directory. Quote paths as literal shell arguments. Use this task's visualization directory from the environment when provided; otherwise create a unique directory under `~/.codex/visualizations/` and use its absolute path. The default is 200 commits; use `--limit` up to 5000 when the user asks for more.
3. Display the generated file with `::codex-inline-vis{file="/absolute/path/to/ravel.html"}` on its own line in the final answer, then yield so the user can select commits. This is an in-Codex visualization, not a browser URL or a Markdown file link. Do not launch a web server or external browser.

The picker reads the current branch's first-parent chain, newest first. Merge commits are visible boundaries and cannot be combined. Each selected edge joins the older commit's group into the surviving newer commit above. Confirm calls `window.openai.sendFollowUpMessage({prompt})` from the user's click and returns the exact full hashes, repository, branch, and expected HEAD to the current task. It does not execute Git commands.

When the confirmed instruction arrives, handle that requested squash. Validate the pinned repository, branch, and HEAD; stale selections require a refreshed picker. Follow the instruction's backup, working-tree, chronology, final-tree, and no-push constraints. A newer target means retaining its message while combining the group's patches in their original oldest-to-newest order, not replaying old patches after the newer commit. Preserve unselected commits and report the resulting groups and backup ref.

If rendering fails, report the actual error; do not show demo history. If the host lacks inline visualizations or the follow-up bridge, explain the limitation. The preview remains readable, but do not claim a prompt was sent or history was changed.
