#!/bin/sh
# Throwaway review worktrees for the review-round skill. No branch is created.
#
#   worktree.sh snapshot <repo>
#     Prints the tree of the current working state of <repo>: commits, uncommitted and untracked
#     changes, deletions. `git diff <tree> <tree>` then compares two states, new files included.
#   worktree.sh empty <repo> <scope start>
#     Exits 0 when the working state equals <scope start>, 1 when it does not.
#   worktree.sh prepare <repo> <worktree> <scope start>
#     Makes <worktree> a detached worktree at <scope start> whose files are that working state.
#     The scope is then exactly `git -C <worktree> diff`.
#   worktree.sh remove <repo> <worktree>
#     Removes a worktree that prepare made, and its folder. Refuses any other folder. When the
#     folder is already gone, it only unregisters the worktree.
# None of them touches the real index of <repo>.
set -eu

cmd=${1:?usage: worktree.sh snapshot|empty|prepare|remove <repo> [<worktree> [<scope start>]]}
repo=${2:?repo missing}

# Built in a copy of the index, not as a patch: a diff would pass through textconv and could drop
# binary files.
snapshot() {
    tmp=$(mktemp)
    cp "$(git -C "$repo" rev-parse --path-format=absolute --git-path index)" "$tmp"
    GIT_INDEX_FILE="$tmp" git -C "$repo" add -A
    GIT_INDEX_FILE="$tmp" git -C "$repo" write-tree
    rm -f "$tmp"
}

case "$cmd" in
snapshot)
    snapshot
    ;;
empty)
    start=${3:?scope start missing}
    git -C "$repo" diff --quiet "$start" "$(snapshot)"
    ;;
prepare)
    wt=${3:?worktree missing}
    start=${4:?scope start missing}
    if [ -e "$wt" ]; then
        echo "error: $wt already exists; run: worktree.sh remove $repo $wt" >&2
        exit 1
    fi
    tree=$(snapshot)
    git -C "$repo" worktree add -q --detach --no-checkout "$wt" "$start"
    touch "$(git -C "$wt" rev-parse --absolute-git-dir)/review-round"
    git -C "$wt" read-tree -u --reset "$tree"
    # Back to the scope start in the index only: the scope becomes unstaged, files the scope adds
    # stay visible as intent-to-add, deleted files show as deleted.
    git -C "$wt" reset -q -N
    echo "worktree $wt at $(git -C "$wt" rev-parse --short HEAD)," \
        "scope: $(git -C "$wt" diff --shortstat)"
    ;;
remove)
    wt=${3:?worktree missing}
    if [ -e "$wt" ]; then
        # --force deletes uncommitted work, so only a worktree marked by prepare goes.
        if [ ! -e "$(git -C "$wt" rev-parse --absolute-git-dir)/review-round" ]; then
            echo "error: $wt is not a review worktree" >&2
            exit 1
        fi
        git -C "$repo" worktree remove --force "$wt"
    fi
    git -C "$repo" worktree prune
    ;;
*)
    echo "error: unknown command $cmd" >&2
    exit 2
    ;;
esac
