# Ravel

![Textured pastel paper strips gathering into one sculptural coil](assets/thumbnail.png)

A minimal, dark Git commit picker embedded in a Codex Desktop conversation. Group adjacent commits, preview the instruction, and select **Confirm** to send it back to the same task.

## Set up Codex

1. Install [Codex Desktop](https://developers.openai.com/codex/app), sign in, and open your local project folder.
2. Install the [Codex CLI](https://developers.openai.com/codex/cli) and check that `codex plugin --help` works. The CLI registers the plugin; Desktop displays the picker.
3. Install Git and Python 3, available as `git` and `python3` in the environment where Codex runs commands. Install [Git LFS](https://git-lfs.com/) to download the cover artwork.

Ravel has no build step, runtime packages, server, or API keys of its own. It requires a Desktop host that supports inline HTML visualizations and `window.openai.sendFollowUpMessage`. A terminal-only Codex session cannot display the interactive picker. Managed workspaces may restrict custom plugins.

## Install Ravel

Run these commands in a terminal, using the same Codex profile as your Desktop instance:

```sh
git lfs install
git clone https://github.com/Jiply/ravel.git
cd ravel
codex plugin marketplace add .
codex plugin add ravel@ravel
```

The included marketplace points at this checkout. Keep it available for updates. Cloning alone does not install the plugin. While the GitHub repository is private, cloning requires repository access.

Restart Desktop and start a new task in the project you want to work on. Select Ravel from the `/` skill picker, or send:

```text
Use $ravel to open this repository's commit history.
```

The task's project is the target, not the Ravel checkout. Codex uses the current working directory when it clearly identifies the intended repository; Git resolves subdirectories to their repository root. If you are in a parent workspace with several repositories, Ravel asks which one. You can also provide an explicit target:

```text
Use $ravel for the repository at ./my-project.
```

Hover or focus the information icon beside the repository name to check the full path. The branch is shown beneath it. Install separately in each Codex profile you want to use; an existing task may not discover a newly installed skill.

## Shape the history

Select **↑ Into** on an older commit to combine it with the newer group above. Use **Undo** or **Reset** to change the selection, inspect **Preview instruction**, then select **Confirm**.

The picker reads the current branch's first-parent chain, newest first. Merge commits form boundaries. It loads 200 commits by default; ask Codex to load more, up to 5,000.

Confirm sends a request to Codex; the interface does not run a rebase. The request pins the repository, branch, and HEAD, retains the newer target's message, and preserves the final file tree. Codex must stop for dirty worktrees, operations in progress, or stale selections, create a backup ref before rewriting, and verify the result. It does not push automatically. Rewriting history changes commit IDs, including affected descendants.

## Update or remove

From your Ravel checkout:

```sh
git pull --ff-only
codex plugin remove ravel@ravel
codex plugin add ravel@ravel
```

Restart Desktop and use a new task. To uninstall completely:

```sh
codex plugin remove ravel@ravel
codex plugin marketplace remove ravel
```

## Troubleshooting

- **Ravel is missing:** run `codex plugin list`, check that it is installed and enabled in the same profile as Desktop, then restart and open a new task. Upgrade the CLI if it does not recognize `plugin`.
- **Wrong repository:** supply the target path explicitly and check the path information icon before selecting commits.
- **No history:** the target must be a local Git repository with at least one commit. Two adjacent non-merge commits are needed to form a squash group.
- **Picker or Confirm unavailable:** the host must support both inline visualizations and the follow-up bridge. Preview instruction remains readable when the bridge is missing; it does not mean a request was sent. Browser previews and CLI sessions are not substitutes for the Desktop bridge.
- **Cover missing:** run `git lfs pull`. The artwork is optional for functionality.

The local marketplace installation is tested with Codex CLI 0.153.4 on macOS. The UI has been exercised in Codex Desktop and in browser tests with a simulated bridge. Compatibility with every Desktop version, account, operating system, or managed workspace is not established. See the [official plugin setup documentation](https://developers.openai.com/plugins/build/plugins) for host installation details.

## Privacy and contributions

Ravel has no analytics or network requests of its own. The generated local HTML contains repository paths, commit subjects, and hashes. Confirm sends the selected hashes and repository identity into your Codex conversation, where your Codex account's data policies apply. Do not publish rendered pickers from private repositories.

Bug reports and pull requests are welcome. Use fictional repositories when sharing examples, and include your Desktop/CLI versions and reproduction steps. Keep changes focused; Ravel needs no dependency installation or build. Run the renderer tests with `python3 -B -m unittest discover -s tests`.

The cover is AI-generated artwork. Ravel is an independent project and is not affiliated with or endorsed by OpenAI.

## License and attribution

Ravel is available under the [MIT License](LICENSE). See [AUTHORS.md](AUTHORS.md) for named contributor credits.
