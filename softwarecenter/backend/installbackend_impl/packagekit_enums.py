# Copyright (C) 2007-2008 Richard Hughes <richard@hughsie.com>
#               2011 Giovanni Campagna <scampa.giovanni@gmail.com>
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

# stolen from gnome-packagekit, which is GPL2+

from gi.repository import PackageKitGlib as packagekit

# this requires packagekit 0.7.2 or better
def status_enum_to_localised_text (status):
    return packagekit.info_enum_to_localised_present(status)

def role_enum_to_localised_present (role):
    return packagekit.role_enum_to_localised_present(role)
