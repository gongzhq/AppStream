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

from gi.repository import Gtk
from gettext import gettext as _

from softwarecenter.hw import TAG_DESCRIPTION


class HardwareRequirementsLabel(Gtk.HBox):
    """ contains a single HW requirement string and a image that shows if
        the requirements are meet
    """

    SUPPORTED_SYM = {
        # TRANSLATORS: symbol for "hardware-supported"
        'yes': _(u'\u2713'),
        # TRANSLATORS: symbol for hardware "not-supported"
        'no': u'<span foreground="red">%s</span>' % _(u'\u2718'),
    }

    # TRANSLATORS: this is a substring that used to build the
    #              "hardware-supported" string, where sym is
    #              either a unicode checkmark or a cross
    #              and hardware is the short hardware description
    #              Note that this is the last substr, no trailing ","
    LABEL_LAST_ITEM = _("%(sym)s%(hardware)s")

    # TRANSLATORS: this is a substring that used to build the
    #              "hardware-supported" string, where sym is
    #              either a unicode checkmark or a cross
    #              and hardware is the short hardware description
    #              Note that the trailing ","
    LABEL = _("%(sym)s%(hardware)s,")

    def __init__(self, last_item=True):
        super(HardwareRequirementsLabel, self).__init__()
        self.tag = None
        self.result = None
        self.last_item = last_item
        self._build_ui()

    def _build_ui(self):
        self._label = Gtk.Label()
        self._label.show()
        self.pack_start(self._label, True, True, 0)

    def get_label(self):
        # get the right symbol
        sym = self.SUPPORTED_SYM[self.result]
        # we add a trailing
        if self.last_item:
            s = self.LABEL_LAST_ITEM
        else:
            s = self.LABEL
        return _(s) % {
            "sym": sym,
            "hardware": _(TAG_DESCRIPTION[self.tag]),
            }

    def set_hardware_requirement(self, tag, result):
        self.tag = tag
        self.result = result
        self._label.set_markup(self.get_label())


class HardwareRequirementsBox(Gtk.HBox):
    """ A collection of HW requirement labels """

    def __init__(self):
        super(HardwareRequirementsBox, self).__init__()

    def clear(self):
        for w in self.get_children():
            self.remove(w)

    def set_hardware_requirements(self, hw_requirements_result):
        self.clear()
        for tag, supported in hw_requirements_result.iteritems():
            # ignore unknown for now
            if not supported in ("yes", "no"):
                continue
            label = HardwareRequirementsLabel(last_item=False)
            label.set_hardware_requirement(tag, supported)
            label.show()
            self.pack_start(label, True, True, 6)
        # tell the last item that its last
        if self.get_children():
            self.get_children()[-1].last_item = True

    @property
    def hw_labels(self):
        return self.get_children()


def get_test_window():
    win = Gtk.Window()
    win.set_size_request(300, 200)

    HW_TEST_RESULT = {
        'hardware::gps': 'yes',
        'hardware::video:opengl': 'no',
    }

    # add it
    hwbox = HardwareRequirementsBox()
    hwbox.set_hardware_requirements(HW_TEST_RESULT)
    win.add(hwbox)

    win.show_all()
    win.connect("destroy", Gtk.main_quit)
    return win

if __name__ == "__main__":
    win = get_test_window()
    Gtk.main()
