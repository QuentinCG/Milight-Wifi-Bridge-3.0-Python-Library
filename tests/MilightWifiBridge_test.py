#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  Automatic test of MilightWifiBridge library with fake socket (using a Mock) and
  getting stdout with a specific class.
"""

import unittest
from MilightWifiBridge import MilightWifiBridge
import logging
import time
import sys

# Python 2.7/3  (Mock)
if sys.version_info >= (3, 3):
  from unittest.mock import patch
else:
  from mock import patch

# Python 2.7/3 compatibility (StringIO)
try:
  from StringIO import StringIO
except ImportError:
  from io import StringIO

class CapturingStdOut(list):
  """
  Capture stdout and give it back into a variable.

  Example:
  with CapturingStdOut() as std_output:
    anyFunctionHere()
  print(std_output)
  """
  def __enter__(self):
    self._stdout = sys.stdout
    sys.stdout = self._stringio = StringIO()
    return self
  def __exit__(self, *args):
    self.extend(self._stringio.getvalue().splitlines())
    del self._stringio    # free up some memory
    sys.stdout = self._stdout

"""
class MockSocket:
  TODO
@patch('socket.socket', new=MockSocket)
"""

class TestMilightWifiBridge(unittest.TestCase):
  """
  Test all the MilightWifiBridge class using fake socket (MockSocket) and getting the std output (CapturingStdOut)
  """
  def setUp(self):
    """
    Get test begining timestamp (used to show time to execute test at the end)
    """
    self.startTime = time.time()

    # Show full difference between 2 values that we wanted to be equal
    self.maxDiff = None

  def tearDown(self):
    """
    Show the execution time of the test
    """
    t = time.time() - self.startTime
    print(str(self.id())+": "+str(round(t, 2))+ " seconds")

  def test_instance(self):
    logging.debug("test_instance")
    milight = MilightWifiBridge.MilightWifiBridge()

if __name__ == '__main__':
  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)
  unittest.main()
