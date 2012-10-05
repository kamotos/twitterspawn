#!/usr/bin/env python

import datetime
import sys

import gevent

def throttle_hook(response):
    ratelimited = "x-ratelimit-remaining" in response.headers and \
                  "x-ratelimit-reset" in response.headers 

    if ratelimited:
        remaining = int(response.headers["x-ratelimit-remaining"])
        reset = datetime.datetime.utcfromtimestamp(float(response.headers["x-ratelimit-reset"]))
        now = datetime.datetime.utcnow()
        
        time_to_reset = reset - now
        #total_seconds doesn't exist in Python 2.6
        if hasattr(datetime.timedelta, "total_seconds"):
            time_to_sleep = time_to_reset.total_seconds() / remaining if remaining > 0 else 0
        else:
            time_to_sleep = int(time_to_reset.days * 86400.0 +
                                time_to_reset.seconds +
                                time_to_reset.microseconds * 1e-6) / remaining if remaining > 0 else 0

        sys.stderr.write("%d requests remaining. Sleeping for %.2f secs...\n" % (remaining, time_to_sleep))
        gevent.sleep(time_to_sleep)
