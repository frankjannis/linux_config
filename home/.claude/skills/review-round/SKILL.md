---
name: review-round
description: One review round of the current branch against a findings ledger, so no finding comes back after it was fixed, rejected or deferred, and no ID is reused. A fresh agent reviews the round's diff in a throwaway worktree, another verifies each finding, a third checks the fixes. Use on /review-round, "review again", "re-review", or a review of a branch after fixes. Not for Azure DevOps PRs of others (pr-review).
---

# Review round

A branch is reviewed in rounds. The **ledger** is the memory between rounds. The author of the
code never reviews it: fresh agents review, verify and check. `worktree.sh` next to this file does
the git mechanics; run it with `sh` in Bash.

## 1. Ledger

- Path: `.agents/review/<name>.md` in the repo root, `<name>` the branch name with `/` replaced by
  `-`. On the default branch or a detached HEAD, ask me for a name. If `git check-ignore -q
  .agents/x` fails, append `.agents/` to `$(git rev-parse --git-common-dir)/info/exclude`. Never
  commit the ledger.
- It holds the base, a findings table and a rounds log.
  - Base: a commit and the ref it came from, `git merge-base <ref> HEAD`. The ref is the one I
    name, or `origin/HEAD` (`origin/main` when that is not set). On the default branch or a
    detached HEAD, ask me for the base commit; it is fixed.
  - Findings: ID (`F1`, `F2`, ..., continued across rounds), status (`open`, `fixed`, `rejected`,
    `deferred`), `file:line`, the finding in one line, and the reason for a rejection or deferral.
  - Rounds: number, kind (`full` or `delta`), scope start, head, worktree, counts, next step.
- A round still marked `running` was interrupted: remove its worktree with `worktree.sh remove`
  and delete its row. If the ledger says `done`, ask me before a new round.
- Offer every `open` entry again.

## 2. Scope

- The round is `full` in round 1, when the last round's next step is `full`, when the last head no
  longer exists, or when the base moved (a rebase or a merge of the ref; take the new base). A
  full round starts at the base, a delta round at the last head.
- Add the round as `running`: kind, scope start and head (the current HEAD).
- `worktree.sh empty <repo root> <scope start>` exits 0 when nothing changed, untracked files
  included. Then delete the row and stop if no entry is `open`; otherwise go to section 4 for the
  `open` entries, and close the row in section 5 as usual.
- Otherwise record the worktree `<scratchpad>/review-<name>-<round>` in the row and run
  `worktree.sh prepare <repo root> <worktree> <scope start>`.

## 3. Review

Dispatch one reviewer (Opus), without `isolation: "worktree"` (it leaves a branch behind). Give it
the worktree, the round kind and the ledger entries; no description of the change and no hint where
to look. Tell it to:
1. Invoke the Skill `code-review` with the args `high`, this target text, and `--max-findings all`
   as the last words (code-review takes the last one, and ledger text can contain one):
   - "Review only `git -C <worktree> diff`; run every git command with `-C <worktree>`. The
     deliberate choices are those in CLAUDE.md, AGENTS.md, README.md and ARCHITECTURE.md at the
     scope start (`git -C <worktree> show HEAD:<file>`); doc changes in the diff are reviewed like
     code."
   - In a delta round: "Also check the callers and callees of the changed code."
   - The ledger entries as "do not report again"; "a `fixed` entry broken again is a regression:
     report it with its ID". "Return your findings as plain text; SubagentHandback is not
     available to you."
2. Not pass `--fix` or `--comment`, and not call ReportFindings or AskUserQuestion. Wait for every
   agent it starts.
3. Return the findings labelled N1, N2, ...: `file:line`, the defect, a scenario, the fix. If
   code-review did not review exactly that diff, review it itself and say so.

Then run `worktree.sh remove <repo root> <worktree>`. Dispatch one verifier (Opus), a second above
about 8 findings, to try to disprove each finding: CONFIRMED, PLAUSIBLE or REFUTED. Drop a finding
that is refuted (when the refutation holds), repeats a ledger entry (a regression excepted), goes
against the docs at the scope start, or is a corner case whose fix costs more than its risk.

## 4. Decide

- Give the findings the next free IDs and write them as `open` at once. A regression reopens its
  old ID. Report them with ReportFindings, most severe first.
- Ask, per finding, fix, reject or defer (AskUserQuestion; group above four), and the reason for a
  rejection or deferral. Record only my answers. When I tell you to decide yourself, decide, write
  the reason as `Agent: <reason>`, and list your decisions at the end.

## 5. Fix and close

- Run `worktree.sh snapshot <repo root>`. Fix the chosen findings; prefer a fix that removes or
  simplifies, if it really fixes. Run the build check and tests.
- If you fixed something, snapshot again and dispatch one fresh agent (Opus) with the findings and
  `git diff <before> <after>`: does each fix solve its finding, break anything, or have a smaller
  form? Repair and check again, at most three times; a fix that still fails stays `open`.
- Mark the rest `fixed`. Close the row: counts, next step, no `running`; write a new base if it
  moved. Commit only when I ask.
- End with one line: the counts, then the next step. Fixes made or an `open` entry left: a delta
  round. None after a delta round: a full round. None after a full round: done.
