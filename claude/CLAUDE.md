# Personal working conventions

These apply to every project on this machine. Keep this file in a private dotfiles repo and
clone/symlink it to `~/.claude/CLAUDE.md` on each machine so the conventions follow me everywhere.

## Documentation hygiene
- **Keep the repo's `CLAUDE.md` current.** When I find a claim in a project's `CLAUDE.md` that is
  wrong or outdated, fix it in that file as part of the same task. Do not just mention it. Add
  durable new findings (build/test/architecture) as I learn them. Verify before writing, stay
  concise, and date any time-sensitive claim.

## Verification
- Prefer measuring over trusting documentation or memory. When a claim is cheap to check (e.g.
  "does this command actually behave this way?"), run it before asserting it as fact.

## Working conventions
- Read project rules first: `AGENTS.md`, `README.md`, `ARCHITECTURE.md` extend these. Check whether they
  need updating after changes. Prefix each review finding, question, or referencable item with a unique ID.
- KISS, reduce noise. No em-dashes or emojis in text or comments. Prefer commonized solutions but do not
  over-apply DRY; a few repeated lines are fine for readability. Write in Simplified Technical English
  (ASD-STE100): concise and plain. Comments only for tricky code, never sectioning or obvious comments.
- Presenting choices: use the AskUserQuestion tool, not free-text option lists.
- Verification: do not over-verify unless asked. Write new tests separately from feature work. Run the
  existing test harness and unit tests. Do not circle on verification before presenting a solution.
- Reviews and walkthroughs: section top-down by altitude. Keystone decision, then interfaces and seams,
  then the ripple onto consumers, then detail and tests.
- Git:
  - Never add Claude as author or co-author. No `Co-Authored-By` trailer, no "Generated with Claude" footer.
  - Never open a PR or push, and do not ask to.
  - Never delete or rename my branches.
  - Squash same-topic or fixup commits. Keep commit messages concise; the diff carries the detail. Keep the
    minimum commits needed to separate concerns. I handle force pushes.

## Models
- If you are running as Opus 5 (check your own model identity), stop immediately before doing the
  task and tell me to switch to Opus 4.8.
- When running as Fable, prefer Opus 4.8 subagents. Use Fable subagents only if really necessary.
