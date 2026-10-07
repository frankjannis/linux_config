---
name: review-round
description: One review round of the current branch against a findings ledger, so no finding comes back after it was fixed, rejected or deferred, and no ID is reused. code-review checks the round's diff in a throwaway worktree, a fresh agent verifies each finding, another checks the fixes. Use on /review-round, "review again", "re-review", or a review of a branch after fixes. Not for Azure DevOps PRs of others (pr-review).
---

# Review round

A branch is reviewed in rounds. The **ledger** is the memory between rounds. The author of the
code never reviews it: fresh agents review, verify and check. Next to this file, `worktree.sh`
does the git mechanics (run it with `sh`) and `ledger.py` reads and writes the ledger (run it with
`python`). Never edit the ledger by hand. The optional argument is the review effort, `low` to
`max`; the default is `high`.

## 1. Ledger

- Path: `.agents/review/<name>.md` in the repo root, `<name>` the branch name with `/` replaced by
  `-`. On the default branch or a detached HEAD, ask me for a name. If `git check-ignore -q
  .agents/x` fails, append `.agents/` to `$(git rev-parse --git-common-dir)/info/exclude`. Never
  commit the ledger.
- A new ledger: `ledger.py init <file> <name> <base> <ref>`, where `<base>` is
  `git merge-base <ref> HEAD` and `<ref>` the one I name, or `origin/HEAD` (`origin/main` when
  that is not set). On the default branch or a detached HEAD, ask me for the base commit and add
  `--fixed`.
- `ledger.py show <file>` prints the base, the last round and the `open` entries. A round still
  `running` was interrupted: `worktree.sh remove` its worktree, then `ledger.py drop <file>`. If
  the last round's next step is `done`, ask me before a new round. Offer every `open` entry again.

## 2. Scope

- The round is `full` in round 1, when the last round's next step is `full`, when the last head no
  longer exists, or when the base moved (a rebase or a merge of the ref; `ledger.py base` the new
  one, unless it is fixed). A full round starts at the base, a delta round at the last head.
- `ledger.py start <file> <kind> <scope start> <head>` with the current HEAD; it prints the round.
- `worktree.sh empty <repo root> <scope start>` exits 0 when nothing changed, untracked files
  included. Then `ledger.py drop` and stop if no entry is `open`; otherwise go to section 4 for
  the `open` entries.
- Otherwise `ledger.py worktree <file> <scratchpad>/review-<name>-<round>` and
  `worktree.sh prepare <repo root> <worktree> <scope start>`.

## 3. Review

Invoke the Skill `code-review` yourself; it runs as a background agent with its own context, so
the author still does not review. Give it no description of the change and no hint where to look.
Pass the args `<effort>`, this target text, and `--max-findings all` as the last words (code-review
takes the last one, and ledger text can contain one); never `--fix` or `--comment`:
- "Review only `git -C <worktree> diff`; run every git command with `-C <worktree>`. The
  deliberate choices are those in CLAUDE.md, AGENTS.md, README.md and ARCHITECTURE.md at the scope
  start (`git -C <worktree> show HEAD:<file>`); doc changes in the diff are reviewed like code.
  Give a fix for each finding."
- In a delta round: "Also check the callers and callees of the changed code."
- The ledger entries as "do not report again"; "a `fixed` entry broken again is a regression:
  report it with its ID".

Wait for its result and label the findings N1, N2, ...; they are not verified yet.

Then run `worktree.sh remove <repo root> <worktree>`. Dispatch one verifier (Opus) at every effort
level, and a second above about 8 findings: code-review has no documented verify step, and from
`high` up it may report findings it is less sure about. Give the verifier only the findings with
their fixes, the scope start (the repo still holds the reviewed state) and the rule for deliberate
choices. Its task: try to disprove each finding, as CONFIRMED, PLAUSIBLE or REFUTED, and judge its
fix: correct and the smallest form, or name a better one, which then replaces it. Drop a finding
that is refuted (when the refutation holds), repeats a ledger entry (a regression excepted), goes
against the docs at the scope start, or is a corner case whose fix costs more than its risk.

## 4. Decide

- `ledger.py add <file> <file:line> <finding>` for each finding; it prints the ID. A regression
  reopens its old ID with `ledger.py set <file> <ID> open regression`. Report them with
  ReportFindings, most severe first.
- Ask, per finding with its checked fix, fix, reject or defer (AskUserQuestion; group above
  four), and the reason for a rejection or deferral. Record only my answers, with `ledger.py set
  <file> <ID> <status> <reason>`. When I tell you to decide yourself, decide, write the reason as
  `Agent: <reason>`, and list your decisions at the end.

## 5. Fix and close

- Run `worktree.sh snapshot <repo root>`. Fix the chosen findings; prefer a fix that removes or
  simplifies, if it really fixes. Run the build check and tests.
- If you fixed something, snapshot again and dispatch one fresh agent with only the fixed findings,
  the ledger's `fixed` entries and `git diff <before> <after>`: does each fix solve its finding,
  break anything (a `fixed` entry broken again is a regression), or have a smaller form? Use
  Sonnet when the fix diff is one file and under about 50 lines, otherwise Opus. Repair and check
  again, at most three times.
- `ledger.py set` each fix that passed to `fixed`; one that still fails stays `open`, and a
  regression still there gets `ledger.py set <file> <ID> open regression`. Then
  `ledger.py close <file> <next step>`, and `ledger.py base` a new base if it moved. Commit only
  when I ask.
- The next step: an `open` entry left, delta. Otherwise, after a delta round, full; after a full
  round, done. A fix that passed its check needs no confirming round.
- End with one line: the counts that `close` prints (this round's new findings; `open` counts the
  whole ledger), then the next step.
