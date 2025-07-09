Just place tmux.conf in ~/.config/tmux

tmux should auto load the config for new sessions

- For running sessions: press Ctrl+B and then ':'
  - input: 'source-file ~/.config/tmux/tmux.conf'
- From a shell
  - $ tmux source-file ~/.config/tmux/tmux.conf
