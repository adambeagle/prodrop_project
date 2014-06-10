"""
Timer.py
Author: Adam Beagle

Inspired by http://preshing.com/20110924/timing-your-code-using-pythons-with-statement
"""
import time

################################################################################
class Timer(object):
    """
    Defines a timer that can be used as part of a 'with' statement
    to time any block of code.

    ATTRIBUTES:
      * interval (read-only)
    """
    def __init__(self):
        self._interval = 0

    def __enter__(self):
        self._startTime = time.clock()
        return self

    def __exit__(self, *args):
        self._endTime = time.clock()
        self._interval = self._endTime - self._startTime

    @property
    def interval(self):
        return self._interval
