---
name: review-round
description: One review round of the current branch against a persistent findings ledger, so no finding comes back after it was fixed, rejected or deferred, and no ID is reused. Runs /code-review in a throwaway worktree, has each finding attacked by a separate verifier, and ends with a full-branch round. Use on /review-round, "review again", "re-review", or a review of a branch after fixes. Not for Azure DevOps PRs of others (pr-review).
---

# Review round

A branch is reviewed in rounds. The **ledger** is the memory between rounds: it survives
compaction and new sessions. Every round reads it first and writes it last. The author of the code
never reviews it: every review and every verification is done by a fresh agent. `worktree.sh` next
to this file does all worktree mechanics; run it with `sh` in Bash.

## 1. Open the ledger

- Path: `.agents/review/<name>.md` in the repo root. `<name>` is the branch name with `/` replaced
  by `-`. On the default branch or a detached HEAD, ask me for a name. If `git check-ignore -q
  .agents/x` fails, append `.agents/` to `$(git rev-parse --git-common-dir)/info/exclude`. Never
  commit the ledger.
- A new ledger records its name, the base, a findings table and a rounds log. The base is
  `git merge-base <default> HEAD`, unless I name another. `<default>` is
  `git symbolic-ref -q --short refs/remotes/origin/HEAD`, or `origin/main` when that is not set.
  - Findings: ID (`F1`, `F2`, ..., continued across rounds), status (`open`, `fixed`, `rejected`,
    `deferred`), `file:line`, the finding in one line, and my reason for a rejection or deferral.
  - Rounds: number, kind (`full` or `delta`), scope start, head, worktree path, the counts, and
    the next step (`delta`, `full` or `done`).
- If the ledger says `done`, ask me before you start a new round on it.
- If the last round is marked `running`, a round was interrupted: run
  `worktree.sh remove <repo root> <its worktree>` and delete its row. The last round is then the
  one before it. Findings the interrupted round wrote stay in the table.
- Offer every `open` entry again: it is fixed in this round, or I set a new status.
- Done when you know the base, the last round, and every entry.

## 2. Scope

- Recompute the base: `git merge-base <default> HEAD`, or `git merge-base <named base> HEAD` when I
  named one. The kind of this round is:
  - `full` in round 1, when the last round's next step is `full`, when the base differs from the
    base in the ledger (a rebase or a merge of the default branch; then update the ledger base), or
    when the last head no longer exists (`git cat-file -e <last head>^{commit}` fails). Say why. A
    full round reviews from the base.
  - `delta` otherwise. A delta round reviews from the last head, also after a squash.
- The scope is the working state, uncommitted and untracked changes included, against the scope
  start. It is empty when `git diff --quiet <scope start>` succeeds and
  `git ls-files --others --exclude-standard` prints nothing.
  - Empty, and no entry is `open`: stop, and say the branch has nothing new.
  - Empty, but entries are `open`: go to section 4 for them, without a review.
- Add the round to the rounds log as `running`, with its kind, scope start, head (the current
  HEAD) and worktree path `<scratchpad>/review-<round number>`. Then run
  `worktree.sh prepare <repo root> <worktree> <scope start>`. It stops if the path exists.

## 3. Review

Dispatch one reviewer (Opus), without `isolation: "worktree"`: that option leaves a branch per
agent behind. Say one line when you launch it.

Give the reviewer the worktree path, the round kind and every ledger entry, each marked "do not
report again" with its status and reason. Give it no description of the change, no suspicion and
no hint where to look. Tell it to:
1. Invoke the Skill `code-review` with the args `high`, then this target text, then
   `--max-findings all` as the last words. code-review takes the last `--max-findings` in the args,
   and the ledger text can contain one. The target text:
   - "Review only the diff of the worktree <worktree>. Run every git command as
     `git -C <worktree> ...`. The scope is exactly `git -C <worktree> diff`; do not diff against a
     branch, upstream or HEAD~1."
   - "The deliberate choices are those in CLAUDE.md, AGENTS.md, README.md and ARCHITECTURE.md at
     the scope start (`git -C <worktree> show HEAD:<file>`). Doc changes inside the scope are
     reviewed like code."
   - In a delta round: "Also read the callers and callees of every changed function, and the code
     that relies on the changed behaviour, and report what the change breaks there."
   - The ledger entries as "do not report again". "A `fixed` entry that is broken again is a
     regression: report it with its ID."
   - "Return your findings as plain text at the end. SubagentHandback is not available to you."
2. Never pass `--fix` or `--comment`. Do not call ReportFindings or AskUserQuestion.
3. If you or the Skill start agents, wait for every result before you return.
4. Return the findings as text: `file:line` (in the repo, not the worktree path), the defect, the
   evidence or failure scenario, and the fix.
5. If the Skill cannot be invoked, or the files it says it reviewed do not match
   `git -C <worktree> diff --stat`, review the diff for correctness bugs yourself and say so in
   the first line.

When the reviewer has reported, run `worktree.sh remove <repo root> <worktree>`.

Then dispatch one verifier (Opus), and a second one above about 8 findings. Give it the findings,
the same ledger entries and the rule for deliberate choices. Its task: try to disprove each finding
against the code in the main tree, and return CONFIRMED, PLAUSIBLE or REFUTED with the evidence.

Drop a finding when it is:
- REFUTED and the refutation holds when you read it;
- a repeat of a ledger entry, except a regression of a `fixed` entry;
- against a deliberate choice in the docs at the scope start.

Done when every surviving finding has a confirmed `file:line`, a verdict and a concrete fix.

## 4. Decide

- Give the new findings the next free IDs and write them to the ledger as `open` at once. A
  regression keeps its old ID: set that entry back to `open`.
- Report them with ReportFindings, most severe first. ReportFindings takes only CONFIRMED and
  PLAUSIBLE: for a finding kept after a REFUTED verdict, use PLAUSIBLE and give the refutation in
  the summary.
- Then ask, for each finding, fix, reject or defer (AskUserQuestion). Group the findings when there
  are more than four. Ask the reason for each rejection or deferral, and record only the reason I
  give. Record each answer in the ledger at once.
- When I reject a finding as intended design, propose the one line for `CLAUDE.md` or
  `ARCHITECTURE.md` that would have prevented it.

## 5. Fix and close

- Fix only the chosen findings. Run the project's build check and tests.
- Mark them `fixed`. Close the round in the rounds log: keep the head in its row, add the counts
  and the next step, and remove `running`. Save the ledger. Uncommitted fixes then show up in the
  next round's scope, so they get reviewed too.
- Commit only when I ask.
- End with one line: the counts of new, fixed, rejected, deferred and still-open findings, then the
  next step. Rejected and deferred findings do not count here:
  - Fixes made in this round, or an `open` entry left: another delta round.
  - No fix and no `open` entry after a delta round: a full round as the final check.
  - No fix and no `open` entry after a full round: the branch is done.
