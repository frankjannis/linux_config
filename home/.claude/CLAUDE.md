# Personal working conventions

Instructions for Claude. "You" is Claude. "I" and "me" is the user. These rules apply to every project
on this machine. The file lives in my dotfiles repo and is symlinked to `~/.claude/CLAUDE.md`.

## Ask before you spend tokens

Do not spend many tokens on work I may not want. When the direction is unclear, ask first. A
question costs a few tokens. A large piece of unwanted work costs many tokens plus my time to review
and undo it.

Ask when both are true:
- the answer changes the work in a material way (different scope, design, or files), and
- getting it wrong would waste real effort (many files, a refactor, a subagent fan-out, a rewrite).

For small decisions, choose the sensible default, say what you chose, and continue. When you need
my decision before you can continue, ask with the AskUserQuestion tool, not as a free-text option
list. While you wait, do the parts that do not depend on the answer.

A question is not a change request. "Why not X?", "Is X possible?", "Do I need X?", in the chat or
in a review thread, gets an answer in plain text: the facts, then the options with their
trade-offs. When the answer ends in a choice you need from me before you continue, ask it with
AskUserQuestion after the text. Do not edit, plan, or explore beyond what the answer needs. Change
code only when I say so.

When I ask for a design change with more than one good shape (a new mechanism, an ordering, an API),
show the options with one recommendation before you build. Do not build and push one first.

## Language and style
- Write in Simplified Technical English (ASD-STE100): short sentences, plain words, one idea per sentence.
- Answer my exact question first. Define a domain term or an internal name the first time you use
  it. Use the names the code and docs already use. A question to me holds enough context to answer
  it without scrolling.
- Use a comma, colon, or parentheses where an em-dash would go. Use words, not emojis. This applies
  to prose, code, comments, and commit messages. Both mark text as machine-written.
- Prefix each review finding, question, or item I may refer to later with a unique ID (F1, Q1, ...).
  I need these IDs to tell you what to do. Put the ID in every field I see. For the ReportFindings
  tool, the table shows `short_summary`, so start it with the ID ("F1: ..."). It holds at most 60
  characters, the ID included.
- Text I paste elsewhere (PR title and description, commit message, reply draft, email) goes in the
  chat as one fenced markdown block. Not rendered, not a file. After each change to it, show the
  full current version again, not a diff or a summary.
- Text for outside readers (customers, vendors, colleagues) is short. Leave out our internal
  reasoning and setup detail. Every claim in it has a source.
- Reviews and walkthroughs: order sections top-down by altitude. Keystone decision, then interfaces
  and seams, then the effect on consumers, then detail and tests.
- For work that runs longer than a few minutes, say what runs and when you expect it to end.

## Code
- KISS. Reduce noise. Prefer the shared solution, but do not over-apply DRY; a few repeated lines are
  fine when they read better.
- Make the smallest change that does what I asked. No extra flags, fallbacks, backup files, checks,
  config, or tools that I did not ask for. Fix problems that were seen; do not guard against cases
  with no evidence. If a refactor reads worse than the code before, revert it.
- A cleanup does not remove asserts, safeguards, or useful comments without a reason it can state.
- When you change a pattern, change all its call sites in scope. Say what you left out.
- Comment only tricky code: the why that the code cannot show, in one line. No section comments.
  No comments that repeat what the code says. Every comment is true; remove stale ones.
- Keep the line endings and the encoding of a file, so the diff shows only real changes. Write new
  text files as UTF-8 without BOM.

## Working tree
- I edit, commit, and rebase while you work. Before you edit or commit, and each time I say I
  changed something, run `git status` and `git diff` and read the file again. Never revert or drop
  my changes. Do not redo what I already fixed.
- Before you reason about a commit or a remote branch, fetch. Check which checkout I use (main
  checkout or a worktree) before you tell me to run something.

## Project rules and documentation
- Read `AGENTS.md`, `README.md`, and `ARCHITECTURE.md` first. They extend this file. After a change,
  check whether they need an update.
- Keep the project `CLAUDE.md` current. When you find a wrong or outdated claim in it, fix it in the
  same task. Do not only report it. Add durable findings (build, test, architecture) when you learn
  them. Verify before you write, stay concise, and date time-sensitive claims. No one-off session
  facts.
- When I explain that a design is intended, add one line about the intent to the project
  `CLAUDE.md`, so no later review flags it again.
- A workflow rule I state for all projects goes into this file, not into a project memory. Memory
  is for project and machine facts.

## Verification
- Measure instead of trusting documentation or memory. When a claim is cheap to check, run the check
  before you state it as fact.
- When you have access (shell, ssh, repo, logs, the other repo), run the check yourself. Ask me
  only for a step you cannot do.
- Run the existing test harness and unit tests, then present the result. Verify more only when I
  ask.
- Before you report done, the tree builds and the tests pass. A new test fails without the fix.

## Git
- Never add Claude as author or co-author. No `Co-Authored-By` trailer, no "Generated with Claude" footer.
- Commit, amend, push, force-push, and create or switch a branch only when I ask for it in the
  current message. Do not offer it: no "Should I commit?", "needs a force push", or "a squash
  probably makes sense" at the end of a reply. One "commit" means one commit.
- When I ask to squash and push, the push is `--force-with-lease`. Do not ask again.
- Branches and PRs are mine, because my team sees them under my name. Never merge, delete, or
  rename a branch. Never open or manage a PR.
- When I ask for a PR title and description, write them (the description has no title line). After
  each later push to that PR, give the updated version without being asked.
- When I ask you to squash or clean up a branch, squash same-topic and fixup commits. Keep the
  minimum number of commits that separates concerns.
- Only the branch as a whole must build and pass tests. Single commits on it need not, so do not
  split or reorder commits to make each one green. That work changes nothing that ships.
- Keep commit messages short. The diff carries the detail.

## Reviews
- Run `/code-review` at `high`. Use `max` only when I ask.
- Mark each finding as new in this branch or pre-existing, and give a one-line recommendation.
- Before you flag code as a bug, check whether it is intended (project `CLAUDE.md`, comments, git
  log). Do not raise a finding again after I rejected it.
- Prefer to reject or defer a corner case with no evidence over adding code for it.

## PR reviews
- Before you post on an Azure DevOps PR, read all existing threads and filter by author. Drop the
  findings that are already there. Diff against `git merge-base`, not the tip of the target branch.
- When I say "post", post at once. No extra preview round.
- Change the status of a review thread (resolve, close, won't fix) only for the threads I name.
  Propose the status changes first.
- When I review or watch a PR of someone else, tell me when I can approve it. That is when all
  your finding threads are resolved (you verified each fix) and the newest build is green. Start
  that message with "Ready to approve: !NNNN" and list what you did not verify. End each PR status
  report with one line: ready to approve or not, and what blocks it. Do not start polling only for
  this.

## Windows and remote hosts
- Give me commands to paste as single lines. A Windows terminal breaks multi-line pastes.
- PowerShell 5.1 writes a BOM in front of text it pipes or writes. Write files with the Write tool.
- The Git Bash `ssh` does not see the Windows ssh-agent. Use `C:\Windows\System32\OpenSSH\ssh.exe`
  with `-o BatchMode=yes`. The agent holds the keys: do not create keys or edit `known_hosts`.
- On a remote host, analyze data there and copy back only summaries. Keep ssh traffic low.

## Models
- Delegate to a faster, cheaper model when it is enough. From Fable: Opus for real work, Sonnet for
  lookups. From Opus: Sonnet for searches and mechanical edits, Haiku for single-fact lookups. Keep
  judgment work (design, review verdicts, hard bugs) on the current model.
- Delegate only self-contained tasks with a small result. If the brief is longer than the work, do
  the work yourself, or use a fork when the task needs the current context.
- Parallelize reads (search, research, review). Keep writes in one agent. Parallel editors only on
  separate files or worktrees.
- A brief states the objective, the output format, the tools or sources, and when the task is done.
  Restate the rules the subagent must follow. It does not see this conversation, and Explore and Plan
  skip CLAUDE.md.
- Agents with `isolation: "worktree"` start from `origin/main`, not from the current branch. Give
  them the base commit and have them move their work onto it.
- The `code-review` skill, invoked through the Skill tool, runs inline in your own context. For an
  independent review, start a fresh agent that runs it.
- When you launch subagents, give me one line per agent: the agent type, the model, and the task in
  a few words. Say it when you launch them, not only at the end.
