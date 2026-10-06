---
name: address-review
description: Work through the open review threads of an Azure DevOps pull request (!NNNN, or the active PR of the current branch), do what each thread asks, commit, and reply in the thread. Use when I say I have reviewed or commented in Azure, or on /address-review [!NNNN | URL] [note].
---

# Address a pull request review (Azure DevOps)

I review in Azure DevOps, not in the chat. This skill brings my threads to you and carries your
answers back. All REST calls go through `ado.py` next to this file (standard-library Python,
API 7.1); its docstring lists the commands. Run it as
`python <this skill's base directory>/ado.py <command>`.

## Token
You need an Azure DevOps Personal Access Token (PAT) with write access: this skill replies in
threads and resolves them, which reading alone cannot do.

- Create it: Azure DevOps -> User settings -> Personal access tokens -> New Token. Org `exacomtech`.
- Scope: cover the projects whose PRs you address (pick the specific projects, or all accessible
  projects for convenience).
- Permission: **Code (Read & Write)**. Read alone cannot post replies or set a thread's status.
- Store the PAT in a file, not in shell history or a committed file. Point the env var
  `AZURE_DEVOPS_PAT_FILE` at that file's path.
- Never print the token; `ado.py` reads it into memory only. `ado.py info` shows the resolved
  repository, branch, and whether the token file is found.

## Steps
The rule of the workflow: nothing leaves this machine until I sign off. You fetch the threads,
we discuss here, you make the changes and draft the replies here, and only after I approve do you
push and write anything back to Azure. No `ado.py reply`/`resolve` and no `git push` before that.

1. Run `ado.py info` first. It resolves the repository and branch and reports whether the token
   file is found, with no network call, so a missing or unreadable PAT fails clearly here. Then
   `ado.py threads [!NNNN]`. `!NNNN` is looked up at the org endpoint, so the current directory
   can be any clone. Without an argument it takes the active PR of the current branch. One block
   per open thread: `T<id>`, status, `file:lines`, then the comments in order. `--all` adds the
   resolved threads, for context only.
2. Digest first: one line per thread with the `T` id, who opened it (me, a named reviewer, or a
   model prefix), the location, and the request in a few words. `threads` prints each comment's
   author, so use it. Then work through them here in the chat. Ask me here (AskUserQuestion)
   whenever a thread is unclear, changes scope, or needs a decision; do the answer-independent
   parts while you wait.
3. Per thread, read the whole thread and the code at the location before you change anything.
   Trust the `file:lines` anchor that `threads` prints: the comment is about that line. Do not
   override it with your own guess that the comment "really" means a nearby line, and check what
   the branch changed at that exact line (a removed or altered log, guard, or call is often the
   point of the comment). A thread that asks a question ("why not X?") is not a change request:
   answer it here with the options and their trade-offs, and change the code only when I pick one.
   A later comment can narrow or withdraw the request, and on a thread with
   several people the last word may be a reviewer's, not mine. A thread whose comment starts with a
   model prefix was posted by a model; it is a review finding too, handle it the same way. A thread
   another person opened is still a real request: fix the code it asks for. But the token posts as
   me, so never invent a reply in my name to a reviewer; if the thread asks something only I can
   answer (intent, a design choice), draft it as an open question for me and leave the thread for
   me to answer.
4. Make the changes in the working tree. Do not commit yet. Run the project's cheap build check
   (here `cargo check`) so that what you show me is already verified.
5. Sign-off gate. Present in the chat, per thread: the change (diff or a tight summary), the
   exact reply you would post (sha as a `<sha>` placeholder since nothing is committed yet), and
   whether you would resolve the thread or leave it open. Do not commit, push, or touch Azure.
   Wait for my explicit go-ahead. I may ask for edits first; fold them into the working tree and
   show me again. My go-ahead approves the resolve/leave-open marks you showed.
6. Only after I sign off: commit by my usual rules (same-topic threads share one commit, no
   thread ids in commit messages), push, then post each reply with
   `ado.py reply T<id> "<text>"` (or `-` with the text on stdin for more than one line), quoting
   the real pushed sha. One or two sentences, starting with a prefix that names the model you are
   actually running as, e.g. `[Opus 4.8] Done in a1b2c3d: ...`. Use your real model, not the one in
   this example. Not done: the reason, or the question I still have to answer. The token is mine,
   so the reply shows my name; the prefix is what says it was you.
7. Resolve, in the same push/reply pass, only the threads I signed off as resolved at the gate:
   `ado.py resolve T<id>`, after posting that thread's reply. Leave open any thread that is
   declined, still carries an open question back to me, or that I said to keep open. Never resolve
   a thread we did not both agree to. A thread another person opened is theirs to close: after
   replying, leave it active so the reviewer can verify and resolve it, unless I explicitly say to
   resolve it.
8. Recap in the chat by `T` id: done with sha (resolved or left open), declined with reason, open
   questions. When the branch has same-topic or fixup commits, remind me a squash before merging
   probably makes sense.

## Arguments
`/address-review [!NNNN | PR URL] [note]`. The note scopes the run, for example "only the GVSP
threads".
