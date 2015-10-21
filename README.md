GOGO
======

gogo is a great way to bookmark directories inside your shell. You don't have to remember long and
complicated paths anymore. Just type `gogo xmas` from anywhere and you're in
`~/Pictures/from_mum/1994/12/christmas`. You can even use it to connect to ssh servers the very same
way!

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

Usage
---------------
```
gogo                 : change directory to default or $HOME if default is not set
gogo alias           : change directory to 'alias'
gogo alias/child/dir : change directory to the child directory of your alias (i.e. 'alias'/child/dir)
gogo -a alias        : add current directory as alias to the configuration
gogo -h, gogo --help : display help message
gogo -l, gogo --ls   : list aliases
gogo -e, gogo --edit : edit configuration in $EDITOR
```

Note however that changing a directory to the child of alias will not work if your alias already
have slash in it. Sorry!

Remember that gogo prints all user-output to `stderr` so you won't be able to see it if
it's redirected on your system. Sorry, but it's the only way gogo can work.

Configuration
---------------
gogo stores configuration file in `~/.config/gogo/gogo.conf`. It's auto created if it doesn't exist.
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

gogo allows you to create aliases for connecting directly into directories on ssh servers:
```
sshalias = ssh://server_info:shell /desired/path
sshalias2 = ssh://another_server ~/second/path
```

`server_info` is provided in a typical ssh format, so it can be e.g. username@server or a host alias
stored in your `~/.ssh/config` file. After that comes an optional shell argument (separated by a
colon) into which you will be logged in. (Note however that if shell is not explicitly specified,
value of your ${SHELL} environment variable will be used.) Then, after a space, comes an actual
path.

If you ever wonder what commands gogo executes, you can alway call it directly:
```
~/bin/gogo.py
```
