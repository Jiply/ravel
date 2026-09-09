# Ravel

A minimal, dark commit picker inside Codex. Invoke `/ravel` with a repository, select **↑ Into**, review the generated instruction, and click **Confirm** to send it to the same task.

The picker reads Git history locally and never rewrites it itself. It shows the current branch's first-parent chain, keeps merges separate, and supports multiple groups, undo, and reset. The confirmed instruction pins the repository and HEAD and asks Codex to preserve the final file tree and create a backup before rewriting.

Requires Git, Python 3, and a Codex desktop host with inline visualizations and the follow-up message bridge. The plugin has no runtime packages, network service, or credentials.

Install Ravel from the personal plugin marketplace. In a new task, select the Ravel skill using `/` or invoke `$ravel` with the target repository.

## A quieter way to shape history

Concept mockups generated with imagegen showing anonymous people using the interface, with fictional commit labels and messages.

![A person browsing commit history on a MacBook](assets/mockups/history.png)

Combine adjacent commits into separate groups, with undo at every step.

![A person grouping commits on a MacBook](assets/mockups/groups.png)

Review the instruction before sending it to Codex.

![A person reviewing the instruction at a desktop Mac](assets/mockups/confirm.png)
