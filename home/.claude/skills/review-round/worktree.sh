#!/bin/sh
# Throwaway review worktrees for the review-round skill. No branch is created.
#
#   worktree.sh prepare <repo> <worktree> <scope start>
#     Makes <worktree> a detached worktree at <scope start> whose files are the current working
#     state of <repo>: commits, uncommitted and untracked changes, deletions. The scope is then
#     exactly `git -C <worktree> diff`. The real index of <repo> is not touched.
#   worktree.sh remove <repo> <worktree>
#     Removes the worktree and its folder, also when git no longer lists it.
set -eu

cmd=${1:?usage: worktree.sh prepare|remove <repo> <worktree> [<scope start>]}
repo=${2:?repo missing}
wt=${3:?worktree missing}

case "$cmd" in
prepare)
    start=${4:?scope start missing}
    if [ -e "$wt" ]; then
        echo "error: $wt already exists; run: worktree.sh remove $repo $wt" >&2
        exit 1
    fi
    # A tree of the working state, built in a copy of the index so the real one stays as it is.
    # No patch file: a diff would pass through textconv and could drop binary files.
    tmp="$wt.index"
    cp "$(git -C "$repo" rev-parse --path-format=absolute --git-path index)" "$tmp"
    GIT_INDEX_FILE="$tmp" git -C "$repo" add -A
    tree=$(GIT_INDEX_FILE="$tmp" git -C "$repo" write-tree)
    rm -f "$tmp"
    git -C "$repo" worktree add -q --detach --no-checkout "$wt" "$start"
    git -C "$wt" read-tree -u --reset "$tree"
    # Back to the scope start in the index only: the scope becomes unstaged, files the scope adds
    # stay visible as intent-to-add, deleted files show as deleted.
    git -C "$wt" reset -q -N
    echo "worktree $wt at $(git -C "$wt" rev-parse --short HEAD)," \
        "scope: $(git -C "$wt" diff --shortstat)"
    ;;
remove)
    # Guards against swapped arguments or a wrong path: rm -rf below must only hit a review
    # worktree.
    case "$wt" in
        */review-[0-9]*) ;;
        *) echo "error: not a review worktree: $wt" >&2; exit 1 ;;
    esac
    [ ! -d "$wt/.git" ] || { echo "error: $wt is a main worktree" >&2; exit 1; }
    git -C "$repo" worktree remove --force "$wt" ||
        echo "note: git did not remove $wt; deleting the folder" >&2
    rm -rf "$wt" "$wt.index"
    git -C "$repo" worktree prune
    ;;
*)
    echo "error: unknown command $cmd" >&2
    exit 2
    ;;
esac
