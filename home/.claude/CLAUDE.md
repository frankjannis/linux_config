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

Do not ask about small decisions. Choose the sensible default, say what you chose, and continue.
Ask with the AskUserQuestion tool. While you wait, do the parts that do not depend on the answer.

A question is not a change request. "Why not X?", in the chat or in a review thread, gets an
answer: the facts, then the options with their trade-offs. Change code only when I say so.

## Language and style
- Write in Simplified Technical English (ASD-STE100): short sentences, plain words, one idea per sentence.
- No em-dashes. No emojis. This applies to prose, code, comments, and commit messages.
- Prefix each review finding, question, or item I may refer to later with a unique ID (F1, Q1, ...).
  I need these IDs to tell you what to do. Put the ID in every field I see. For the ReportFindings
  tool, the table shows `short_summary`, so start it with the ID ("F1: ..."). It holds at most 60
  characters, the ID included.
- Present choices with the AskUserQuestion tool, never as a free-text option list.
- Text I paste elsewhere (PR title and description, commit message, reply draft) goes in the chat
  as one fenced markdown block. Not rendered, not a file.
- Reviews and walkthroughs: order sections top-down by altitude. Keystone decision, then interfaces
  and seams, then the effect on consumers, then detail and tests.

## Code
- KISS. Reduce noise. Prefer the shared solution, but do not over-apply DRY; a few repeated lines are
  fine when they read better.
- Comment only tricky code: the why that the code cannot show, in one line. No section comments.
  No comments that repeat what the code says.

## Project rules and documentation
- Read `AGENTS.md`, `README.md`, and `ARCHITECTURE.md` first. They extend this file. After a change,
  check whether they need an update.
- Keep the project `CLAUDE.md` current. When you find a wrong or outdated claim in it, fix it in the
  same task. Do not only report it. Add durable findings (build, test, architecture) when you learn
  them. Verify before you write, stay concise, and date time-sensitive claims.

## Verification
- Measure instead of trusting documentation or memory. When a claim is cheap to check, run the check
  before you state it as fact.
- Do not over-verify unless I ask. Run the existing test harness and unit tests. Do not loop on
  verification before you present a solution.

## Git
- Never add Claude as author or co-author. No `Co-Authored-By` trailer, no "Generated with Claude" footer.
- Commit, amend, push, force-push, and create or switch a branch only when I ask for it in the
  current message. Do not offer it. One "commit" means one commit.
- Branches and PRs are mine. Never merge, delete, or rename a branch. Never open or manage a PR.
- Squash same-topic and fixup commits. Keep the minimum number of commits that separates concerns.
- Single commits on a branch do not have to build or pass tests on their own. Only the branch as a
  whole must build and pass. Do not split or reorder commits to make each one green.
- Keep commit messages short. The diff carries the detail.

## Models
- When you run as Fable, dispatch subagents as Opus, or Sonnet for light lookups, whenever that is
  enough. Fable is far more expensive. Use Fable subagents only for work that needs Fable.
- When you launch subagents, give me one line per agent: the agent type, the model, and the task in
  a few words. Say it when you launch them, not only at the end.
