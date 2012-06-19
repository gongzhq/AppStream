# Copyright (C) 2012 Canonical
#
# Authors:
#  Michael Vogt
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

from gettext import gettext as _

TAG_DESCRIPTION = {
    'hardware::webcam' : _('webcam'),
    'hardware::digicam' : _('digicam'),
    'hardware::input:mouse' : _('mouse'),
    'hardware::input:joystick' : _('joystick'),
    'hardware::input:touchscreen' : _('touchscreen'),
    'hardware::gps' : _('GPS'),
    'hardware::laptop' : _('notebook computer'),
    'hardware::printer': _('printer'),
    'hardware::scanner' : _('scanner'),
    'hardware::storage:cd' : _('CD drive'),
    'hardware::storage:cd-writer' : _('CD burner'),
    'hardware::storage:dvd' : _('DVD drive'),
    'hardware::storage:dvd-writer' : _('DVD burner'),
    'hardware::storage:floppy' : _('floppy disk drive'),
    'hardware::video:opengl' : _('OpenGL hardware acceleration'),

}

TAG_MISSING_DESCRIPTION = {
    'hardware::digicam' : _('This software requires a digital camera, but none '
                           'are currently connected'),
    'hardware::webcam' : _('This software requires a video camera, but none '
                           'are currently connected'),
    'hardware::input:mouse' : _('This software requires a mouse, '
                                'but none is currently setup.'),
    'hardware::input:joystick' : _('This software requires a joystick, '
                                   'but none are currently connected.'),
    'hardware::input:touchscreen' : _('This software requires a touchscreen, '
                                      'but the computer does not have one.'),
    'hardware::gps' : _('This software requires a GPS, '
                        'but the computer does not have one.'),
    'hardware::laptop' : _('This software is for notebook computers.'),
    'hardware::printer': _('This software requires a printer, but none '
                           'are currently set up.'),
    'hardware::scanner' : _('This software requires a scanner, but none are '
                            'currently set up.'),
    'hardware::stoarge:cd' : _('This software requires a CD drive, but none '
                               'are currently connected.'),
    'hardware::storage:cd-writer' : _('This software requires a CD burner, '
                                      'but none are currently connected.'),
    'hardware::storage:dvd' : _('This software requires a DVD drive, but none '
                                'are currently connected.'),
    'hardware::storage:dvd-writer' : _('This software requires a DVD burner, '
                                       'but none are currently connected.'),
    'hardware::storage:floppy' : _('This software requires a floppy disk '
                                   'drive, but none are currently connected.'),
    'hardware::video:opengl' : _('This computer does not have graphics fast '
                                 'enough for this software.'),
}

def get_hw_missing_long_description(tags):
    s = ""
    # build string
    for tag, supported in tags.iteritems():
        if supported == "no":
            s += "%s\n" % TAG_MISSING_DESCRIPTION.get(tag)
    # ensure that the last \n is gone
    if s:
        s = s[:-1]
    return s
