#!/bin/sh
# Per-file symlink dotfiles into place.
# If a real file already exists at the target, adopt it into the repo (overwrite the repo
# working copy with it), then link. Review or drop the adopted content with git afterwards.
# With --restore, drop all repo working-tree changes back to the committed version after
# linking, so the machine snaps to what is committed (applied live through the links).
# Linux only. config/ links into ~/.config, home/ links into ~.
set -eu

repo=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

restore=0
for a in "$@"; do
    case "$a" in
        --restore) restore=1 ;;
        -h|--help) echo "usage: install.sh [--restore]"; exit 0 ;;
        *) echo "unknown arg: $a" >&2; exit 2 ;;
    esac
done

# Ensure $1 exists as real directories. Remove any symlink standing in for a path
# component (e.g. a folded stow package link, maybe now dangling) so files land in the
# real tree instead of being written through a stale link.
ensure_dir() {
    dir=$1
    p=$dir
    while [ -n "$p" ] && [ "$p" != "/" ] && [ "$p" != "." ]; do
        [ -L "$p" ] && rm -- "$p"
        parent=${p%/*}
        [ "$parent" = "$p" ] && break
        p=$parent
    done
    mkdir -p -- "$dir"
}

link_root() {
    src_root=$1
    dst_root=$2
    [ -d "$repo/$src_root" ] || return 0
    find "$repo/$src_root" -type f | while IFS= read -r src; do
        rel=${src#"$repo/$src_root/"}
        dst=$dst_root/$rel
        ensure_dir "${dst%/*}"
        if [ -L "$dst" ]; then
            [ "$(readlink -- "$dst")" = "$src" ] && continue
            rm -- "$dst"
        elif [ -e "$dst" ]; then
            if [ ! -f "$dst" ]; then
                echo "skip (not a regular file): $dst" >&2
                continue
            fi
            mv -- "$dst" "$src"   # adopt existing file into the repo
        fi
        ln -s -- "$src" "$dst"
    done
}

link_root config "$HOME/.config"
link_root home "$HOME"

if [ "$restore" -eq 1 ]; then
    git -C "$repo" checkout HEAD -- .
    echo "Linked. Adopted changes dropped; repo and live config now at the committed version."
else
    echo "Linked. Pre-existing files were adopted into the repo; review with: git -C \"$repo\" status"
fi
