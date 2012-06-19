# Copyright (C) 2009 Canonical
#
# Authors:
#  Michael Vogt
#  Andrew Higginson (rugby471)
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

from gi.repository import Gtk, Gdk, GObject, GdkPixbuf

from softwarecenter.ui.gtk3.drawing import rounded_rect


class ProgressImage(Gtk.Image):

    ANIMATION_PATH = ("/usr/share/icons/hicolor/24x24/status/"
        "softwarecenter-progress.png")
    FRAME_DELAY = 50  # msec

    BUBBLE_BORDER_RADIUS = 6
    BUBBLE_XPADDING = 4
    BUBBLE_YPADDING = 1

    _frame_cache = {}

    def __init__(self):
        Gtk.Image.__init__(self)
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(
                                                self.ANIMATION_PATH)

        # attrs specific to the pending animation image
        self.col_count = 6
        self.row_count = 3
        self.h_stride = self.pixbuf.get_width() / self.col_count
        self.v_stride = self.pixbuf.get_height() / self.row_count
        self.position = (0, 0)

        # transaction count num
        self.transaction_count = 0
        # the signal tag for the animation timeout
        self.handler = None
        # the first frame
        self.frame = self.get_idle_frame()

        # a Pango.Layout for rendering the transaction count
        layout = self.create_pango_layout("")
        self.connect("draw", self.on_draw, layout)

    # overrides
    def do_get_preferred_width(self):
        return self.h_stride, self.h_stride

    def do_get_preferred_height(self):
        return self.v_stride, self.v_stride

    # handlers
    def on_new_frame(self):
        i, j = self.position
        x = i * self.h_stride
        y = j * self.v_stride

        if (i, j) in self._frame_cache:
            self.frame = self._frame_cache[(i, j)]
        else:
            self.frame = GdkPixbuf.Pixbuf.new_subpixbuf(self.pixbuf,
                                                        x, y,
                                                        self.h_stride,
                                                        self.v_stride)
            self._frame_cache[(i, j)] = self.frame

        if i < self.col_count - 1:
            i += 1
        else:
            i = 0
            if j < self.row_count - 1:
                j += 1
            else:
                j = 0
        self.position = (i, j)

        self.queue_draw()
        return True

    # public
    def get_idle_frame(self):
        i, j = self.position
        x = i * self.h_stride
        y = j * self.v_stride

        self.frame = GdkPixbuf.Pixbuf.new_subpixbuf(self.pixbuf,
                                                    x, y,
                                                    self.h_stride,
                                                    self.v_stride)
        self._frame_cache[(i, j)] = self.frame
        return self.frame

    def set_transaction_count(self, transaction_count):
        self.transaction_count = transaction_count
        self.queue_draw()

    def on_draw(self, widget, cr, layout):
        a = widget.get_allocation()
        # paint the current animation frame
        x = (a.width - self.h_stride) * 0.5
        y = (a.height - self.v_stride) * 0.5
        Gdk.cairo_set_source_pixbuf(cr, self.frame, x, y)
        cr.paint()
        if self.transaction_count <= 0:
            return
        # paint a bubble with the transaction count
        layout.set_markup('<small>%i</small>' % self.transaction_count, -1)
        # determine bubble size
        extents = layout.get_pixel_extents()[1]
        width = extents.width + (2 * self.BUBBLE_XPADDING)
        height = extents.height + (2 * self.BUBBLE_YPADDING)
        # now render the bubble and layout
        context = self.get_style_context()
        x += self.h_stride + self.BUBBLE_XPADDING
        y += (self.v_stride - height) / 2
        rounded_rect(cr, x, y, width, height, self.BUBBLE_BORDER_RADIUS)
        cr.set_source_rgba(0, 0, 0, 0.2)
        cr.fill()
        Gtk.render_layout(context, cr,
                          x + self.BUBBLE_XPADDING,
                          y + self.BUBBLE_YPADDING,
                          layout)

    def is_playing(self):
        return self.handler is not None

    def start(self):
        if self.is_playing():
            return
        self.position = (0, 0)
        self.handler = GObject.timeout_add(self.FRAME_DELAY,
                                           self.on_new_frame)

    def stop(self):
        if self.handler:
            GObject.source_remove(self.handler)
            self.handler = None

        self.position = (0, 0)
        self.queue_draw()
