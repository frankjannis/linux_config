# linux_config

Personal dotfiles for an Arch Linux + Wayland setup. Plain git, no external tool.
`install.sh` makes per-file symlinks from this repo into your home directory.

## Layout
The top-level folder name is the link target:
- `config/` mirrors `~/.config` (e.g. `config/fish/config.fish` -> `~/.config/fish/config.fish`)
- `home/` mirrors `~` (e.g. `home/.claude/CLAUDE.md` -> `~/.claude/CLAUDE.md`)

New home-dir dotfiles just drop into `home/`.

## Install (Linux)
```
git clone https://github.com/frankjannis/linux_config.git ~/Documents/linux_config
cd ~/Documents/linux_config
sh install.sh
```
`install.sh` links every file per file. If a target is already a real file, it is **adopted**:
its content is copied over the repo's working copy, then the target is replaced by the link.
Git is the safety net: `git diff` shows how the machine differed, `git restore` drops the
adopted content back to the committed repo version (applied live through the link). Re-running
is idempotent: a link that already points here is left alone.

To make a machine match the repo in one step, discarding whatever was there:
```
sh install.sh --restore
```
`--restore` links, then runs `git checkout HEAD -- .`, so the repo working tree (and the live
config through the links) returns to the committed version. It discards all uncommitted repo
changes, so commit anything you want to keep first.

Because the links point back at the repo, editing a file here changes the live config
immediately. No apply or sync step. Edit on any machine, commit, `git pull` on the others.
`git diff` shows your local edits and `git restore .` reverts them live.

## Per-machine sway config
Pick the device profile once per machine:
```
ln -sfn ~/.config/sway/notebook ~/.sway_device_conf   # or: work
```
`~/.config/sway/config` includes `~/.sway_device_conf`. This choice is local and not tracked.

## tmux
tmux auto-loads the config for new sessions. Reload a running session:
```
tmux source-file ~/.config/tmux/tmux.conf
```

## Windows
`install.sh` is Linux only, and the Linux configs are not used on Windows. The one file worth
linking there is the global Claude config. In an **admin** PowerShell (or with Developer Mode
on), run from the repo root:
```powershell
$dst="$HOME\.claude\CLAUDE.md"; $src="$PWD\home\.claude\CLAUDE.md"; New-Item -ItemType Directory -Force "$HOME\.claude" | Out-Null; $probe="$HOME\.claude\.symlink_probe"; New-Item -ItemType SymbolicLink -Path $probe -Target $src -ErrorAction Stop | Out-Null; Remove-Item $probe; $cur=Get-Item $dst -ErrorAction SilentlyContinue; if ($cur -and -not $cur.LinkType) { Move-Item -Force $dst $src } elseif ($cur) { Remove-Item $dst }; New-Item -ItemType SymbolicLink -Path $dst -Target $src
```
Like the Linux installer, this adopts: an existing `~/.claude/CLAUDE.md` is moved over the repo
copy, then replaced by the link. Review or drop the adopted content with git in the repo
(`git diff`, `git restore`). It first probes that symlink creation works, so if you are not in
an admin shell it stops before moving anything. On Linux the same file is linked by
`install.sh` via the `home/` root.

## Notes
- `fish_variables` is tracked and linked. fish rewrites it at runtime through the link, so
  `git diff` shows what changed and `git restore` puts the repo version back. Caveat: if fish
  ever replaces the file by atomic rename instead of writing in place, the symlink breaks and
  updates stop reaching the repo. Check once on a machine: after changing a universal var,
  confirm `readlink ~/.config/fish/fish_variables` still points into this repo.
- Edited on Windows, deployed on Linux. `install.sh` is Linux only.
