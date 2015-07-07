#!/usr/bin/env python

"""
Copyright (C) 2013-2014 Michal Goral

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

import sys
import os
import errno
import getpass
import gettext
import locale
import operator

__version__ = "1.3.0"

t = gettext.translation(
    domain='gogo',
    fallback=True)
gettext.install('gogo')
_ = t.ugettext

HELP_MSG = _(
"""gogo - bookmark your favorite directories

usage:
  gogo [OPTIONS]|[DIR_ALIAS]

options:
  -a alias      : add current directory as alias to the configuration
  -l, --ls      : list aliases
  -e, --edit    : open configuration file in $EDITOR
  -h, --help    : show this message
  -v, --version : print version number and exit

examples:
  gogo alias
  gogo alias/child/directory

See ~/.config/gogo/gogo.conf for configuration details."""
)

DEFAULT_CONFIG = [
    _("# This is an example 'gogo' config file") + '\n',
    _("# Each line starting with '#' character is considered a comment.") + '\n',
    _("# Each entry should be in the following format:") + '\n',
    _("# dir_alias = /dir/path/") + '\n',
    _("# Example:") + '\n',
    "\n",
    "default = %s\n" % os.path.expanduser("~"),
    "\n",
    _("# 'default' is a special alias which is used when no alias is given to gogo.") + '\n',
    _("# If you don't specify it in a configuration file, it'll point to your home dir.") + '\n',
    "\n",
    _("# You can also connect to directory on ssh server but syntax is slightly different:") + '\n',
    _("# dir_alias = ssh://server_name:chosen_shell /dir/path/") + '\n\n',
    _("# You can omit shell if you wish but in this case gogo will use ${SHELL} variable.") + '\n',
    _("# dir_alias = ssh://second_server /dir/path/") + '\n',
    "\n",
    "sshloc = ssh://%s@127.0.0.1:%s %s\n" %
        (getpass.getuser(), os.environ["SHELL"], os.path.expanduser("~")),
    "- = -\n"
    "gogo = ~/.config/gogo\n",
]

configName = "gogo.conf"
configDir = "%s/%s" % (os.path.expanduser("~"), "/.config/gogo")
configPath = os.path.join(configDir, configName)

def echo(text, output=sys.stdout, endline=True):
    if output == sys.stdout:
        if endline is True:
            output.write("echo '%s';" %  text)
        else:
            output.write("echo -n '%s';" %  text)
    else:
        output.write("%s" % text)
        if endline is True:
            output.write("\n")

def call(cmd):
    sys.stdout.write("%s;\n" % cmd)
    sys.exit(0)

def printVersion():
    echo("gogo %s" % __version__)
    sys.exit(0)

def fatalError(msg, status=1):
    echo(msg, sys.stderr)
    sys.exit(status)

def _changeDirectory(directory):
    if directory.startswith("~/"):
        directory = directory.replace("~", os.path.expanduser("~"))
    call("cd '%s'" % directory)

def _sshToAddress(address):
    addressPart, directory = address.split(" ", 1)
    splitted = addressPart.split(":")
    server = splitted[0]
    shell = splitted[1] if len(splitted) > 1 else "${SHELL}"

    call("ssh %s -t 'cd %s; %s'" % (server, directory, shell))

def processRequest(request):
    if request.startswith("ssh://"):
        address = request.replace("ssh://", "", 1)
        _sshToAddress(address)
    else:
        _changeDirectory(request)

def printConfig(config):
    echo(_("Current gogo configuration (sorted alphabetically):"))
    if len(config) > 0:
        justification = len(max(config.keys(), key=len)) + 2

        # sort
        configList = [(key, config[key]) for key in config.keys()]
        configList.sort(key = operator.itemgetter(0))

        for key, val in configList:
            keyStr = "%s" % key.decode(locale.getpreferredencoding())
            valStr = " : %s" % val
            echo(keyStr.rjust(justification), endline=False)
            echo(valStr)
    else:
        echo(_("  [ NO CONFIGURATION ] "), sys.stderr)

def createNonExistingConfigDir():
    try:
        os.makedirs(configDir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(configDir):
            pass
        else: raise

def openConfigInEditor():
    try:
        editor = os.environ["EDITOR"]
    except KeyError:
        echo(_("No $EDITOR set. Trying vi."), sys.stderr)
        editor = "vi"
    call("%s %s" % (editor, configPath))
    sys.exit(1)

def readConfig():
    createNonExistingConfigDir()
    lines = None
    try:
        with open(configPath, 'r') as file_:
            lines = file_.readlines()
    except IOError:
        lines = DEFAULT_CONFIG
        with open(configPath, 'w+') as file_:
            file_.writelines(lines)
    return lines

def preparePath(path):
    path = path.strip('"\' ')
    return path

def prepareAlias(alias):
    alias = alias.strip()
    return alias

def parseConfig(lines):
    configDict = {}
    for lineNo, line in enumerate(lines):
        line = line.strip()
        if not line.startswith('#') and line != "":
            split = line.strip().split('=', 1)
            try:
                key = prepareAlias(split[0])
                val = preparePath(split[1])
            except IndexError:
                fatalError(_("Error at parsing a config file..\n  at line %s:\n  %s" % (lineNo, line) ))
            configDict[key] = val
    return configDict

def addAlias(alias, currentConfig):
    if currentConfig.get(alias) is None:
        currentDir = os.getcwd()

        with open(configPath, "a") as file_:
            file_.write("%s = %s\n" % (alias, currentDir))
    else:
        fatalError(_("Alias '%s' already exists!") % alias)

def parseAlias(alias, config):
    """Parse alias inputted by a user. Returns a tuple: ('dir', 'remainder_path').
    It's because of a feature that user can input something like "alias/child/directory" and gogo
    should change directory into "dir/child/directory"."""

    # If user chooses an alias with a slash in it, so be it.
    newdir = config.get(alias)
    if newdir is not None:
        return (newdir, "")

    splitted = alias.split("/", 1)
    newdir = config.get(splitted[0])
    if newdir is None:
        fatalError(_("'%s' not found in a configuration file!" % alias))

    if len(splitted) == 1:
        return (newdir, "")
    else:
        return (newdir, splitted[1])

def main():
    lines = readConfig()

    argNo = len(sys.argv[1:])
    if 0 == argNo:
        config = parseConfig(lines)
        processRequest(config.get("default", os.path.expanduser("~")))
    elif 1 == argNo:
        arg = sys.argv[1]
        if arg == "-h" or arg == "--help":
            echo(HELP_MSG)
        elif arg == "-v" or arg == "--version":
            printVersion()
        elif arg == "-l" or arg == "--ls":
            config = parseConfig(lines)
            printConfig(config)
        elif arg == "-e" or arg == "--edit":
            openConfigInEditor()
        elif arg == "-a":
            fatalError(_("Alias to add not specified!"))
        else:
            config = parseConfig(lines)
            newdir, remainder = parseAlias(arg, config)
            if len(remainder) > 0: # fix for e.g. 'gogo -' which would result in '-/'
                processRequest(os.path.join(newdir, remainder))
            else:
                processRequest(newdir)
    elif 2 == argNo:
        arg = sys.argv[1]
        if arg == "-a":
            alias = sys.argv[2]
            config = parseConfig(lines)
            addAlias(alias, config)
        else:
            fatalError(HELP_MSG, 2)
    else:
        fatalError(HELP_MSG, 3)

try:
    main()
except KeyboardInterrupt:
    sys.exit(2)
