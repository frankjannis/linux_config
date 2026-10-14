---
name: missed
description: Short list of what the user may have missed in this conversation - open questions, decisions taken for them, skipped or failed steps, background results, state changes. Covers the time since the last /missed run. Use on /missed or "what did I miss".
---

# What you may have missed

List what the user could have overlooked in this conversation. This is not a recap of
the work: the built-in `/recap` does that. Report only items that need the user's
attention or that were easy to skip in long output.

## Window
Start after the last `/missed` report in this conversation. With no earlier report,
start at the beginning. Say in the first line which window you cover ("Since the last
/missed" or "Whole session").

## Groups
In this order. Leave out a group that has no items.

1. **Needs you:** questions or choices still open, and actions that wait for approval.
   Keep their existing IDs (Q1, F1, ...).
2. **Decided for you:** defaults you chose without asking, and what you chose.
3. **Not done or not verified:** skipped steps, failed or unrun tests and builds,
   denied tool calls, errors you worked around, claims you did not check.
4. **Background:** results of subagents, background tasks and workflows, and the
   parts of them you did not pass on to the user. Tasks that still run.
5. **State:** files changed, commits, uncommitted work, running servers or processes,
   open worktrees, temporary files left behind.

## Rules
- At most 12 lines after the window line. When more items qualify, keep the most
  material ones and say how many you left out.
- One line per item, with a new ID (M1, M2, ...; continue after the IDs of the last
  `/missed` report). Point to the source: `file:line`, commit, task, or the turn.
- Every item traces to the conversation or to a command output. Do not reconstruct.
- Run `git status --short` once for the State group. No other exploration, no subagents.
- If the context was summarized in the window, say so in one line: older detail may be
  lost.
- No preamble and no closing offer. When nothing qualifies, say that in one line.
