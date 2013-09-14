GOGO
======

gogo is a great way to bookmark directories inside your shell. You don't have to remember long and 
complicated paths anymore. Just type `gogo xmas` from anywhere and you're in 
`~/Pictures/from_mum/1994/12/christmas`.

Installation
--------------
gogo, like every script, is executed in a child shell so it's impossible to directly change the
directory of parent shell. That's why if you want to use gogo, you have to do a 2-step installation:

1. Copy `gogo.py` to any directory in your `$PATH`, e.g. ~/bin/:
   ```
   mkdir -p ~/bin && cp gogo.py ~/bin/
   ```

2. Add a function from `gogo.sh` e.g. to your `.bashrc` or `.zshrc`. You can also source it
   there.
   ```
   cat gogo.sh >> ~/.bashrc
   ```
   or:
   ```
   cat gogo.sh >> ~/.zshrc
   ```
   source version with `.bashrc`:
   ```
   cp gogo.sh ~/.gogo.sh && echo "source ~/.gogo.sh" >> ~/.bashrc
   ```

   You can simply use your favorite text editor to perform one of these operations. It's
   probably the safest to do it anyway.

Configuration
---------------
gogo stores configuration file in `~/.config/gogo.conf`. It's auto created if it doesn't exist.
The syntax is pretty simple:
```
# Comments are lines that start from '#' character.
default = ~/something
alias = /desired/path
alias2 = /desired/path with space
alias3 = "/this/also/works"
zażółć = "unicode/is/also/supported/zażółć gęślą jaźń"
```
`default` is a special alias - gogo will go there if it's executed with no arguments. It's always
available, even if it's not in a configuration file. In that case it will point to `$HOME` directory.

Please note that you cannot place a comment at the same line as the alias definition.

Other options
---------------
* list aliases: `gogo -l` or `gogo --ls`
* edit configuration file in `$EDITOR`: `gogo -e` or `gogo --edit`

Remember that gogo prints all user-output to `stderr` so you won't be able to see it if
it's redirected on your system. Sorry, but it's the only way gogo can work.
