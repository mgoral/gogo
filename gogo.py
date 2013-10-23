#!/usr/bin/env python

"""
Copyright (C) 2013 Michal Goral

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
import gettext
import locale
from subprocess import call
import operator

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
  -a alias   : add current directory as alias to the configuration
  -l, --ls   : list aliases
  -e, --edit : open configuration file in $EDITOR
  -h, --help : show this message

See ~/.config/gogo/gogo.conf for configuration details."""
)

DEFAULT_CONFIG = [
    _("# This is an example 'gogo' config file") + '\n',
    _("# Each line starting with '#' character is considered a comment.") + '\n',
    _("# Each entry should be in the following format:") + '\n',
    _("# dir_alias = /dir/path/") + '\n',
    _("# Example:") + '\n',
    "default = %s\n" % os.path.expanduser("~"),
    "\n",
    _("# 'default' is a special alias which is used when no alias is given to gogo.") + '\n',
    _("# If you don't specify it in a configuration file, it'll point to your home dir.") + '\n',
    _("# Have fun!") + '\n\n',
    "- = -\n"
    "gogo = ~/.config/gogo\n",
]

def fatalError(msg):
    sys.stderr.write(msg + '\n')
    sys.exit(1)

def printDir(directory):
    sys.stdout.write(directory + '\n')
    sys.exit(0)

def printConfig(config):
    sys.stderr.write(_("Current gogo configuration (sorted alphabetically):\n"))
    if len(config) > 0:
        justification = len(max(config.keys(), key=len)) + 2

        # sort
        configList = [(key, config[key]) for key in config.keys()]
        configList.sort(key = operator.itemgetter(0))

        for key, val in configList:
            keyStr = "%s" % key.decode(locale.getpreferredencoding())
            valStr = " : %s\n" % val
            sys.stderr.write(keyStr.rjust(justification))
            sys.stderr.write(valStr)
    else:
        sys.stderr.write(_("  [ NO CONFIGURATION ] \n"))

    sys.exit(1)

def createNonExistingConfigDir(configDir):
    try:
        os.makedirs(configDir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(configDir):
            pass
        else: raise

def openConfigInEditor(configDir, configName):
    configPath = os.path.join(configDir, configName)
    try:
        editor = os.environ["EDITOR"]
    except KeyError:
        sys.stderr.write(_("No $EDITOR set. Trying vi.\n"))
        editor = "vi"
    call([editor, configPath])
    sys.exit(1)

def readConfig(configDir, configName):
    createNonExistingConfigDir(configDir)
    lines = None
    configPath = os.path.join(configDir, configName)
    try:
        with open(configPath, 'r') as file_:
            lines = file_.readlines()
    except IOError:
        lines = DEFAULT_CONFIG
        with open(configPath, 'w+') as file_:
            file_.writelines(lines)
    return lines

def preparePath(path):
    path = path.strip('" ')
    if path.startswith("~/"):
        path = path.replace("~", os.path.expanduser("~"))
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

def addAlias(alias, configDir, configName):
    currentDir = os.getcwd()

    configPath = os.path.join(configDir, configName)
    with open(configPath, "a") as file_:
        file_.write("%s = %s\n" % (alias, currentDir))

def main():
    configName = "gogo.conf"
    configDir = "%s/%s" % (os.path.expanduser("~"), "/.config/gogo")
    lines = readConfig(configDir, configName)

    argNo = len(sys.argv[1:])
    if 0 == argNo:
        config = parseConfig(lines)
        printDir(config.get("default", os.path.expanduser("~")))
    elif 1 == argNo:
        arg = sys.argv[1]
        if arg == "-h" or arg == "--help":
            fatalError(HELP_MSG)
        elif arg == "-l" or arg == "--ls":
            config = parseConfig(lines)
            printConfig(config)
        elif arg == "-e" or arg == "--edit":
            openConfigInEditor(configDir, configName)
        elif arg == "-a":
            fatalError(_("Alias to add not specified!"))
        else:
            config = parseConfig(lines)
            newdir = config.get(arg)
            if newdir is None:
                fatalError(_("'%s' not found in a configuration file!" % arg))
            printDir(newdir)
    elif 2 == argNo:
        arg = sys.argv[1]
        if arg == "-a":
            alias = sys.argv[2]
            addAlias(alias, configDir, configName)
            #sys.exit(1)
        else:
            fatalError(HELP_MSG)
    else:
        fatalError(HELP_MSG)

try:
    main()
except KeyboardInterrupt:
    raise SystemExit(0)
