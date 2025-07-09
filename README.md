```
git clone https://github.com/frankjannis/linux_config.git ~/Documents/linux_config
cd ~/Documents/linux_config
stow -t ~/.config .
```

---
In case the folders already exist under ~/.config, run
```
stow --adopt -t ~/.config .
```
This will move changes inside this repo.

```
git restore .
```
will drop those differences.

---
Inverse:
```
stow -D -t ~/.config .
```
