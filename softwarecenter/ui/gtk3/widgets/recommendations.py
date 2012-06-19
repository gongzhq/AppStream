# -*- coding: utf-8 -*-
# Copyright (C) 2012 Canonical
#
# Authors:
#  Gary Lasker
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

from gi.repository import Gtk, GObject
import logging

from gettext import gettext as _

from softwarecenter.ui.gtk3.em import StockEms
from softwarecenter.ui.gtk3.widgets.containers import (FramedHeaderBox,
                                                       FlowableGrid)
from softwarecenter.db.categories import (RecommendedForYouCategory,
                                          AppRecommendationsCategory)
from softwarecenter.backend.recagent import RecommenderAgent


LOG = logging.getLogger(__name__)


class RecommendationsPanel(FramedHeaderBox):
    """
    Base class for widgets that display recommendations
    """

    __gsignals__ = {
        "application-activated": (GObject.SIGNAL_RUN_LAST,
                                  GObject.TYPE_NONE,
                                  (GObject.TYPE_PYOBJECT,),
                                 ),
        }

    def __init__(self, catview):
        FramedHeaderBox.__init__(self)
        # FIXME: we only need the catview for "add_titles_to_flowgrid"
        #        and "on_category_clicked" so we should be able to
        #        extract this to a "leaner" widget
        self.catview = catview
        self.catview.connect(
            "application-activated", self._on_application_activated)
        self.recommender_agent = RecommenderAgent()

    def _on_application_activated(self, catview, app):
        self.emit("application-activated", app)


class RecommendationsPanelLobby(RecommendationsPanel):
    """
    Panel for use in the lobby view that manages the recommendations
    experience, includes the initial opt-in screen and display of
    recommendations once they have been received from the recommender agent
    """
    __gsignals__ = {
        "recommendations-opt-in": (GObject.SIGNAL_RUN_LAST,
                                   GObject.TYPE_NONE,
                                   (GObject.TYPE_STRING,),
                                  ),
        "recommendations-opt-out": (GObject.SIGNAL_RUN_LAST,
                                    GObject.TYPE_NONE,
                                    (),
                                   ),
        }

    def __init__(self, catview):
        RecommendationsPanel.__init__(self, catview)
        self.set_header_label(_(u"Recommended for You"))

        # if we already have a recommender UUID, then the user is already
        # opted-in to the recommender service
        self.recommended_for_you_content = None
        if self.recommender_agent.recommender_uuid:
            self._update_recommended_for_you_content()
        else:
            self._show_opt_in_view()

    def _show_opt_in_view(self):
        # opt in box
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, StockEms.MEDIUM)
        vbox.set_border_width(StockEms.LARGE)
        self.opt_in_vbox = vbox  # for tests
        self.recommended_for_you_content = vbox  # hook it up to the rest

        self.add(self.recommended_for_you_content)

        # opt in button
        button = Gtk.Button(_("Turn On Recommendations"))
        button.connect("clicked", self._on_opt_in_button_clicked)
        hbox = Gtk.Box(Gtk.Orientation.HORIZONTAL)
        hbox.pack_start(button, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)
        self.opt_in_button = button  # for tests

        # opt in text
        text = _("To make recommendations, Ubuntu Software Center "
                 "will occasionally send to Canonical an anonymous list "
                 "of software currently installed.")
        label = Gtk.Label(text)
        label.set_alignment(0, 0.5)
        label.set_line_wrap(True)
        vbox.pack_start(label, False, False, 0)

    def _on_opt_in_button_clicked(self, button):
        # we upload the user profile here, and only after this is finished
        # do we fire the request for recommendations and finally display
        # them here -- a spinner is shown for this process (the spec
        # wants a progress bar, but we don't have access to real-time
        # progress info)
        self._upload_user_profile_and_get_recommendations()

    def _upload_user_profile_and_get_recommendations(self):
        # initiate upload of the user profile here
        self._upload_user_profile()

    def _upload_user_profile(self):
        self.spinner_notebook.show_spinner(_(u"Submitting inventory…"))
        self.recommender_agent.connect("submit-profile-finished",
                                  self._on_profile_submitted)
        self.recommender_agent.connect("error",
                                  self._on_profile_submitted_error)
        self.recommender_agent.post_submit_profile(self.catview.db)

    def _on_profile_submitted(self, agent, profile, recommender_uuid):
        # after the user profile data has been uploaded, make the request
        # and load the the recommended_for_you content
        LOG.debug("The recommendations profile has been successfully "
                  "submitted to the recommender agent")
        self.emit("recommendations-opt-in", recommender_uuid)
        self._update_recommended_for_you_content()

    def _on_profile_submitted_error(self, agent, msg):
        LOG.warn("Error while submitting the recommendations profile to the "
                 "recommender agent: %s" % msg)
        # TODO: handle this! display an error message in the panel
        self._hide_recommended_for_you_panel()

    def _update_recommended_for_you_content(self):
        # destroy the old content to ensure we don't see it twice
        # (also removes the opt-in panel if it was there)
        if self.recommended_for_you_content:
            self.recommended_for_you_content.destroy()
        # add the new stuff
        self.header_implements_more_button()
        self.recommended_for_you_content = FlowableGrid()
        self.add(self.recommended_for_you_content)
        self.spinner_notebook.show_spinner(_(u"Receiving recommendations…"))
        # get the recommendations from the recommender agent
        self.recommended_for_you_cat = RecommendedForYouCategory()
        self.recommended_for_you_cat.connect(
                                    'needs-refresh',
                                    self._on_recommended_for_you_agent_refresh)
        self.recommended_for_you_cat.connect('recommender-agent-error',
                                             self._on_recommender_agent_error)

    def _on_recommended_for_you_agent_refresh(self, cat):
        docs = cat.get_documents(self.catview.db)
        # display the recommendedations
        if len(docs) > 0:
            self.catview._add_tiles_to_flowgrid(docs,
                                        self.recommended_for_you_content, 8)
            self.recommended_for_you_content.show_all()
            self.spinner_notebook.hide_spinner()
            self.more.connect('clicked',
                              self.catview.on_category_clicked,
                              cat)
        else:
            # TODO: this test for zero docs is temporary and will not be
            # needed once the recommendation agent is up and running
            self._hide_recommended_for_you_panel()

    def _on_recommender_agent_error(self, agent, msg):
        LOG.warn("Error while accessing the recommender agent for the "
                 "lobby recommendations: %s" % msg)
        # TODO: temporary, instead we will display cached recommendations here
        self._hide_recommended_for_you_panel()

    def _hide_recommended_for_you_panel(self):
        # and hide the pane
        self.hide()


class RecommendationsPanelDetails(RecommendationsPanel):
    """
    Panel for use in the details view to display recommendations for a given
    application
    """
    def __init__(self, catview):
        RecommendationsPanel.__init__(self, catview)
        self.set_header_label(_(u"People Also Installed"))
        self.app_recommendations_content = FlowableGrid()
        self.add(self.app_recommendations_content)

    def set_pkgname(self, pkgname):
        self.pkgname = pkgname
        self._update_app_recommendations_content()

    def _update_app_recommendations_content(self):
        self.app_recommendations_content.remove_all()
        self.spinner_notebook.show_spinner(_(u"Receiving recommendations…"))
        # get the recommendations from the recommender agent
        self.app_recommendations_cat = AppRecommendationsCategory(self.pkgname)
        self.app_recommendations_cat.connect(
                                    'needs-refresh',
                                    self._on_app_recommendations_agent_refresh)
        self.app_recommendations_cat.connect('recommender-agent-error',
                                             self._on_recommender_agent_error)

    def _on_app_recommendations_agent_refresh(self, cat):
        docs = cat.get_documents(self.catview.db)
        # display the recommendations
        if len(docs) > 0:
            self.catview._add_tiles_to_flowgrid(docs,
                                        self.app_recommendations_content, 8)
            self.show_all()
            self.spinner_notebook.hide_spinner()
        else:
            self._hide_app_recommendations_panel()

    def _on_recommender_agent_error(self, agent, msg):
        LOG.warn("Error while accessing the recommender agent for the "
                 "details view recommendations: %s" % msg)
        # TODO: temporary, instead we will display cached recommendations here
        self._hide_app_recommendations_panel()

    def _hide_app_recommendations_panel(self):
        # and hide the pane
        self.hide()


# test helpers
def get_test_window():
    import softwarecenter.log
    softwarecenter.log.root.setLevel(level=logging.DEBUG)
    fmt = logging.Formatter("%(name)s - %(message)s", None)
    softwarecenter.log.handler.setFormatter(fmt)

    # this is *way* to complicated we should *not* need a CatView
    # here! see FIXME in RecommendationsPanel.__init__()
    from softwarecenter.ui.gtk3.views.catview_gtk import CategoriesViewGtk
    from softwarecenter.testutils import (
        get_test_db, get_test_pkg_info, get_test_gtk3_icon_cache)
    cache = get_test_pkg_info()
    db = get_test_db()
    icons = get_test_gtk3_icon_cache()
    catview = CategoriesViewGtk(softwarecenter.paths.datadir,
                                softwarecenter.paths.APP_INSTALL_PATH,
                                cache,
                                db,
                                icons)

    view = RecommendationsPanelLobby(catview)

    win = Gtk.Window()
    win.connect("destroy", lambda x: Gtk.main_quit())
    win.add(view)
    win.set_data("rec_panel", view)
    win.set_size_request(600, 200)
    win.show_all()

    return win


if __name__ == "__main__":
    win = get_test_window()
    Gtk.main()
