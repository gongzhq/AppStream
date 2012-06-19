#!/usr/bin/python

from gi.repository import GObject
from mock import patch
import unittest

from testutils import setup_test_env
setup_test_env()

from softwarecenter.backend.scagent import SoftwareCenterAgent

class TestSCAgent(unittest.TestCase):
    """ tests software-center-agent """

    def setUp(self):
        self.loop = GObject.MainLoop(GObject.main_context_default())
        self.error = False

    def on_query_done(self, scagent, data):
        print "query done, data: '%s'" % data
        self.loop.quit()
        
    def on_query_error(self, scagent, error):
        self.loop.quit()
        self.error = True

    def test_scagent_query_available(self):
        sca = SoftwareCenterAgent()
        sca.connect("available", self.on_query_done)
        sca.connect("error", self.on_query_error)
        sca.query_available()
        self.loop.run()        
        self.assertFalse(self.error)

    def test_scagent_query_exhibits(self):
        sca = SoftwareCenterAgent()
        sca.connect("exhibits", self.on_query_done)
        sca.connect("error", self.on_query_error)
        sca.query_exhibits()
        self.loop.run()  
        self.assertFalse(self.error)

    def test_scaagent_query_available_for_me_uses_complete_only(self):
        run_generic_piston_helper_fn = (
            'softwarecenter.backend.spawn_helper.SpawnHelper.'
            'run_generic_piston_helper')
        with patch(run_generic_piston_helper_fn) as mock_run_piston_helper:
            sca = SoftwareCenterAgent()
            sca.query_available_for_me()

            mock_run_piston_helper.assert_called_with(
                'SoftwareCenterAgentAPI', 'subscriptions_for_me',
                complete_only=True)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
