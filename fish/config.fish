# source /usr/share/cachyos-fish-config/cachyos-config.fish

# overwrite greeting
function fish_greeting
end

# set editor
set -gx EDITOR helix

## Useful aliases

# Replace ls with eza
alias ls='eza -l --color=always --group-directories-first --icons' # preferred listing
alias ll='eza -al --color=always --group-directories-first --icons'  # long format
alias lt='eza -T --color=always --group-directories-first --icons' # tree listing
alias lT='eza -aT --color=always --group-directories-first --icons' # tree listing
alias l.="eza -a | grep -e '^\.'"                                     # show only dotfiles

alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
alias ......='cd ../../../../..'

# Recent installed packages
alias rip="expac --timefmt='%Y-%m-%d %T' '%l\t%n %v' | sort | tail -200 | nl"
# Sort installed packages according to size in MB
alias big="expac -H M '%m\t%n' | sort -h | nl"
# Cleanup orphaned packages
alias cleanup='sudo pacman -Rns (pacman -Qtdq)'

## yazi wrapper
function y
    set tmp (mktemp -t "yazi-cwd.XXXXXX")
    yazi $argv --cwd-file="$tmp"
    if read -z cwd < "$tmp"; and [ -n "$cwd" ]; and [ "$cwd" != "$PWD" ]
        cd "$cwd"
    end
    rm -f -- "$tmp"
end

## zoxide init
zoxide init --cmd=cd fish | source
