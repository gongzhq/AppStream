#from gi.repository import Gtk

import cairo
import os

from softwarecenter.enums import ViewPages
from softwarecenter.paths import datadir
from mkit import floats_from_string


class SectionPainter(object):

    # specify background overlay image and color mappings for available and
    # installed view ids
    BACKGROUND_IMAGES = {
        ViewPages.AVAILABLE: cairo.ImageSurface.create_from_png(
            os.path.join(datadir, 'images/clouds.png')),
        ViewPages.INSTALLED: cairo.ImageSurface.create_from_png(
            os.path.join(datadir, 'images/arrows.png')),
                        }
    BACKGROUND_COLORS = {ViewPages.AVAILABLE: floats_from_string('#0769BC'),
                         ViewPages.INSTALLED: floats_from_string('#aea79f'),
                        }

    def __init__(self):
        self._view_id = None

    def set_view_id(self, id):
        self._view_id = id

    def draw(self, widget, cr):
        # sky
        #r,g,b = self.get_background_color()
        #lin = cairo.LinearGradient(0,a.y,0,a.y+150)
        #lin.add_color_stop_rgba(0, r,g,b, 0.3)
        #lin.add_color_stop_rgba(1, r,g,b,0)
        #cr.set_source(lin)
        #cr.rectangle(0,0,a.width, 150)
        #cr.fill()

        #s = self.get_background_image()
        #if widget.get_direction() != Gtk.TextDirection.RTL:
        #    cr.set_source_surface(s, a.x+a.width-s.get_width(), 0)
        #else:
        #    cr.set_source_surface(s, a.x, 0)

        #cr.paint()
        pass

    def get_background_color(self):
        return self.BACKGROUND_COLORS[self._view_id]

    def get_background_image(self):
        return self.BACKGROUND_IMAGES[self._view_id]
