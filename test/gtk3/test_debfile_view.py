#!/usr/bin/python

import time
import unittest

from mock import Mock

from testutils import setup_test_env, do_events
setup_test_env()

import softwarecenter.paths
from softwarecenter.ui.gtk3.app import SoftwareCenterAppGtk3
from softwarecenter.ui.gtk3.panes.availablepane import AvailablePane

class DebFileOpenTestCase(unittest.TestCase):

    def test_deb_file_view_error(self):
        mock_options = Mock()
        mock_options.display_navlog = False
        mock_options.disable_apt_xapian_index = False
        mock_options.disable_buy = False
        xapianpath = softwarecenter.paths.XAPIAN_BASE_PATH
        app = SoftwareCenterAppGtk3(
            softwarecenter.paths.datadir, xapianpath, mock_options)
        app.run(["./data/test_debs/gdebi-test1.deb"])
        # give it time
        for i in range(10):
            time.sleep(0.1)
            do_events()
            # its ok to break out early
            if (app.available_pane.app_details_view and
                app.available_pane.app_details_view.get_property("visible")):
                break
        # check that we are on the right page
        self.assertEqual(
            app.available_pane.get_current_page(), AvailablePane.Pages.DETAILS)
        # this is deb that is not installable
        action_button = app.available_pane.app_details_view.pkg_statusbar.button
        self.assertFalse(action_button.get_property("visible"))
        


if __name__ == "__main__":
    unittest.main()
