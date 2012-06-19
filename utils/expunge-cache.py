#!/usr/bin/python

"""
Expunge httplib2 caches
"""

import argparse
import logging
import os
import time
import sys

class ExpungeCache(object):
    def __init__(self, dirs, args):
        self.dirs = dirs
        # days to keep data in the cache (0 == disabled)
        self.keep_time = 60*60*24* args.by_days
        self.keep_only_http200 = args.by_unsuccessful_http_states
        self.dry_run = args.dry_run

    def _rm(self, f):
        if self.dry_run:
            print "Would delete: %s" % f
        else:
            logging.debug("Deleting: %s" % f)
            os.unlink(f)

    def clean(self):
        # go over the directories
        now = time.time()
        for d in self.dirs:
            for root, dirs, files in os.walk(d):
                for f in files:
                    fullpath = os.path.join(root, f)
                    header = open(fullpath).readline().strip()
                    if not header.startswith("status:"):
                        logging.debug(
                            "Skipping files with unknown header: '%s'" % f)
                        continue
                    if self.keep_only_http200 and header != "status: 200":
                        self._rm(fullpath)
                    if self.keep_time:
                        mtime = os.path.getmtime(fullpath)
                        logging.debug("mtime of '%s': '%s" % (f, mtime))
                        if (mtime + self.keep_time) < now:
                            self._rm(fullpath)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='clean software-center httplib2 cache')
    parser.add_argument(
        '--debug', action="store_true",
        help='show debug output')
    parser.add_argument(
        '--dry-run', action="store_true",
        help='do not act, just show what would be done')
    parser.add_argument(
        'directories', metavar='directory', nargs='+', type=str,
        help='directories to be checked')
    parser.add_argument(
        '--by-days', type=int, default=0,
        help='expire everything older than N days')
    parser.add_argument(
        '--by-unsuccessful-http-states', action="store_true",
        help='expire any non 200 status responses')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # sanity checking
    if args.by_days == 0 and not args.by_unsuccessful_http_states:
        print "Need either --by-days or --by-unsuccessful-http-states argument"
        sys.exit(1)

    # be nice
    os.nice(19)

    # do it
    cleaner = ExpungeCache(args.directories, args)
    cleaner.clean()
