from gi.repository import Atk
from gi.repository import Gtk, Gdk
from gi.repository import GObject
from gi.repository import Pango

from softwarecenter.ui.gtk3.em import em

from gettext import gettext as _

import logging
LOG = logging.getLogger("softwarecenter.view.widgets.NavigationBar")

# pi constants
from math import pi

PI = pi
PI_OVER_180 = pi / 180


class Shape:

    """ Base class for a Shape implementation.

        Currently implements a single method <layout> which is called
        to layout the shape using cairo paths.  It can also store the
        'direction' of the shape which should be on of the Gtk.TEXT_DIR
        constants.  Default 'direction' is Gtk.TextDirection.LTR.

        When implementing a Shape, there are two options available.

        If the Shape is direction dependent, the Shape MUST
        implement <_layout_ltr> and <_layout_rtl> methods.

        If the Shape is not direction dependent, then it simply can
        override the <layout> method.

        <layout> methods must take the following as arguments:

        cr :    a CairoContext
        x  :    x coordinate
        y  :    y coordinate
        w  :    width value
        h  :    height value

        <layout> methods can then be passed Shape specific
        keyword arguments which can be used as paint-time modifiers.
    """

    def __init__(self, direction):
        self.direction = direction
        self.name = 'Shapeless'
        self.hadjustment = 0
        self._color = 1, 0, 0

    def __eq__(self, other):
        return self.name == other.name

    def layout(self, cr, x, y, w, h, r, aw):
        if self.direction != Gtk.TextDirection.RTL:
            self._layout_ltr(cr, x, y, w, h, r, aw)
        else:
            self._layout_rtl(cr, x, y, w, h, r, aw)


class ShapeRoundedRect(Shape):

    """
        RoundedRect lays out a rectangle with all four corners
        rounded as specified at the layout call by the keyword argument:

        radius :    an integer or float specifying the corner radius.
                    The radius must be > 0.

        RoundedRectangle is not direction sensitive.
    """

    def __init__(self, direction=Gtk.TextDirection.LTR):
        Shape.__init__(self, direction)
        self.name = 'RoundedRect'

    def layout(self, cr, x, y, w, h, r, aw):
        cr.new_sub_path()
        cr.arc(r + x, r + y, r, PI, 270 * PI_OVER_180)
        cr.arc(x + w - r, r + y, r, 270 * PI_OVER_180, 0)
        cr.arc(x + w - r, y + h - r, r, 0, 90 * PI_OVER_180)
        cr.arc(r + x, y + h - r, r, 90 * PI_OVER_180, PI)
        cr.close_path()


class ShapeStartArrow(Shape):

    def __init__(self, direction=Gtk.TextDirection.LTR):
        Shape.__init__(self, direction)
        self.name = 'StartArrow'

    def _layout_ltr(self, cr, x, y, w, h, r, aw):
        haw = aw / 2

        cr.new_sub_path()
        cr.arc(r + x, r + y, r, PI, 270 * PI_OVER_180)

        # arrow head
        cr.line_to(x + w - haw, y)
        cr.line_to(x + w + haw, y + (h / 2))
        cr.line_to(x + w - haw, y + h)

        cr.arc(r + x, y + h - r, r, 90 * PI_OVER_180, PI)
        cr.close_path()

    def _layout_rtl(self, cr, x, y, w, h, r, aw):
        haw = aw / 2

        cr.new_sub_path()
        cr.move_to(x - haw, (y + h) / 2)
        cr.line_to(x + aw - haw, y)
        cr.arc(x + w - r, r + y, r, 270 * PI_OVER_180, 0)
        cr.arc(x + w - r, y + h - r, r, 0, 90 * PI_OVER_180)
        cr.line_to(x + aw - haw, y + h)
        cr.close_path()


class ShapeMidArrow(Shape):

    def __init__(self, direction=Gtk.TextDirection.LTR):
        Shape.__init__(self, direction)
        #~ self.draw_xoffset = -2
        self._color = 0, 1, 0
        self.name = 'MidArrow'

    def _layout_ltr(self, cr, x, y, w, h, r, aw):
        self.hadjustment = haw = aw / 2
        cr.move_to(x - haw - 1, y)
        # arrow head
        cr.line_to(x + w - haw, y)
        cr.line_to(x + w + haw, y + (h / 2))
        cr.line_to(x + w - haw, y + h)
        cr.line_to(x - haw - 1, y + h)

        cr.line_to(x + haw - 1, y + (h / 2))

        cr.close_path()

    def _layout_rtl(self, cr, x, y, w, h, r, aw):
        self.hadjustment = haw = -aw / 2

        cr.move_to(x + haw, (h + y) / 2)
        cr.line_to(x + aw + haw, y)
        cr.line_to(x + w - haw + 1, y)
        cr.line_to(x + w - aw - haw + 1, (y + h) / 2)
        cr.line_to(x + w - haw + 1, y + h)
        cr.line_to(x + aw + haw, y + h)
        cr.close_path()


class ShapeEndCap(Shape):

    def __init__(self, direction=Gtk.TextDirection.LTR):
        Shape.__init__(self, direction)
        #~ self.draw_xoffset = -2
        self._color = 0, 0, 1
        self.name = 'EndCap'

    def _layout_ltr(self, cr, x, y, w, h, r, aw):
        self.hadjustment = haw = aw / 2

        cr.move_to(x - haw - 1, y)
        # rounded end
        cr.arc(x + w - r, r + y, r, 270 * PI_OVER_180, 0)
        cr.arc(x + w - r, y + h - r, r, 0, 90 * PI_OVER_180)
        # arrow
        cr.line_to(x - haw - 1, y + h)
        cr.line_to(x + haw - 1, y + (h / 2))
        cr.close_path()

    def _layout_rtl(self, cr, x, y, w, h, r, aw):
        self.hadjustment = haw = -aw / 2

        cr.arc(r + x, r + y, r, PI, 270 * PI_OVER_180)
        cr.line_to(x + w - haw + 1, y)
        cr.line_to(x + w - haw - aw + 1, (y + h) / 2)
        cr.line_to(x + w - haw + 1, y + h)
        cr.arc(r + x, y + h - r, r, 90 * PI_OVER_180, PI)
        cr.close_path()


class AnimationClock(GObject.GObject):
    _1SECOND = 1000
    __gsignals__ = {
        "animation-frame": (GObject.SignalFlags.RUN_LAST,
                                None,
                                (float,),),

        "animation-finished": (GObject.SignalFlags.RUN_FIRST,
                                None,
                                (bool,),),
                    }

    def __init__(self, fps, duration):
        GObject.GObject.__init__(self)

        self.fps = fps
        self.in_progress = False
        self.set_duration(duration)

        self._clock = None
        self._progress = 0  # progress as an msec offset

    def _get_timstep(self):
        d = self.duration
        return max(10, int(d / ((d / AnimationClock._1SECOND) * self.fps)))

    def _schedule_animation_frame(self):
        if self._progress > self.duration:
            self._clock = None
            self.in_progress = False
            self.emit('animation-finished', False)
            return False

        self._progress += self._timestep
        self.emit('animation-frame', self.progress)
        return True

    @property
    def progress(self):
        return min(1.0, self._progress / self.duration)

    def set_duration(self, duration):
        self.duration = float(duration)
        self._timestep = self._get_timstep()

    def stop(self, who_called='?'):

        if self._clock:
            #~ print who_called+'.Stop'
            GObject.source_remove(self._clock)
            self.emit('animation-finished', True)

        self._clock = None
        self._progress = 0
        self.in_progress = False

    def start(self):
        self.stop(who_called='start')
        if not self.sequence:
            return

        self._clock = GObject.timeout_add(self._timestep,
                                          self._schedule_animation_frame,
                                          priority=100)
        self.in_progress = True


class PathBarAnimator(AnimationClock):
    # animation display constants
    FPS = 50
    DURATION = 150  # spec says 150ms

    # animation modes
    NONE = 'animation-none'
    OUT = 'animation-out'
    IN = 'animation-in'
    WIDTH_CHANGE = 'animation-width-change'

    def __init__(self, pathbar):
        AnimationClock.__init__(self, self.FPS, self.DURATION)

        self.pathbar = pathbar
        self.sequence = []

        self.connect('animation-frame', self._on_animation_frame)
        self.connect('animation-finished', self._on_animation_finished)

    def _animate_out(self, part, progress, kwargs):
        real_alloc = part.get_allocation()
        xo = real_alloc.width - int(real_alloc.width * progress)

        if self.pathbar.get_direction() == Gtk.TextDirection.RTL:
            xo *= -1

        anim_alloc = Gdk.Rectangle()
        anim_alloc.x = real_alloc.x - xo
        anim_alloc.y = real_alloc.y
        anim_alloc.width = real_alloc.width
        anim_alloc.height = real_alloc.height

        part.new_frame(anim_alloc)

    def _animate_in(self, part, progress, kwargs):
        real_alloc = part.get_allocation()
        xo = int(real_alloc.width * progress)

        if self.pathbar.get_direction() == Gtk.TextDirection.RTL:
            xo *= -1

        anim_alloc = Gdk.Rectangle()
        anim_alloc.x = real_alloc.x - xo
        anim_alloc.y = real_alloc.y
        anim_alloc.width = real_alloc.width
        anim_alloc.height = real_alloc.height

        part.new_frame(anim_alloc)

    def _animate_width_change(self, part, progress, kwargs):
        start_w = kwargs['start_width']
        end_w = kwargs['end_width']

        width = int(round(start_w + (end_w - start_w) * progress))
        part.set_size_request(width, part.get_height_request())

    def _on_animation_frame(self, clock, progress):
        if not self.sequence:
            return

        for actor, animation, kwargs in self.sequence:
            if animation == PathBarAnimator.NONE:
                continue

            if animation == PathBarAnimator.OUT:
                self._animate_out(actor, progress, kwargs)

            elif animation == PathBarAnimator.IN:
                self._animate_in(actor, progress, kwargs)

            elif animation == PathBarAnimator.WIDTH_CHANGE:
                self._animate_width_change(actor, progress, kwargs)

    def _on_animation_finished(self, clock, interrupted):
        for actor, animation, kwargs in self.sequence:
            actor.animation_finished()

        self.sequence = []
        self.pathbar.psuedo_parts = []
        self.pathbar.queue_draw()

    def append_animation(self, actor, animation, **kwargs):
        self.sequence.append((actor, animation, kwargs))

    def reset(self, who_called='?'):
        AnimationClock.stop(self, who_called=who_called + '.reset')
        self.sequence = []


class PathBar(Gtk.HBox):

    MIN_PART_WIDTH = 25  # pixels

    def __init__(self):
        GObject.GObject.__init__(self)
        self.set_redraw_on_allocate(False)
        self.set_size_request(-1, em(1.75))
        self._allocation = None

        # Accessibility info
        atk_desc = self.get_accessible()
        atk_desc.set_name(_("You are here:"))
        atk_desc.set_role(Atk.Role.PANEL)

        self.use_animations = True
        self.animator = PathBarAnimator(self)

        self.out_of_width = False
        self.psuedo_parts = []

        # used for certain button press logic
        self._press_origin = None
        # tracks the id of the revealer timeout
        self._revealer = None

        # values derived from the gtk settings
        s = Gtk.Settings.get_default()
        # time to wait before revealing a part on enter event in ms
        self._timeout_reveal = s.get_property("gtk-tooltip-timeout")
        # time to wait until emitting click event in ms
        self._timeout_initial = s.get_property("gtk-timeout-initial")

        # les signales!
        self.connect('size-allocate', self._on_allocate)
        self.connect('draw', self._on_draw)

    # sugar
    def __len__(self):
        return len(self.get_children())

    def __getitem__(self, index):
        return self.get_children()[index]

    # signal handlers
    def _on_allocate(self, widget, _):
        allocation = self.get_allocation()

        if self._allocation == allocation:
            return True

        # prevent vertical bobby when the searchentry is shown/hidden
        if allocation.height > self.get_property('height-request'):
            self.set_property('height-request', allocation.height)

        if not self._allocation:
            self._allocation = allocation
            self.queue_draw()
            return True

        pthbr_width = allocation.width
        parts_width = self.get_parts_width()

        #~ print parts_width, pthbr_width

        #~ self.animator.reset('on_allocate')
        self.set_use_animations(True)

        if pthbr_width > parts_width and self.out_of_width:
            dw = pthbr_width - parts_width
            self._grow_parts(dw)

        elif pthbr_width < parts_width:
            overhang = parts_width - pthbr_width
            if overhang > 0:
                self.set_use_animations(False)
                self._shrink_parts(overhang)

        self._allocation = allocation
        if self.use_animations and self.animator.sequence and not \
            self.animator.in_progress:
            self.animator.start()
        else:
            self.queue_draw()

    def _on_draw(self, widget, cr):
        # always paint psuedo parts first
        a = self.get_allocation()
        context = self.get_style_context()
        context.save()
        context.add_class("button")

        self._paint_psuedo_parts(cr, context, a.x, a.y)

        # paint a frame around the entire pathbar
        width = self.get_parts_width()
        Gtk.render_background(context, cr, 1, 1, width - 2, a.height - 2)

        self._paint_widget_parts(cr, context, a.x, a.y)

        Gtk.render_frame(context, cr, 0, 0, width, a.height)
        context.restore()
        return True

    # private methods
    def _paint_widget_parts(self, cr, context, xo, yo):
        parts = self.get_children()
        # paint in reverse order, so we get correct overlapping during
        # animation
        parts.reverse()
        for part in parts:
            part.paint(cr,
                       part.animation_allocation or part.get_allocation(),
                       context,
                       xo, yo)

    def _paint_psuedo_parts(self, cr, context, xo, yo):
        # a special case: paint psuedo parts paint first,
        # i.e those parts animating 'in' on their removal
        for part in self.psuedo_parts:
            part.paint(cr,
                       part.animation_allocation or part.get_allocation(),
                       context,
                       xo, yo)

    def _shrink_parts(self, overhang):
        self.out_of_width = True

        for part in self:
            old_width = part.get_width_request()
            new_width = max(self.MIN_PART_WIDTH, old_width - overhang)

            if False:  # self.use_animations:
                self.animator.append_animation(part,
                                               PathBarAnimator.WIDTH_CHANGE,
                                               start_width=old_width,
                                               end_width=new_width)
            else:
                part.set_size_request(new_width,
                                      part.get_height_request())

            overhang -= old_width - new_width
            if overhang <= 0:
                break

    def _grow_parts(self, claim):
        children = self.get_children()
        children.reverse()

        for part in children:

            if part.get_allocation().width == part.get_natural_width():
                continue

            growth = min(claim, (part.get_natural_width() - part.width))
            if growth <= 0:
                break

            claim -= growth

            if self.use_animations:
                self.animator.append_animation(part,
                                               PathBarAnimator.WIDTH_CHANGE,
                                               start_width=part.width,
                                               end_width=part.width + growth)
            else:
                part.set_size_request(part.width + growth,
                                      part.get_height_request())

    def _make_space(self, part):
        children = self.get_children()
        if not children:
            return

        cur_width = self.get_parts_width()
        incomming_width = cur_width + part.get_width_request()
        overhang = incomming_width - self.get_allocation().width

        if overhang > 0:
            print 'shrink parts by:', overhang
            self._shrink_parts(overhang)

    def _reclaim_space(self, part):
        if not self.out_of_width:
            return

        claim = part.get_width_request()
        self._grow_parts(claim)

    def _append_compose_parts(self, new_part):
        d = self.get_direction()
        children = self.get_children()
        n_parts = len(children)

        if n_parts > 0:
            new_part.set_shape(ShapeEndCap(d))
            first_part = children[0]
            first_part.set_shape(ShapeStartArrow(d))
        else:
            new_part.set_shape(ShapeRoundedRect(d))

        if not n_parts > 1:
            return

        new_mid = children[-1]
        new_mid.set_shape(ShapeMidArrow(d))

    def _remove_compose_parts(self):
        d = self.get_direction()
        children = self.get_children()
        n_parts = len(children)

        if n_parts == 0:
            return

        elif n_parts == 1:
            children[0].set_shape(ShapeRoundedRect(d))
            return

        last = children[-1]
        last.set_shape(ShapeEndCap(d))
        self.queue_draw()

    def _cleanup_revealer(self):
        if not self._revealer:
            return
        GObject.source_remove(self._revealer)
        self._revealer = None

    def _theme(self, part):
        #~ part.set_padding(self.theme['xpad'], self.theme['ypad'])
        part.set_padding(12, 4)

    # public methods
    @property
    def first_part(self):
        children = self.get_children()
        if children:
            return children[0]

    @property
    def last_part(self):
        children = self.get_children()
        if children:
            return children[-1]

    def reveal_part(self, part, animate=True):
        # do not do here:
        #~ self.animator.reset(who_called='reveal_animation')
        self.set_use_animations(animate)

        part_old_width = part.get_width_request()
        part_new_width = part.get_natural_width()

        if part_new_width == part_old_width:
            return

        change_amount = part_new_width - part_old_width

        for p in self.get_children():

            if p == part:
                old_width = part_old_width
                new_width = part_new_width
            else:
                if change_amount <= 0:
                    continue

                old_width = p.get_width_request()
                new_width = max(self.MIN_PART_WIDTH, old_width - change_amount)
                change_amount -= old_width - new_width

            if self.use_animations:
                self.animator.append_animation(p,
                                               PathBarAnimator.WIDTH_CHANGE,
                                               start_width=old_width,
                                               end_width=new_width)
            else:
                p.set_size_request(new_width,
                                   p.get_height_request())

        self.animator.start()

    def queue_reveal_part(self, part):

        def reveal_part_cb(part):
            self.reveal_part(part)
            return

        self._cleanup_revealer()
        self._revealer = GObject.timeout_add(self._timeout_reveal,
                                             reveal_part_cb,
                                             part)

    def get_parts_width(self):
        last = self.last_part
        if not last:
            return 0

        if self.get_direction() != Gtk.TextDirection.RTL:
            return last.x + last.width - self.first_part.x

        first = self.first_part
        return first.x + first.width - last.x

    def get_visual_width(self):
        last = self.last_part
        first = self.first_part
        if not last:
            return 0

        la = last.animation_allocation or last.get_allocation()
        fa = first.animation_allocation or first.get_allocation()

        if self.get_direction() != Gtk.TextDirection.RTL:
            return la.x + la.width - fa.x

        return fa.x + fa.width - la.x

    def set_use_animations(self, use_animations):
        self.use_animations = use_animations
        if not use_animations and self.animator.in_progress:
            self.animator.reset()

    def append(self, part):
        print 'append', part
        print
        part.set_nopaint(True)
        self.animator.reset('append')

        self._theme(part)
        self._append_compose_parts(part)
        self._make_space(part)

        self.pack_start(part, False, False, 0)
        part.show()

        if self.use_animations:
            # XXX: please note that animations also get queued up
            #      within _shrink_parts()
            self.animator.append_animation(part, PathBarAnimator.OUT)
            #~ print self.animator.sequence
            self.animator.start()
        else:
            part.set_nopaint(False)
            part.queue_draw()

    def pop(self):
        children = self.get_children()
        if not children:
            return

        self.animator.reset('pop')

        last = children[-1]
        if self.use_animations:
            # because we remove the real part immediately we need to
            # replicate just enough attributes to preform the slide in
            # animation
            part = PsuedoPathPart(self, last)
            self.psuedo_parts.append(part)

        self.remove(last)

        self._remove_compose_parts()
        self._reclaim_space(last)

        last.destroy()

        if not self.use_animations:
            return

        self.animator.append_animation(part, PathBarAnimator.IN)
        self.animator.start()

    def navigate_up(self):
        """ just another name for pop() """
        self.pop()


class PathPartCommon:

    def __init__(self):
        self.animation_in_progress = False
        self.animation_allocation = None

    @property
    def x(self):
        return self.get_allocation().x

    @property
    def y(self):
        return self.get_allocation().y

    @property
    def width(self):
        return self.get_allocation().width

    @property
    def height(self):
        return self.get_allocation().height

    def new_frame(self, allocation):
        if self.is_nopaint:
            self.is_nopaint = False
        if not self.animation_in_progress:
            self.animation_in_progress = True

        self.animation_allocation = allocation
        self.queue_draw()

    def animation_finished(self):
        self.animation_in_progress = False
        self.animation_allocation = None
        if self.get_parent():
            self.get_parent().queue_draw()

    def paint(self, cr, a, context, xo, yo):
        if self.is_nopaint:
            return

        cr.save()

        x, y = 0, 0
        w, h = a.width, a.height
        arrow_width = 12  # theme['arrow-width']

        if isinstance(self, PathPart):
            _a = self.get_allocation()
            self.shape.layout(cr,
                              _a.x - xo + 1, _a.y - yo,
                              w, h, 3, arrow_width)
            cr.clip()
        else:
            Gtk.render_background(context, cr,
                                  a.x - xo - 10, a.y - yo,
                                  a.width + 10, a.height)

        cr.translate(a.x - xo, a.y - yo)

        if self.shape.name.find('Arrow') != -1:
            # draw arrow head
            cr.move_to(w - arrow_width / 2, 2)
            cr.line_to(w + 5, h / 2)
            cr.line_to(w - arrow_width / 2, h - 2)
            # fetch the line color and stroke
            rgba = context.get_border_color(Gtk.StateFlags.NORMAL)
            cr.set_source_rgb(rgba.red, rgba.green, rgba.blue)
            cr.set_line_width(1)
            cr.stroke()

        # render the layout
        e = self.layout.get_pixel_extents()[1]
        lw, lh = e.width, e.height
        pw, ph = a.width, a.height

        x = min(self.xpadding, (pw - lw) / 2)
        y = (ph - lh) / 2

        # layout area
        Gtk.render_layout(context,
                          cr,
                          int(x),
                          int(y),
                          self.layout)

        # paint the focus frame if need be
        if isinstance(self, PathPart) and self.has_focus():
            # layout area
            x, w, h = x - 2, lw + 4, lh + 1
            Gtk.render_focus(context, cr, x, y, w, h)

        cr.restore()


class PsuedoPathPart(PathPartCommon):

    def __init__(self, pathbar, real_part):
        PathPartCommon.__init__(self)
        self.parent = pathbar
        self.style = pathbar.get_style()
        self.state = real_part.get_state()
        self.allocation = real_part.get_allocation()
        self.size_request = real_part.get_size_request()
        self.xpadding = real_part.xpadding
        self.ypadding = real_part.ypadding

        # PsuedoPathParts are only used during the remove animation
        # sequence, so the shape is always a ShapeEndCap
        self.shape = ShapeEndCap(pathbar.get_direction())

        self.label = real_part.label
        self.layout = real_part.create_pango_layout(self.label)

        self.is_nopaint = False

    def get_allocation(self):
        return self.allocation

    def get_state(self):
        return self.state

    def get_width_request(self):
        return self.size_request[0]

    def get_height_request(self):
        return self.size_request[1]

    def animation_finished(self):
        pass

    def queue_draw(self):
        a = self.allocation
        aw = 12
        self.parent.queue_draw_area(a.x - aw / 2, a.y,
                                    a.width + aw, a.height)


class PathPart(Gtk.EventBox, PathPartCommon):

    __gsignals__ = {
        "clicked": (GObject.SignalFlags.RUN_LAST,
                     None,
                     (),),
        }

    def __init__(self, label):
        Gtk.EventBox.__init__(self)
        PathPartCommon.__init__(self)
        self.set_visible_window(False)

        self.atk = self.get_accessible()
        self.atk.set_role(Atk.Role.PUSH_BUTTON)

        self.layout = self.create_pango_layout(label)
        self.layout.set_ellipsize(Pango.EllipsizeMode.END)

        self.xpadding = 6
        self.ypadding = 3

        self.shape = ShapeRoundedRect(self.get_direction())
        self.is_nopaint = False

        self.set_label(label)
        self._init_event_handling()

    def __repr__(self):
        return "PathPart: '%s'" % self.label

    def __str__(self):
        return "PathPart: '%s'" % self.label

    # signal handlers
    def _on_enter_notify(self, part, event):
        self.pathbar.queue_reveal_part(self)
        if self.pathbar._press_origin == part:
            part.set_state(Gtk.StateFlags.ACTIVE)
        else:
            part.set_state(Gtk.StateFlags.PRELIGHT)
        self.queue_draw()

    def _on_leave_notify(self, part, event):
        self.pathbar.queue_reveal_part(self.pathbar.last_part)
        part.set_state(Gtk.StateFlags.NORMAL)
        self.queue_draw()

    def _on_button_press(self, part, event):
        if event.button != 1:
            return
        self.pathbar._press_origin = part
        part.set_state(Gtk.StateFlags.ACTIVE)
        self.queue_draw()

    def _on_button_release(self, part, event):
        if event.button != 1:
            return

        if self.pathbar._press_origin != part:
            self.pathbar._press_origin = None
            return

        self.pathbar._press_origin = None

        state = part.get_state()
        if state == Gtk.StateFlags.ACTIVE:
            part.set_state(Gtk.StateFlags.PRELIGHT)
            GObject.timeout_add(self.pathbar._timeout_initial,
                                self.emit, 'clicked')

        self.queue_draw()

    def _on_key_press(self, part, event):
        if event.keyval in (Gdk.KEY_space, Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            part.set_state(Gtk.StateFlags.ACTIVE)
        self.queue_draw()

    def _on_key_release(self, part, event):
        if event.keyval in (Gdk.KEY_space, Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            part.set_state(Gtk.StateFlags.NORMAL)
            GObject.timeout_add(self.pathbar._timeout_initial,
                                self.emit, 'clicked')
        self.queue_draw()

    def _on_focus_in(self, part, event):
        self.pathbar.reveal_part(self)

    def _on_focus_out(self, part, event):
        self.queue_draw()

    # private methods
    def _init_event_handling(self):
        self.set_property("can-focus", True)
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.KEY_RELEASE_MASK |
                        Gdk.EventMask.KEY_PRESS_MASK |
                        Gdk.EventMask.ENTER_NOTIFY_MASK |
                        Gdk.EventMask.LEAVE_NOTIFY_MASK)

        self.connect("enter-notify-event", self._on_enter_notify)
        self.connect("leave-notify-event", self._on_leave_notify)
        self.connect("button-press-event", self._on_button_press)
        self.connect("button-release-event", self._on_button_release)
        self.connect("key-press-event", self._on_key_press)
        self.connect("key-release-event", self._on_key_release)
        self.connect("focus-in-event", self._on_focus_in)
        self.connect("focus-out-event", self._on_focus_out)

    def _calc_natural_size(self, who_called='?'):
        ne = self.natural_extents
        nw, nh = ne.width, ne.height

        nw += self.shape.hadjustment + 2 * self.xpadding
        nh += 2 * self.ypadding

        self.natural_size = nw, nh
        self.set_size_request(nw, nh)

    # public methods
    @property
    def pathbar(self):
        return self.get_parent()

    def set_padding(self, xpadding, ypadding):
        self.xpadding = xpadding
        self.ypadding = ypadding
        self._calc_natural_size()

    def set_size_request(self, width, height):
        width = max(2 * self.xpadding + 1, width)
        height = max(2 * self.ypadding + 1, height)
        self.layout.set_width(Pango.SCALE * (width - 2 * self.xpadding))
        Gtk.Widget.set_size_request(self, width, height)

    def set_nopaint(self, is_nopaint):
        self.is_nopaint = is_nopaint
        self.queue_draw()

    def set_shape(self, shape):
        if shape == self.shape:
            return
        self.shape = shape
        self._calc_natural_size()
        self.queue_draw()

    def set_label(self, label):
        self.label = label

        self.atk.set_name(label)
        self.atk.set_description(_('Navigates to the %s page.') % label)

        self.layout.set_markup(label, -1)
        self.layout.set_width(-1)
        self.natural_extents = self.layout.get_pixel_extents()[1]

        self._calc_natural_size()
        self.queue_draw()

    def get_natural_size(self):
        return self.natural_size

    def get_natural_width(self):
        return self.natural_size[0]

    def get_natural_height(self):
        return self.natural_size[1]

    def get_width_request(self):
        return self.get_property("width-request")

    def get_height_request(self):
        return self.get_property("height-request")

    def queue_draw(self):
        a = self.get_allocation()
        parent = self.get_parent()
        if parent:
            aw = 12
        else:
            aw = 0
        self.queue_draw_area(a.x - aw / 2, a.y,
                             a.width + aw, a.height)


class NavigationBar(PathBar):

    def __init__(self, group=None):
        PathBar.__init__(self)
        self.id_to_part = {}
        self._callback_id = None

    def _on_part_clicked(self, part):
        part.callback(self, part)

    def add_with_id(self, label, callback, id, do_callback=True, animate=True):
        """
        Add a new button with the given label/callback

        If there is the same id already, replace the existing one
        with the new one
        """
        LOG.debug("add_with_id label='%s' callback='%s' id='%s' "
                  "do_callback=%s animate=%s" % (label, callback, id,
                                                 do_callback, animate))

        label = GObject.markup_escape_text(label)

        if not self.id_to_part:
            self.set_use_animations(False)
        else:
            self.set_use_animations(animate)

        # check if we have the button of that id or need a new one
        if id in self.id_to_part:
            part = self.id_to_part[id]
            if part.label == label:
                return

            part.set_label(label)
        else:
            part = PathPart(label)
            part.connect('clicked', self._on_part_clicked)

            part.set_name(id)
            self.id_to_part[id] = part

            part.callback = callback
            if do_callback:
                # cleanup any superceeded idle callback
                if self._callback_id:
                    GObject.source_remove(self._callback_id)
                    self._callback_id = None

                # if i do not have call the callback in an idle,
                # all hell breaks loose
                self._callback_id = GObject.idle_add(callback,
                                                     self,      # pathbar
                                                     part)

            self.append(part)

    def remove_ids(self, *ids, **kwargs):
        parts = self.get_parts()

        print 'remove ids', ids

        # it would seem parts can become stale within the id_to_part dict,
        # so we clean these up ...
        cleanup_ids = []
        # the index of the first part to be clipped
        index = len(parts)

        for id, part in self.id_to_part.iteritems():
            if id not in ids:
                continue
            if part not in parts:
                cleanup_ids.append(id)
                part.destroy()
            else:
                index = min(index, parts.index(part))

        if index == len(parts):
            return

        # cleanup any stale id:part pairs in the id_to_part dict
        for id in cleanup_ids:
            del self.id_to_part[id]

        # remove id:part pairs from the id_to_part dict, for whom removal
        # has been requested
        for id in ids:
            if id in self.id_to_part:
                del self.id_to_part[id]

        #~ print index, self.id_to_part.keys()

        # the index is used to remove all parts after the index but we
        # keep one part around to animate its removal
        for part in parts[index + 1:]:
            part.destroy()

        animate = True
        if 'animate' in kwargs:
            animate = kwargs['animate']

        # animate the removal of the final part, or not
        self.set_use_animations(animate)
        self.pop()

        # check if we should call the new tail parts callback
        if 'do_callback' in kwargs and kwargs['do_callback']:
            part = self[-1]
            part.callback(self, part)

    def remove_all(self, **kwargs):
        if len(self) <= 1:
            return
        ids = filter(lambda k: k != 'category',
                     self.id_to_part.keys())
        self.remove_ids(*ids, **kwargs)

    def has_id(self, id):
        return id in self.id_to_part

    def get_parts(self):
        return self.get_children()

    def get_active(self):
        parts = self.get_parts()
        if parts:
            return parts[-1]

    def get_button_from_id(self, id):
        """
        return the button for the given id (or None)
        """
        return self.id_to_part.get(id)

    def set_active_no_callback(self, part):
        pass


class TestIt:

    def __init__(self):

        def append(button, entry, pathbar):
            t = entry.get_text() or 'no label %s' % len(pathbar)
            part = PathPart(t)
            pathbar.append(part)

        def remove(button, entry, pathbar):
            pathbar.pop()

        win = Gtk.Window()
        win.set_border_width(30)
        win.set_size_request(600, 300)

        vb = Gtk.VBox(spacing=6)
        win.add(vb)

        pb = PathBar()
        pb.set_size_request(-1, 30)

        vb.pack_start(pb, False, False, 0)
        part = PathPart('Get Software')
        pb.append(part)

        entry = Gtk.Entry()
        vb.pack_start(entry, False, False, 0)

        b = Gtk.Button('Append')
        vb.pack_start(b, True, True, 0)
        b.connect('clicked', append, entry, pb)

        b = Gtk.Button('Remove')
        vb.pack_start(b, True, True, 0)
        b.connect('clicked', remove, entry, pb)

        win.show_all()

        win.connect('destroy', Gtk.main_quit)
        self.win = win
        self.win.pb = pb


def get_test_pathbar_window():
    t = TestIt()
    return t.win

if __name__ == '__main__':
    win = get_test_pathbar_window()
    Gtk.main()
