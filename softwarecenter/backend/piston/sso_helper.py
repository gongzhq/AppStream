#!/usr/bin/python
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
from gettext import gettext as _

from softwarecenter.backend.login_sso import get_sso_backend
from softwarecenter.backend.ubuntusso import UbuntuSSOAPI
from softwarecenter.enums import (SOFTWARE_CENTER_NAME_KEYRING,
                                  SOFTWARE_CENTER_SSO_DESCRIPTION,
                                  )
from softwarecenter.utils import clear_token_from_ubuntu_sso



class SSOLoginHelper(object):
    def __init__(self, xid=0):
        self.oauth = None
        self.xid = xid
        self.loop = GObject.MainLoop(GObject.main_context_default())
    
    def _login_successful(self, sso_backend, oauth_result):
        self.oauth = oauth_result
        # FIXME: actually verify the token against ubuntu SSO
        self.loop.quit()

    def verify_token(self, token):
        def _whoami_done(sso, me):
            self._whoami = me
            self.loop.quit()
        def _whoami_error(sso, err):
            #print "ERRR", err
            self.loop.quit()
        self._whoami = None
        sso = UbuntuSSOAPI()
        sso.connect("whoami", _whoami_done)
        sso.connect("error", _whoami_error)
        sso.whoami()
        self.loop.run()
        # check if the token is valid
        if self._whoami is None:
            return False
        else:
            return True

    def clear_token(self):
        clear_token_from_ubuntu_sso(SOFTWARE_CENTER_NAME_KEYRING)

    def get_oauth_token_and_verify_sync(self):
        token = self.get_oauth_token_sync()
        # check if the token is valid and reset it if it is not
        if token and not self.verify_token(token):
            self.clear_token()
            # re-trigger login
            token = self.get_oauth_token_sync()
        return token

    def get_oauth_token_sync(self):
        self.oauth = None
        sso = get_sso_backend(
            self.xid, 
            SOFTWARE_CENTER_NAME_KEYRING,
            _(SOFTWARE_CENTER_SSO_DESCRIPTION))
        sso.connect("login-successful", self._login_successful)
        sso.connect("login-failed", lambda s: self.loop.quit())
        sso.connect("login-canceled", lambda s: self.loop.quit())
        sso.login_or_register()
        self.loop.run()
        return self.oauth
