---
name: afk
description: Enter unattended AFK mode - keep working without blocking, bank would-be questions as deferred decisions, resume on "tadaima". A vague but measurable goal ("make the build faster", "make the UI feel more modern") runs as a self-paced improvement loop until stopped.
disable-model-invocation: true
---

# AFK mode

The user is away and will return with the resume signal **tadaima**. Work the task
through to completion on your own. Treat every would-be question as a decision you
make now and record for the user to review later.

## First: last call before the user leaves
This is the only point where you may block on the user. Make it fast: the questions
must arrive within about a minute.

1. **Permission mode.** A permission prompt stalls the run until the user is back. If
   the session's mode is not one that runs tools without asking (auto mode, or bypass
   permissions), put one line at the top of the reply: the run stops at the first
   permission prompt, so change the mode before leaving.
2. **Find the decisions the task will raise.** Read only what you need: the request,
   the project rules (CLAUDE.md, AGENTS.md), the files the task touches. When the task
   spans several areas, scan them in parallel with Explore subagents on Sonnet or
   Haiku, one area each, and ask each for the open decisions only. Look for scope
   limits, design choices that change files or outcome, git actions the rules leave
   open, irreversible steps, missing access, and for a goal loop the metric and guards.
3. **Ask once.** Ask up to eight questions, the most material first. One
   AskUserQuestion call holds four, so use a second call right after the first when
   needed. Decide the rest yourself and bank them as deferred decisions.
4. **Go.** Say in one line that you now work on your own and the user can leave, and
   what you start with. Then start the work. From here on, do not ask.

Skip steps 2 and 3 when the note says so (e.g. "no questions"): a question blocks
until answered, so a user who leaves right after `/afk` would stall the run.

## The contract
- **Decide and proceed.** When a choice arises that you would normally raise, take
  the most defensible option, act on it, and keep moving. Resolve every
  AskUserQuestion-shaped moment this way instead of pausing for the user.
- **Infer the git rules.** Take what you may do with git (branch, commit, push) from
  the user's and the project's rules (CLAUDE.md, AGENTS.md) and from the request. When
  they forbid an action or leave it open, do not take it; bank it. Never rewrite
  history (squash, amend, rebase, force-push) unless the request allows it explicitly;
  a standing rule to squash does not count.
- **Bank irreversible actions, do not take them.** Deleting, publishing or sending
  anything outside the machine waits for the user, and so does a push unless the
  rules allow it. Do the reversible work around them.
- **Bank each deferred decision.** Append it to `.agents/deferred-questions.md` in
  the active project with the next free ID (Q1, Q2, ...; continue the numbering of an
  existing file): the question, the option you took, and a one-line why. Create the
  file on the first entry. It is the durable record that survives a long session
  where context gets summarized.
- **Keep the AFK files out of commits.** Never stage `.agents/deferred-questions.md`,
  `.agents/afk-goal.md` or `.agents/afk-goal/`. Stage files by name, not with
  `git add -A` or `git add .`.
- **Run the whole backlog.** Finish the task and its follow-ups; keep working rather
  than winding down to wait for input.
- **Notify when the run ends early.** When the work is done, or blocked so that
  nothing useful is left before the user is back, send one line with
  `PushNotification` (if the tool is available): what ended and why.
- **Mid-session messages still count.** If the user sends a message before the resume
  signal, address it, then continue in AFK mode.

## Goal loop
A goal is **vague but measurable** when it names a direction, not an end state, and
something can tell better from worse. That is a number ("make the tests faster",
"fewer lint warnings", "smaller bundle", "raise coverage of X") or your own judgement
("make the UI feel better and more modern", "make the error messages clearer"). Such a
goal has no completion point, so do not finish it: improve it in a loop until the user
stops you.

1. **Pin the metric.** Set the guards that must keep passing (the existing tests, the
   build), then the measure. Unless the user settled it in the last call, bank the
   metric choice as a deferred decision.
   - **Number:** one command that prints it and its direction (lower or higher is
     better). Run it three times and take the median when it is noisy.
   - **Judgement:** write a rubric of three to five concrete criteria into the log
     ("one spacing scale", "consistent 4px corners", "clear primary action per page"),
     derived from the goal and the project's own rules (for a UI: its component
     library and the UI rules in its CLAUDE.md). Capture the evidence the rubric
     judges: screenshots of the affected pages (with the project's own screenshot
     tooling, or the session's browser tools), sample outputs. The baseline is that
     evidence, kept under `.agents/afk-goal/`.
2. **Set up the log.** Write `.agents/afk-goal.md`: the goal as stated, the metric
   command, the guards, the baseline, the judge model, and how kept changes are
   stored (commits on which branch, or uncommitted; see the git rules above).
3. **Start the loop.** Invoke the `loop` skill with no interval (self-paced) and this
   prompt: `AFK goal loop: run one iteration of the goal in .agents/afk-goal.md`.
4. **One iteration** per firing:
   - Read `.agents/afk-goal.md` first; it holds the state, not the context.
   - Pick the most promising idea not tried yet. Make one change.
   - Run the guards, then the metric.
   - For a judged goal, capture the new evidence and let a fresh subagent judge it
     against the last kept evidence by the rubric, without telling it which is new.
     Better means it prefers the new one on the rubric and finds no criterion worse.
     Pick the judge model by the rubric: Sonnet when the criteria are concrete and
     checkable (counts, consistency, layout rules), Opus when they need taste (design
     quality, clarity of prose).
   - Better and guards pass: keep it. With commits allowed, one commit per kept idea.
     Without, leave it in the working tree.
   - Otherwise revert the change completely. Without commits, restore the files the
     change touched to their state before it (save a checkpoint first with
     `git stash create`, which changes nothing) and remove only the files it added.
   - Append one line to the log: idea, metric before and after (or the judge's reason),
     kept or reverted.
   - Schedule the next firing soon (60 s); nothing external is pending.
5. **Plateau.** After several reverted ideas in a row, widen the search: profile or
   measure where the number comes from, try a larger restructuring, re-read the log
   for ideas that combine. Note the plateau in the log; do not stop.
6. **Never game the metric.** A change that improves the number by skipping, deleting
   or weakening what it measures (disabled tests, removed features, cached results) is
   not an improvement. When unsure, revert it and bank it as a deferred decision.

The loop stops only on the resume signal, an explicit "stop", or a guard that cannot
be made to pass again. On stop, end the loop (`ScheduleWakeup` with `stop: true`) and
add a summary at the top of the log: baseline, current value, kept ideas. When the
loop stops on a guard, notify the user as in the contract.

## Resuming
When the user says **tadaima** (or otherwise signals they are back), stop deferring
and end any goal loop. Report the goal result from `.agents/afk-goal.md` in one line,
then walk them through `.agents/deferred-questions.md` top to bottom by ID, get their
answers, and apply them.

## Arguments
`/afk [resume-word] [note]` - all optional. A custom resume word replaces "tadaima"
for this run; a note (e.g. an ETA, a scope limit, a measurable goal, or "no
questions" to skip the last call) shapes what you work on while away.
