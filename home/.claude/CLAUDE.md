# Personal working conventions

Instructions for Claude. "You" is Claude. "I" and "me" is the user. These rules apply to every project
on this machine. The file lives in my dotfiles repo and is symlinked to `~/.claude/CLAUDE.md`.

## Ask before you spend tokens

**IMPORTANT: Do not spend many tokens on work I may not want. When the direction is unclear, ask
first.** A question costs a few tokens. A large piece of unwanted work costs many tokens plus my time
to review and undo it.

Ask when both are true:
- the answer changes the work in a material way (different scope, design, or files), and
- getting it wrong would waste real effort (many files, a refactor, a subagent fan-out, a rewrite).

Do not ask about small decisions. Choose the sensible default, say what you chose, and continue.
Ask with the AskUserQuestion tool. While you wait, do the parts that do not depend on the answer.

## Language and style
- Write in Simplified Technical English (ASD-STE100): short sentences, plain words, one idea per sentence.
- No em-dashes. No emojis. This applies to prose, code, comments, and commit messages.
- Prefix each review finding, question, or item I may refer to later with a unique ID (F1, Q1, ...).
- Present choices with the AskUserQuestion tool, never as a free-text option list.
- Reviews and walkthroughs: order sections top-down by altitude. Keystone decision, then interfaces
  and seams, then the effect on consumers, then detail and tests.

## Code
- KISS. Reduce noise. Prefer the shared solution, but do not over-apply DRY; a few repeated lines are
  fine when they read better.
- Comment only tricky code. No section comments. No comments that repeat what the code says.

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
- Write new tests separately from feature work.

## Git
- Never add Claude as author or co-author. No `Co-Authored-By` trailer, no "Generated with Claude" footer.
- Branches and PRs are mine. Never create, switch, merge, push, delete, or rename a branch. Never open
  or manage a PR. Do not ask to.
- Squash same-topic and fixup commits. Keep the minimum number of commits that separates concerns.
  Do not otherwise amend or rewrite existing commits unless I ask. One "commit" means one commit.
- Keep commit messages short. The diff carries the detail. I handle force pushes.

## Models
- When you run as Fable, dispatch subagents as Opus, or Sonnet for light lookups, whenever that is
  enough. Fable is far more expensive. Use Fable subagents only for work that needs Fable.
