#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Author:     Andy Stewart <lazycat.manatee@gmail.com>
# Maintainer: Andy Stewart <lazycat.manatee@gmail.com>
# 
# Copyright (C) 2011 Andy Stewart, all rights reserved.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#from constant import *
from gi.repository import Gtk as gtk
from gi.repository import GdkPixbuf
import utils
import cairo

def buttonSetBackground(widget, scaleX, scaleY, normalImg, hoverImg, pressImg,
                        buttonLabel=None, fontSize=None, labelColor=None):
    '''Set event box's background.'''
    image = GdkPixbuf.Pixbuf.new_from_file(normalImg)

    if scaleX:
        requestWidth = -1
    else:
        requestWidth = image.get_width()

    if scaleY:
        requestHeight = -1
    else:
        requestHeight = image.get_height()

    widget.set_size_request(requestWidth, requestHeight)

    # Add button label if buttonLabel is not None.
    if buttonLabel != None:
        if labelColor == None:
            color = "#000000"
        else:
            color = labelColor

        if fontSize == None:
            size = "medium"
        else:
            size = int (fontSize * 1000)

        label = gtk.Label()
        label.set_markup("<span foreground='%s' size='%s'>%s</span>" % (color, size, buttonLabel))
        widget.add(label)

    widget.connect("draw", lambda w, e: buttonOnExpose(
            w, e,
            scaleX, scaleY,
            normalImg, hoverImg, pressImg))

def buttonOnExpose(widget, event,
                   scaleX, scaleY,
                   normalImg, hoverImg, pressImg):
    '''Expose function to replace event box's image.'''
    if widget.get_state() == gtk.StateType.NORMAL:
        image=cairo.ImageSurface.create_from_png(normalImg)
        #image = GdkPixbuf.Pixbuf.new_from_file(normalImg)
    elif widget.get_state() == gtk.StateType.PRELIGHT:
        image=cairo.ImageSurface.create_from_png(hoverImg)
        #image = GdkPixbuf.Pixbuf.new_from_file(hoverImg)
    elif widget.get_state() == gtk.StateType.ACTIVE:
        image=cairo.ImageSurface.create_from_png(pressImg)
        #image = GdkPixbuf.Pixbuf.new_from_file(pressImg)

    if scaleX:
        imageWidth = widget.allocation.width
    else:
        imageWidth = image.get_width()

    if scaleY:
        imageHeight = widget.get_allocation().height
    else:
        imageHeight = image.get_height()

    cr = widget.get_window().cairo_create()
    if image is not None:
	cr.set_source_surface(image, widget.get_allocation().x, widget.get_allocation().y)
	cr.paint()
    #pixbuf = image.scale_simple(imageWidth, imageHeight, GdkPixbuf.InterpType.BILINEAR)

    #cr = widget.get_window().cairo_create()
    #drawPixbuf(cr, pixbuf, widget.get_allocation().x, widget.get_allocation().y)

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def drawButton(widget, iconPrefix, subDir="cell", scaleX=False,
               buttonLabel=None, fontSize=None, labelColor=None):
    '''Draw button.'''
    buttonSetBackground(
        widget,
        scaleX, False,
        "/usr/share/icons/%s/%s_normal.png" % (subDir, iconPrefix),
        "/usr/share/icons/%s/%s_hover.png" % (subDir, iconPrefix),
        "/usr/share/icons/%s/%s_press.png" % (subDir, iconPrefix),
        buttonLabel, fontSize, labelColor
        )

def drawPixbuf(cr, pixbuf, x=0, y=0):
    '''Draw pixbuf.'''
    if pixbuf != None:
        cr.set_source_pixbuf(pixbuf, x, y)
        cr.paint()

def draw(cr, pixbuf, x=0, y=0):
    '''Draw pixbuf.'''
    if pixbuf != None:
        cr.set_source_pixbuf(pixbuf, x, y)
        cr.paint()

class Titlebar:
    '''Title bar.'''
	
    def __init__(self, minCallback, maxCallback, closeCallback):
        '''Init for title bar.'''
        self.box = gtk.VBox()
        
        self.controlBox = gtk.HBox()
        self.controlAlign = gtk.Alignment()
        self.controlAlign.set(1.0, 0.0, 0.0, 0.0)
        self.controlAlign.add(self.controlBox)
        self.box.add(self.controlAlign)
        
        self.minButton = gtk.Button()
        self.minButton.connect("button-release-event", lambda w, e: minCallback())
        drawButton(self.minButton, "min", "navigate")
        self.controlBox.pack_start(self.minButton, False, False,0)
        
        self.maxButton = gtk.Button()
        self.maxButton.connect("button-release-event", lambda w, e: maxCallback())
        drawButton(self.maxButton, "max", "navigate")
        self.controlBox.pack_start(self.maxButton, False, False,0)

        self.closeButton = gtk.Button()
        self.closeButton.connect("button-release-event", lambda w, e: closeCallback())
        drawButton(self.closeButton, "close", "navigate")
        self.controlBox.pack_start(self.closeButton, False, False,0)
        
        self.box.show_all()
