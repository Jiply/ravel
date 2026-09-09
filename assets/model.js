/** When adjacent commits share a linear edge, allow joining them. */
function canJoin(commits, index) {
  if (index <= 0 || index >= commits.length) return false;
  const newer = commits[index - 1];
  const older = commits[index];
  return newer.parents.length === 1 && older.parents.length <= 1 && newer.parents[0] === older.hash;
}

/** When an edge is selected, resolve its newest surviving commit. */
function targetIndex(joins, index) {
  while (index > 0 && joins.has(index)) index -= 1;
  return index;
}

/** When the selection changes, collect contiguous groups under their newer targets. */
function squashGroups(commits, joins) {
  const groups = [];
  for (let index = 0; index < commits.length; index += 1) {
    if (!joins.has(index)) continue;
    if (!canJoin(commits, index)) throw new Error('Cannot squash across a merge boundary.');
    const target = commits[targetIndex(joins, index)];
    let group = groups.at(-1);
    if (!group || group.target.hash !== target.hash) {
      group = { target, sources: [] };
      groups.push(group);
    }
    group.sources.push(commits[index]);
  }
  return groups;
}

/** When the user confirms, turn the exact snapshot and selection into a Codex instruction. */
function buildPrompt(data, joins) {
  const groups = squashGroups(data.commits, joins);
  if (!groups.length) return '';
  return [
    'Squash the following commits in repository ' + JSON.stringify(data.repository) + ':',
    '',
    ...groups.map(function (group) {
      return (
        group.sources
          .map(function (commit) {
            return commit.hash;
          })
          .join(', ') +
        ' into more recent ' +
        group.target.hash
      );
    }),
    '',
    'Expected branch: ' + JSON.stringify(data.branch),
    'Expected HEAD: ' + data.head,
    '',
    'This is my confirmed Ravel selection. Verify the repository, branch, and HEAD still match before changing history; if they differ, reopen Ravel for a fresh selection.',
    "Keep each target's commit message and combine each group's changes in their original chronological order. Preserve all unselected commits' changes and messages, and preserve the final HEAD tree. Commit hashes may change as history is rewritten.",
    'Preserve uncommitted work. Stop if the working tree is dirty or a Git operation is in progress. Create a backup ref before rewriting, verify the final tree and selected groups afterward, and do not push.',
  ].join('\n');
}

if (typeof module !== 'undefined') module.exports = { canJoin, targetIndex, squashGroups, buildPrompt };
