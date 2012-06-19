# Copyright (C) 2009-2010 Canonical
#
# Authors:
#  Seif Lotfy
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

import logging
import time
LOG = logging.getLogger("sofwarecenter.zeitgeist")

try:
    from zeitgeist.client import ZeitgeistClient
    from zeitgeist.datamodel import Event, Interpretation, ResultType
except ImportError:
    LOG.exception("zeitgeist import failed")
    ZEITGEIST_AVAILABLE = False
else:
    ZEITGEIST_AVAILABLE = True

class SoftwareCenterZeitgeist():
    """ simple wrapper around zeitgeist """

    def __init__(self):
        try:
            self.zg_client = ZeitgeistClient()
        except Exception as e:
            logging.warn("can not get zeitgeist client: '%s'" % e)
            self.zg_client = None
        
    def get_usage_counter(self, application, callback, timerange=None):
        """Request the usage count as integer for the given application.
           When the request is there, "callback" is called. A optional
           timerange like [time.time(), time.time() - 30*24*60*60] can
           also be specified
        """
        # helper
        def _callback(event_ids):
            callback(len(event_ids))
        # no client or empty query -> empty result
        if not self.zg_client or not application:
            callback(0)
            return
        # the app we are looking for
        application = "application://"+application.split("/")[-1]
        # the event_templates
        e1 = Event.new_for_values(
            actor=application, interpretation=Interpretation.MODIFY_EVENT.uri)
        e2 = Event.new_for_values(
            actor=application, interpretation=Interpretation.CREATE_EVENT.uri)
        # run it
        self.zg_client.find_event_ids_for_templates(
            [e1, e2], _callback, timerange=timerange, num_events=0)
       
    def get_popular_mimetypes(self, callback, num=3):
        """ get the "num" (default to 3) most popular mimetypes based
            on the last 1000 events that zeitgeist recorded and
            call "callback" with [(count1, "mime1"), (count2, "mime2"), ...] 
            as arguement
        """
        def _callback(events):
            # gather
            mimetypes = {}
            for event in events:
                if event.subjects is None:
                    continue
                mimetype = event.subjects[0].mimetype
                if not mimetype in mimetypes:
                    mimetypes[mimetype] = 0
                mimetypes[mimetype] += 1
            # return early if empty
            results = []
            if not mimetypes:
                callback([])
            # convert to result and sort
            for k, v in mimetypes.items():
                results.append([v, k])
            results.sort(reverse = True)
            # tell the client about it
            callback(results[:num])
        # no zeitgeist
        if not self.zg_client:
            return
        # trigger event (actual processing is done in _callback)
        # FIXME: investigate how result_type MostRecentEvents or
        #        MostRecentSubjects would affect the results
        self.zg_client.find_events_for_templates(
            [], _callback, num_events=1000, 
            result_type=ResultType.MostRecentEvents)

class SoftwareCenterZeitgeistDummy():
    def get_usage_counter(self, application, callback, timerange=None):
        callback(0)
    def get_popular_mimetypes(self, callback):
        callback([])

# singleton
if ZEITGEIST_AVAILABLE:
    zeitgeist_singleton = SoftwareCenterZeitgeist()
else:
    zeitgeist_singleton = SoftwareCenterZeitgeistDummy()

if __name__ == "__main__":

    def _callback_counter(events):
        print("test _callback: %s" % events)
    # all time gedit
    zeitgeist_singleton.get_usage_counter("gedit.desktop", _callback_counter)

    # yesterday gedit
    end = time.time()
    start = end - 24*60*60
    zeitgeist_singleton.get_usage_counter("gedit.desktop", _callback_counter,
                                          timerange=[start, end])
    
    # most popular
    def _callback_popular(mimetypes):
        print("test _callback: ")
        for tuple in mimetypes:
        	print(tuple)
    zeitgeist_singleton.get_popular_mimetypes(_callback_popular)

    from gi.repository import Gtk
    Gtk.main()
