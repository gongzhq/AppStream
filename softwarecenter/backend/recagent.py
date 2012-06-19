#!/usr/bin/python
# -*- coding: utf-8 -*-

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

from gi.repository import GObject
import logging

import softwarecenter.paths
from spawn_helper import SpawnHelper

from softwarecenter.config import get_config
from softwarecenter.db.utils import get_installed_apps_list
from softwarecenter.utils import get_uuid

LOG = logging.getLogger(__name__)

class RecommenderAgent(GObject.GObject):

    __gsignals__ = {
        "server-status" : (GObject.SIGNAL_RUN_LAST,
                           GObject.TYPE_NONE, 
                           (GObject.TYPE_PYOBJECT,),
                          ),
        "profile" : (GObject.SIGNAL_RUN_LAST,
                     GObject.TYPE_NONE, 
                     (GObject.TYPE_PYOBJECT,),
                    ),
        "submit-profile-finished" : (GObject.SIGNAL_RUN_LAST,
                            GObject.TYPE_NONE, 
                            (GObject.TYPE_PYOBJECT, str),
                           ),
        "submit-anon-profile-finished" : (GObject.SIGNAL_RUN_LAST,
                                 GObject.TYPE_NONE, 
                                 (GObject.TYPE_PYOBJECT,),
                                ),
        "recommend-me" : (GObject.SIGNAL_RUN_LAST,
                              GObject.TYPE_NONE, 
                              (GObject.TYPE_PYOBJECT,),
                             ),
        "recommend-app" : (GObject.SIGNAL_RUN_LAST,
                           GObject.TYPE_NONE, 
                           (GObject.TYPE_PYOBJECT,),
                          ),
        "recommend-all-apps" : (GObject.SIGNAL_RUN_LAST,
                                GObject.TYPE_NONE, 
                                (GObject.TYPE_PYOBJECT,),
                               ),
        "recommend-top" : (GObject.SIGNAL_RUN_LAST,
                           GObject.TYPE_NONE, 
                           (GObject.TYPE_PYOBJECT,),
                          ),
        "error" : (GObject.SIGNAL_RUN_LAST,
                   GObject.TYPE_NONE, 
                   (str,),
                  ),
        }
    
    def __init__(self, xid=None):
        GObject.GObject.__init__(self)
        self.xid = xid
        self.recommender_uuid = self._get_recommender_uuid()

    def query_server_status(self):
        # build the command
        spawner = SpawnHelper()
        spawner.parent_xid = self.xid
        spawner.needs_auth = True
        spawner.connect("data-available", self._on_server_status_data)
        spawner.connect("error", lambda spawner, err: self.emit("error", err))
        spawner.run_generic_piston_helper(
            "SoftwareCenterRecommenderAPI", "server_status")
            
    def post_submit_profile(self, db):
        """ This will post the users profile to the recommender server
            and also generate the UUID for the user if that is not 
            there yet
        """
        # if we have not already set a recommender UUID, now is the time
        # to do it
        if not self.recommender_uuid:
            self.recommender_uuid = get_uuid()
        installed_pkglist = [app.pkgname 
                             for app in get_installed_apps_list(db)]
        data = self._generate_submit_profile_data(self.recommender_uuid,
                                                  installed_pkglist)
        # build the command
        spawner = SpawnHelper()
        spawner.parent_xid = self.xid
        spawner.needs_auth = True
        spawner.connect("data-available", self._on_submit_profile_data)
        spawner.connect("error", lambda spawner, err: self.emit("error", err))
        spawner.run_generic_piston_helper(
            "SoftwareCenterRecommenderAPI",
            "submit_profile",
            data=data)
            
    def post_submit_anon_profile(self, uuid, installed_packages, extra):
        # build the command
        spawner = SpawnHelper()
        spawner.parent_xid = self.xid
        spawner.needs_auth = True
        spawner.connect("data-available", self._on_submit_anon_profile_data)
        spawner.connect("error", lambda spawner, err: self.emit("error", err))
        spawner.run_generic_piston_helper(
            "SoftwareCenterRecommenderAPI",
            "submit_anon_profile",
            uuid=uuid,
            installed_packages=installed_packages,
            extra=extra)
            
    def query_profile(self, pkgnames):
        # build the command
        spawner = SpawnHelper()
        spawner.parent_xid = self.xid
        spawner.needs_auth = True
        spawner.connect("data-available", self._on_profile_data)
        spawner.connect("error", lambda spawner, err: self.emit("error", err))
        spawner.run_generic_piston_helper(
            "SoftwareCenterRecommenderAPI",
            "profile",
            pkgnames=pkgnames)

    def query_recommend_me(self):
        # build the command
        spawner = SpawnHelper()
        spawner.parent_xid = self.xid
        spawner.needs_auth = True
        spawner.connect("data-available", self._on_recommend_me_data)
        spawner.connect("error", lambda spawner, err: self.emit("error", err))
        spawner.run_generic_piston_helper(
            "SoftwareCenterRecommenderAPI", "recommend_me")
            
    def query_recommend_app(self, pkgname):
        # build the command
        spawner = SpawnHelper()
        spawner.parent_xid = self.xid
        spawner.connect("data-available", self._on_recommend_app_data)
        spawner.connect("error", lambda spawner, err: self.emit("error", err))
        spawner.run_generic_piston_helper(
            "SoftwareCenterRecommenderAPI",
            "recommend_app",
            pkgname=pkgname)
            
    def query_recommend_all_apps(self):
        # build the command
        spawner = SpawnHelper()
        spawner.parent_xid = self.xid
        spawner.connect("data-available", self._on_recommend_all_apps_data)
        spawner.connect("error", lambda spawner, err: self.emit("error", err))
        spawner.run_generic_piston_helper(
            "SoftwareCenterRecommenderAPI", "recommend_all_apps")
            
    def query_recommend_top(self):
        # build the command
        spawner = SpawnHelper()
        spawner.parent_xid = self.xid
        spawner.connect("data-available", self._on_recommend_top_data)
        spawner.connect("error", lambda spawner, err: self.emit("error", err))
        spawner.run_generic_piston_helper(
            "SoftwareCenterRecommenderAPI", "recommend_top")
            
    def _on_server_status_data(self, spawner, piston_server_status):
        self.emit("server-status", piston_server_status)
        
    def _on_profile_data(self, spawner, piston_profile):
        self.emit("profile", piston_profile)
        
    def _on_submit_profile_data(self, spawner, piston_submit_profile):
        self.emit("submit-profile-finished", 
                  piston_submit_profile, 
                  self.recommender_uuid)
        
    def _on_submit_anon_profile_data(self, spawner, piston_submit_anon_profile):
        self.emit("submit-anon_profile", piston_submit_anon_profile)

    def _on_recommend_me_data(self, spawner, piston_me_apps):
        self.emit("recommend-me", piston_me_apps)
        
    def _on_recommend_app_data(self, spawner, piston_app):
        self.emit("recommend-app", piston_app)
        
    def _on_recommend_all_apps_data(self, spawner, piston_all_apps):
        self.emit("recommend-all-apps", piston_all_apps)
        
    def _on_recommend_top_data(self, spawner, piston_top_apps):
        self.emit("recommend-top", piston_top_apps)
        
    def _get_recommender_uuid(self):
        """ returns the recommender UUID value, which can be empty if it
            has not yet been set (indicating that the user has not yet
            opted-in to the recommender service)
        """
        config = get_config()
        if config.has_option("general", "recommender_uuid"):
            recommender_uuid = config.get("general", "recommender_uuid")
            if recommender_uuid:
                return recommender_uuid
        return ""
        
    def _generate_submit_profile_data(self, recommender_uuid, package_list):
        submit_profile_data = [
            {
                'uuid': recommender_uuid, 
                'package_list': package_list
            }
        ]
        return submit_profile_data

   
if __name__ == "__main__":
    from gi.repository import Gtk

    def _recommend_top(agent, top_apps):
        print ("_recommend_top: %s" % top_apps)
    def _recommend_me(agent, top_apps):
        print ("_recommend_me: %s" % top_apps)
    def _error(agent, msg):
        print ("got a error: %s" % msg)
        Gtk.main_quit()

    # test specific stuff
    logging.basicConfig()
    softwarecenter.paths.datadir = "./data"

    agent = RecommenderAgent()
    agent.connect("recommend-top", _recommend_top)
    agent.connect("recommend-me", _recommend_me)
    agent.connect("error", _error)
    agent.query_recommend_top()
    agent.query_recommend_me()


    Gtk.main()
