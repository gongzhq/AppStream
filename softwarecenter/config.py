# Copyright (C) 20011 Canonical
#
# Authors:
#  Andrew Higginson
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

# py3 compat
try:
    from configparser import SafeConfigParser
    SafeConfigParser # pyflakes
except ImportError:
    from ConfigParser import SafeConfigParser
import os

from paths import SOFTWARE_CENTER_CONFIG_FILE

class SoftwareCenterConfig(SafeConfigParser):
    def __init__(self, config):
        SafeConfigParser.__init__(self)
        if not os.path.exists(os.path.dirname(config)):
            os.makedirs(os.path.dirname(config))
        self.configfile = config
        try:
            self.read(self.configfile)
        except:
            # don't crash on a corrupted config file
            pass
    def write(self):
        tmpname = self.configfile+".new"
        f=open(tmpname, "w")
        SafeConfigParser.write(self, f)
        f.close()
        os.rename(tmpname, self.configfile)
    
_software_center_config = None    
def get_config(filename=SOFTWARE_CENTER_CONFIG_FILE):
    """ get the global config class """
    global _software_center_config
    if not _software_center_config:
        _software_center_config = SoftwareCenterConfig(filename)
    return _software_center_config

