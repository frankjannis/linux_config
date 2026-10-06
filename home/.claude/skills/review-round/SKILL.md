---
name: review-round
description: One review round of the current branch against a persistent findings ledger, so no finding comes back after it was fixed, rejected or deferred, and no ID is reused. Runs /code-review and /simplify as its engines in throwaway worktrees, has each finding attacked by a separate verifier, and ends with a full-branch round. Use on /review-round, "review again", "re-review", or a review of a branch after fixes. Not for Azure DevOps PRs of others (pr-review).
---

# Review round

A branch is reviewed in rounds. The **ledger** is the memory between rounds: it survives
compaction and new sessions. Every round reads it first and writes it last. The author of the code
never reviews it: every review and every verification is done by a fresh agent.

## 1. Open the ledger

- Path: `.agents/review/<branch>.md` in the repo root, `/` in the branch name replaced by `-`.
  If `git check-ignore -q .agents/x` fails, append `.agents/` to
  `$(git rev-parse --git-common-dir)/info/exclude`. Never commit the ledger.
- A new ledger records the base (`git merge-base origin/main HEAD` unless I name another), a
  findings table and a rounds log.
  - Findings: ID, status (`open`, `fixed`, `rejected`, `deferred`), `file:line`, the finding in one
    line, and my reason for a rejection or deferral. IDs are `F1`, `F2`, ... and continue across
    rounds.
  - Rounds: number, kind (`full` or `delta`), scope start, head, and the counts of the round.
- Done when you know the base, the head of the last round (none on round 1), and every entry.

## 2. Scope

- A **full** round reviews from the base. A **delta** round reviews from the last head.
  - Round 1 is full.
  - A later round is delta, unless the last round was a delta round that found nothing above a nit.
    Then this round is full: it is the final check of the whole branch.
  - Both include uncommitted changes.
- If the scope is empty and no entry is `open`, stop: say the branch has nothing new.
- Write the uncommitted changes to a patch in the scratchpad: `git diff --binary HEAD > <patch>`.

## 3. Review

Dispatch two reviewers in parallel, each with `isolation: "worktree"`:
- Engine A runs `/code-review`, as Opus.
- Engine B runs `/simplify`, as Sonnet.

Say one line per agent when you launch them.

Give each reviewer only this, and no description of the change, no suspicion and no hint where to
look:
- the scope start, the patch path and the original HEAD;
- the doc pointers: the repo's `CLAUDE.md`, `AGENTS.md` and `ARCHITECTURE.md`, whose deliberate
  choices are not findings;
- every ledger entry, each marked "do not report again" with its status and reason. A `fixed` entry
  that is broken again is reported as a regression of that ID.

Tell each reviewer to do these steps in its worktree:
1. Prepare the scope as the current diff: `git reset -q <scope start>`, then
   `git apply --allow-empty --binary <patch>`. HEAD is now the scope start, and the whole scope is
   unstaged. The reset must come after the worktree is at the original HEAD and must keep the
   working tree (no `--hard`), because the patch is taken against the original HEAD.
2. Engine A:
   - Invoke the Skill `code-review` with the args `high`.
   - Never pass `--fix` or `--comment`. Do not call ReportFindings or AskUserQuestion.
   - In a delta round, also read the callers and callees of every changed function, and the code
     that relies on the changed behaviour, and report what the change breaks there.
3. Engine B:
   - Record the baseline with `B=$(git stash create)` (this leaves the tree as it is).
   - Invoke the Skill `simplify` and let it apply its changes.
   - Each hunk of `git diff $B` is one finding, with its diff as the fix.
4. Restore: `git reset -q --hard <original HEAD> && git clean -fdq`, so the worktree is removed.
5. Return the findings as text: `file:line` (in the scope's code, not the worktree path), the
   defect, the evidence or failure scenario, and the fix.
6. If the Skill cannot be invoked or cannot review the prepared diff, review the same diff along the
   same dimension yourself and say so in the first line.

Then dispatch one verifier (Opus), and a second one above about 8 findings. Give it the findings
and the same doc pointers and ledger entries. Its task: try to disprove each finding against the
code in the main tree, and return CONFIRMED, PLAUSIBLE or REFUTED with the evidence.

Drop a finding when it is:
- REFUTED and the refutation holds when you read it;
- a repeat of a ledger entry;
- against a documented deliberate choice.

Done when every surviving finding has a confirmed `file:line`, a verdict and a concrete fix.

## 4. Decide

- Give the new findings the next free IDs and report them with ReportFindings, most severe first,
  with the verifier's verdict. Then ask which to fix (AskUserQuestion, multiSelect). Record each
  answer in the ledger now.
- When I reject a finding as intended design, propose the one line for `CLAUDE.md` or
  `ARCHITECTURE.md` that would have prevented it.

## 5. Fix and close

- Fix only the chosen findings. Run the project's build check and tests.
- Mark them `fixed`. Write the current HEAD as the last head, and add the round to the rounds log.
  Save the ledger. Uncommitted fixes then show up in the next round's scope, so they get reviewed
  too.
- Commit only when I ask.
- End with one line: the counts of new, fixed, rejected, deferred and still-open findings, then the
  next step:
  - Findings above a nit: another delta round.
  - Nothing above a nit in a delta round: a full round as the final check.
  - Nothing above a nit in a full round: the branch is done, and another round is not needed.
