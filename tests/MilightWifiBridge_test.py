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

class MockSocket:
  __read_write = []

  @staticmethod
  def initializeMock(read_write):
    MockSocket.__read_write = read_write

  @staticmethod
  def initializeMilight(ip = "127.0.0.1", port = 100):
    milight = MilightWifiBridge.MilightWifiBridge()
    milight.setup(ip, port)

    return milight

  @staticmethod
  def initializeMockAndMilight(command, zoneId, milight_response):
    def calculateCheckSum(command, zoneId):
      checkSum = 0
      for byteCommand in command:
        checkSum += byteCommand
      checkSum += zoneId

      return (checkSum & 0xFF)

    if (isinstance(command, bytearray) and isinstance(milight_response, bool) and isinstance(zoneId, int)):
      command = [command]
      milight_response = [milight_response]
      zoneId = [zoneId]

    read_write = []

    seq_number = 1
    for index in range(len(command)):
      read_write.append(
        # Start session request
        {'IN': bytearray([0x20,0x00,0x00,0x00,0x16,0x02,0x62,0x3a,0xd5,0xed,0xa3,0x01,0xae,
                          0x08,0x2d,0x46,0x61,0x41,0xa7,0xf6,0xdc,0xaf,0xd3,0xe6,0x00,0x00,0x1e])})
      read_write.append(
        # Start session response
        {'OUT': bytearray([0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x10,0x11,0x12,0x13,0x14,
                           0x15,0x16,0x17,0x18,0x19,0x20,0x21,0x22])})

      bytesToSend = bytearray([0x80, 0x00, 0x00, 0x00, 0x11, 0x20, 0x21, 0x00, seq_number, 0x00])
      bytesToSend += bytearray(command[index])
      bytesToSend += bytearray([int(zoneId[index]), 0x00])
      bytesToSend += bytearray([int(calculateCheckSum(bytearray(command[index]), int(zoneId[index])))])

      # Request
      read_write.append({'IN': bytesToSend})

      # Response
      if len(milight_response) > index:
        if milight_response[index]:
          read_write.append({'OUT': bytearray([0x00,0x00,0x00,0x00,0x00,0x00,seq_number,0x00])})

      seq_number += 1

    MockSocket.initializeMock(read_write)

    return MockSocket.initializeMilight()

  def __init__(self, family = None, type = None):
    return

  def shutdown(self, how):
    return

  def close(self):
    return

  def connect(self, addr):
    return

  def settimeout(self, timeout_sec):
    return

  def sendto(self, data, addr):
    if len(MockSocket.__read_write) > 0:
      if 'IN' in MockSocket.__read_write[0]:
        check_val = MockSocket.__read_write[0]['IN']
        if bytearray(data) != bytearray(check_val):
          raise AssertionError('Mock Socket: Should write "' + str(check_val) + '" but "'+str(data)+'" requested')

        MockSocket.__read_write.pop(0)
        return len(data)

    return 0

  def recvfrom(self, bufsize):
    if len(MockSocket.__read_write) > 0:
      if 'OUT' in MockSocket.__read_write[0]:
        if len(MockSocket.__read_write[0]) <= bufsize:
          val = MockSocket.__read_write[0]['OUT']
          MockSocket.__read_write.pop(0)
          return (val, None)
        else:
          val = MockSocket.__read_write[0]['OUT'][:bufsize]
          MockSocket.__read_write[0]['OUT'] = MockSocket.__read_write[0]['OUT'][bufsize:]
          return (val, None)
    return ("", None)

class BasicCommandRequest:
    LINK_CMD = bytearray([0x3d,0x00,0x00,0x08,0x00,0x00,0x00,0x00,0x00])
    UNLINK_CMD = bytearray([0x3e,0x00,0x00,0x08,0x00,0x00,0x00,0x00,0x00])
    ON_CMD = bytearray([0x31,0x00,0x00,0x08,0x04,0x01,0x00,0x00,0x00])
    OFF_CMD = bytearray([0x31,0x00,0x00,0x08,0x04,0x02,0x00,0x00,0x00])
    WIFI_BRIDGE_LAMP_ON_CMD = bytearray([0x31,0x00,0x00,0x00,0x03,0x03,0x00,0x00,0x00])
    WIFI_BRIDGE_LAMP_OFF_CMD = bytearray([0x31,0x00,0x00,0x00,0x03,0x04,0x00,0x00,0x00])
    NIGHT_MODE_CMD = bytearray([0x31,0x00,0x00,0x08,0x04,0x05,0x00,0x00,0x00])
    WHITE_MODE_CMD = bytearray([0x31,0x00,0x00,0x08,0x05,0x64,0x00,0x00,0x00])
    WIFI_BRIDGE_LAMP_WHITE_MODE_CMD = bytearray([0x31,0x00,0x00,0x00,0x03,0x05,0x00,0x00,0x00])
    DISCO_MODE_SPEED_UP_CMD = bytearray([0x31,0x00,0x00,0x08,0x04,0x03,0x00,0x00,0x00])
    WIFI_BRIDGE_LAMP_DISCO_MODE_SPEED_UP_CMD = bytearray([0x31,0x00,0x00,0x00,0x03,0x02,0x00,0x00,0x00])
    DISCO_MODE_SLOW_DOWN_CMD = bytearray([0x31,0x00,0x00,0x08,0x04,0x04,0x00,0x00,0x00])
    WIFI_BRIDGE_LAMP_DISCO_MODE_SLOW_DOWN_CMD = bytearray([0x31,0x00,0x00,0x00,0x03,0x01,0x00,0x00,0x00])
    @staticmethod
    def getDiscoModeCmd(mode):
      return bytearray([0x31, 0x00, 0x00, 0x08, 0x06, mode, 0x00, 0x00, 0x00])
    @staticmethod
    def getDiscoModeBridgeCmd(mode):
      return bytearray([0x31, 0x00, 0x00, 0x00, 0x04, mode, 0x00, 0x00, 0x00])
    @staticmethod
    def getColorCmd(color):
      return bytearray([0x31, 0x00, 0x00, 0x08, 0x01, color, color, color, color])
    @staticmethod
    def getColorBridgeCmd(color):
      return bytearray([0x31, 0x00, 0x00, 0x00, 0x01, color, color, color, color])
    @staticmethod
    def getBrightnessCmd(brightness):
      return bytearray([0x31, 0x00, 0x00, 0x08, 0x03, brightness, 0x00, 0x00, 0x00])
    @staticmethod
    def getBrightnessBridgeCmd(brightness):
      return bytearray([0x31, 0x00, 0x00, 0x00, 0x02, brightness, 0x00, 0x00, 0x00])
    @staticmethod
    def getSaturationCmd(saturation):
      return bytearray([0x31, 0x00, 0x00, 0x08, 0x02, saturation, 0x00, 0x00, 0x00])
    @staticmethod
    def getTemperatureCmd(temperature):
      return bytearray([0x31, 0x00, 0x00, 0x08, 0x05, temperature, 0x00, 0x00, 0x00])

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
    self.assertNotEqual(milight, None)

  @patch('socket.socket', new=MockSocket)
  def test_close(self, new=MockSocket):
    logging.debug("test_close")
    milight = MilightWifiBridge.MilightWifiBridge()
    self.assertTrue(milight.setup("127.0.0.1", 100))
    self.assertEqual(milight.close(), None)

  @patch('socket.socket', new=MockSocket)
  def test_setup(self, new=MockSocket):
    logging.debug("test_instance")
    milight = MilightWifiBridge.MilightWifiBridge()
    self.assertTrue(milight.setup("127.0.0.1", 100))

  def test_socket(self, new=MockSocket):
    logging.debug("test_socket")
    # Use real socket, not Mock (to be sure the use of socket.socket is compatible between python version)
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("127.0.0.1", 9461))
    sock.settimeout(0)
    sock.sendto(bytearray([0x00]), ("127.0.0.1", 9461))
    try:
      sock.recvfrom(0)
    except Exception as e:
      logging.debug("Handled exception error: "+str(e))
      self.assertTrue(("10054" in str(e)) or ("Connection refused" in str(e)))

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()

    milight = MilightWifiBridge.MilightWifiBridge()
    self.assertTrue(milight.setup("127.0.0.1", 100))

  @patch('socket.socket', new=MockSocket)
  def test_get_mac_address(self, new=MockSocket):
    logging.debug("test_get_mac_address")

    MockSocket.initializeMock([
      {'IN': bytearray([0x20,0x00,0x00,0x00,0x16,0x02,0x62,0x3a,0xd5,0xed,0xa3,0x01,0xae,
                        0x08,0x2d,0x46,0x61,0x41,0xa7,0xf6,0xdc,0xaf,0xd3,0xe6,0x00,0x00,0x1e])},
      {'OUT': bytearray([0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x10,0x11,0x12,0x13,0x14,
                         0x15,0x16,0x17,0x18,0x19,0x20,0x21,0x22])},
      {'IN': bytearray([0x20,0x00,0x00,0x00,0x16,0x02,0x62,0x3a,0xd5,0xed,0xa3,0x01,0xae,
                        0x08,0x2d,0x46,0x61,0x41,0xa7,0xf6,0xdc,0xaf,0xd3,0xe6,0x00,0x00,0x1e])},
      {'OUT': bytearray([0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x10,0x11,0x12,0x13,0x14,
                         0x15,0x16,0x17,0x18,0x19,0x20,0x21,0x22])}
    ])
    milight = MockSocket.initializeMilight()
    self.assertEqual(milight.getMacAddress(), "8:9:10:11:12:13")

    MockSocket.initializeMock([
      {'IN': bytearray([0x20,0x00,0x00,0x00,0x16,0x02,0x62,0x3a,0xd5,0xed,0xa3,0x01,0xae,
                        0x08,0x2d,0x46,0x61,0x41,0xa7,0xf6,0xdc,0xaf,0xd3,0xe6,0x00,0x00,0x1e])},
      {'OUT': bytearray([0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x10,0xFF,0x12,0xF0,0xFF,0xDE,0x14,
                         0x15,0x16,0x17,0x18,0x19,0x20,0x21,0x22])},
      {'IN': bytearray([0x20,0x00,0x00,0x00,0x16,0x02,0x62,0x3a,0xd5,0xed,0xa3,0x01,0xae,
                        0x08,0x2d,0x46,0x61,0x41,0xa7,0xf6,0xdc,0xaf,0xd3,0xe6,0x00,0x00,0x1e])},
      {'OUT': bytearray([0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x10,0x11,0x12,0x13,0x14,
                         0x15,0x16,0x17,0x18,0x19,0x20,0x21,0x22])}
    ])
    milight = MockSocket.initializeMilight()
    self.assertEqual(milight.getMacAddress(), "10:ff:12:f0:ff:de")

  @patch('socket.socket', new=MockSocket)
  def test_turn_on(self, new=MockSocket):
    logging.debug("test_turn_on")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.ON_CMD, 2, True).turnOn(2))
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.ON_CMD, 2, False).turnOn(2))

  @patch('socket.socket', new=MockSocket)
  def test_turn_off(self, new=MockSocket):
    logging.debug("test_turn_off")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.OFF_CMD, 3, True).turnOff(3))
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.OFF_CMD, 3, False).turnOff(3))

  @patch('socket.socket', new=MockSocket)
  def test_turn_on_wifi_bridge(self, new=MockSocket):
    logging.debug("test_turn_on_wifi_bridge")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.WIFI_BRIDGE_LAMP_ON_CMD, 1, True).turnOnWifiBridgeLamp())
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.WIFI_BRIDGE_LAMP_ON_CMD, 1, False).turnOnWifiBridgeLamp())

  @patch('socket.socket', new=MockSocket)
  def test_turn_off_wifi_bridge(self, new=MockSocket):
    logging.debug("test_turn_off_wifi_bridge")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.WIFI_BRIDGE_LAMP_OFF_CMD, 1, True).turnOffWifiBridgeLamp())
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.WIFI_BRIDGE_LAMP_OFF_CMD, 1, False).turnOffWifiBridgeLamp())

  @patch('socket.socket', new=MockSocket)
  def test_set_night_mode(self, new=MockSocket):
    logging.debug("test_set_night_mode")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.NIGHT_MODE_CMD, 4, True).setNightMode(4))
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.NIGHT_MODE_CMD, 4, False).setNightMode(4))

  @patch('socket.socket', new=MockSocket)
  def test_set_white_mode(self, new=MockSocket):
    logging.debug("test_set_white_mode")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.WHITE_MODE_CMD, 4, True).setWhiteMode(4))
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.WHITE_MODE_CMD, 4, False).setWhiteMode(4))

  @patch('socket.socket', new=MockSocket)
  def test_set_white_mode_bridge(self, new=MockSocket):
    logging.debug("test_set_white_mode_bridge")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.WIFI_BRIDGE_LAMP_WHITE_MODE_CMD, 1, True).setWhiteModeBridgeLamp())
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.WIFI_BRIDGE_LAMP_WHITE_MODE_CMD, 1, False).setWhiteModeBridgeLamp())

  @patch('socket.socket', new=MockSocket)
  def test_speed_up_disco_mode(self, new=MockSocket):
    logging.debug("test_speed_up_disco_mode")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.DISCO_MODE_SPEED_UP_CMD, 4, True).speedUpDiscoMode(4))
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.DISCO_MODE_SPEED_UP_CMD, 4, False).speedUpDiscoMode(4))

  @patch('socket.socket', new=MockSocket)
  def test_speed_up_disco_mode_bridge(self, new=MockSocket):
    logging.debug("test_speed_up_disco_mode_bridge")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.WIFI_BRIDGE_LAMP_DISCO_MODE_SPEED_UP_CMD, 1, True).speedUpDiscoModeBridgeLamp())
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.WIFI_BRIDGE_LAMP_DISCO_MODE_SPEED_UP_CMD, 1, False).speedUpDiscoModeBridgeLamp())

  @patch('socket.socket', new=MockSocket)
  def test_slow_down_disco_mode(self, new=MockSocket):
    logging.debug("test_slow_down_disco_mode")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.DISCO_MODE_SLOW_DOWN_CMD, 4, True).slowDownDiscoMode(4))
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.DISCO_MODE_SLOW_DOWN_CMD, 4, False).slowDownDiscoMode(4))

  @patch('socket.socket', new=MockSocket)
  def test_slow_down_disco_mode_bridge(self, new=MockSocket):
    logging.debug("test_slow_down_disco_mode_bridge")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.WIFI_BRIDGE_LAMP_DISCO_MODE_SLOW_DOWN_CMD, 1, True).slowDownDiscoModeBridgeLamp())
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.WIFI_BRIDGE_LAMP_DISCO_MODE_SLOW_DOWN_CMD, 1, False).slowDownDiscoModeBridgeLamp())

  @patch('socket.socket', new=MockSocket)
  def test_link(self, new=MockSocket):
    logging.debug("test_link")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.LINK_CMD, 2, True).link(2))
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.LINK_CMD, 3, False).link(3))

  @patch('socket.socket', new=MockSocket)
  def test_unlink(self, new=MockSocket):
    logging.debug("test_unlink")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.UNLINK_CMD, 2, True).unlink(2))
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.UNLINK_CMD, 3, False).unlink(3))

  @patch('socket.socket', new=MockSocket)
  def test_set_disco_mode(self, new=MockSocket):
    logging.debug("test_set_disco_mode")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getDiscoModeCmd(1), 2, True).setDiscoMode(1, 2))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getDiscoModeCmd(9), 3, True).setDiscoMode(9, 3))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getDiscoModeCmd(9), 3, True).setDiscoMode(50, 3))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getDiscoModeCmd(9), 3, True).setDiscoMode(9999, 3))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getDiscoModeCmd(1), 3, True).setDiscoMode(-454, 3))
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.getDiscoModeCmd(1), 2, False).setDiscoMode(1, 2))

  @patch('socket.socket', new=MockSocket)
  def test_set_disco_mode_bridge(self, new=MockSocket):
    logging.debug("test_set_disco_mode_bridge")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getDiscoModeBridgeCmd(1), 1, True).setDiscoModeBridgeLamp(1))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getDiscoModeBridgeCmd(9), 1, True).setDiscoModeBridgeLamp(9))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getDiscoModeBridgeCmd(9), 1, True).setDiscoModeBridgeLamp(50))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getDiscoModeBridgeCmd(9), 1, True).setDiscoModeBridgeLamp(9999))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getDiscoModeBridgeCmd(1), 1, True).setDiscoModeBridgeLamp(-19))
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.getDiscoModeBridgeCmd(1), 1, False).setDiscoModeBridgeLamp(1))

  @patch('socket.socket', new=MockSocket)
  def test_set_color(self, new=MockSocket):
    logging.debug("test_set_color")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getColorCmd(1), 0, True).setColor(1, 0))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getColorCmd(50), 3, True).setColor(50, 3))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getColorCmd(255), 2, True).setColor(9999, 2))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getColorCmd(0), 2, True).setColor(-785, 2))
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.getColorCmd(1), 2, False).setColor(1, 2))

  @patch('socket.socket', new=MockSocket)
  def test_set_color_bridge(self, new=MockSocket):
    logging.debug("test_set_color_bridge")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getColorBridgeCmd(1), 1, True).setColorBridgeLamp(1))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getColorBridgeCmd(50), 1, True).setColorBridgeLamp(50))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getColorBridgeCmd(255), 1, True).setColorBridgeLamp(9999))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getColorBridgeCmd(0), 1, True).setColorBridgeLamp(-785))
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.getColorBridgeCmd(1), 1, False).setColorBridgeLamp(1))

  @patch('socket.socket', new=MockSocket)
  def test_brightness(self, new=MockSocket):
    logging.debug("test_brightness")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getBrightnessCmd(1), 0, True).setBrightness(1, 0))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getBrightnessCmd(50), 3, True).setBrightness(50, 3))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getBrightnessCmd(100), 2, True).setBrightness(15522, 2))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getBrightnessCmd(0), 2, True).setBrightness(-785, 2))
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.getBrightnessCmd(0), 2, False).setBrightness(0, 2))

  @patch('socket.socket', new=MockSocket)
  def test_brightness_bridge(self, new=MockSocket):
    logging.debug("test_brightness_bridge")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getBrightnessBridgeCmd(1), 1, True).setBrightnessBridgeLamp(1))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getBrightnessBridgeCmd(50), 1, True).setBrightnessBridgeLamp(50))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getBrightnessBridgeCmd(100), 1, True).setBrightnessBridgeLamp(15522))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getBrightnessBridgeCmd(0), 1, True).setBrightnessBridgeLamp(-785))
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.getBrightnessBridgeCmd(10), 1, False).setBrightnessBridgeLamp(10))

  @patch('socket.socket', new=MockSocket)
  def test_saturation(self, new=MockSocket):
    logging.debug("test_saturation")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getSaturationCmd(1), 0, True).setSaturation(1, 0))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getSaturationCmd(50), 3, True).setSaturation(50, 3))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getSaturationCmd(100), 2, True).setSaturation(15522, 2))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getSaturationCmd(0), 2, True).setSaturation(-785, 2))
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.getSaturationCmd(0), 2, False).setSaturation(0, 2))

  @patch('socket.socket', new=MockSocket)
  def test_temperature(self, new=MockSocket):
    logging.debug("test_temperature")
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getTemperatureCmd(1), 0, True).setTemperature(1, 0))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getTemperatureCmd(50), 3, True).setTemperature(50, 3))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getTemperatureCmd(100), 2, True).setTemperature(15522, 2))
    self.assertTrue(MockSocket.initializeMockAndMilight(BasicCommandRequest.getTemperatureCmd(0), 2, True).setTemperature(-785, 2))
    self.assertFalse(MockSocket.initializeMockAndMilight(BasicCommandRequest.getTemperatureCmd(0), 2, False).setTemperature(0, 2))

  @patch('socket.socket', new=MockSocket)
  def test_all_help_cmd(self):
    logging.debug("test_all_help_cmd")

    # Request failed because nothing requested
    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((['--ip', '127.0.0.1', '--port', '1234', '--timeout', '5', '--zone', '0', '--nodebug', '--debug']))
    self.assertNotEqual(cm.exception.code, 0)
    self.assertTrue("Debugging..." in std_output)
    self.assertTrue("Ip: 127.0.0.1" in std_output)
    self.assertTrue("Zone: 0" in std_output)
    self.assertTrue("Timeout: 5" in std_output)
    self.assertTrue("Port: 1234" in std_output)
    self.assertTrue("[ERROR] You must call one action, use '-h' to get more information." in std_output)

    # Invalid parameters
    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main(([]))
    self.assertNotEqual(cm.exception.code, 0)
    self.assertTrue("[ERROR] You need to specify the ip..." in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((['--undefinedParam']))
    self.assertNotEqual(cm.exception.code, 0)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main(('--ip', '127.0.0.1', '--port', '-4'))
    self.assertNotEqual(cm.exception.code, 0)
    self.assertTrue("[ERROR] You need to specify a valid port (more than 0)" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main(('--ip', '127.0.0.1', '--timeout', '-4'))
    self.assertNotEqual(cm.exception.code, 0)
    self.assertTrue("[ERROR] You need to specify a valid timeout (more than 0sec)" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main(('--ip', '127.0.0.1', '--zone', '-7'))
    self.assertNotEqual(cm.exception.code, 0)
    self.assertTrue("[ERROR] You need to specify a valid zone ID (between 0 and 4)" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main(('--ip', '127.0.0.1', '--zone', '7'))
    self.assertNotEqual(cm.exception.code, 0)
    self.assertTrue("[ERROR] You need to specify a valid zone ID (between 0 and 4)" in std_output)

    # Show help
    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("LINK (-l, --link): Link lights to a specific zone" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "help"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "ip"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "port"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "timeout"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "zone"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "getmacaddress"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "link"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "unlink"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "turnon"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "turnoff"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "turnonwifibridgelamp"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "turnoffwifibridgelamp"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "setnightmode"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "setwhitemode"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "setwhitemodebridgelamp"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "speedupdiscomodebridgelamp"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "slowdowndiscomodebridgelamp"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "speedupdiscomode"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "slowdowndiscomode"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "setcolor"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "setbrightness"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "setcolorbridgelamp"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "setbrightnessbridgelamp"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "setsaturation"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "settemperature"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "setdiscomode"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((["--help", "setdiscomodebridgelamp"]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Usage:" in std_output)

  @patch('socket.socket', new=MockSocket)
  def test_all_cmd_request_except_help_cmd(self):
    logging.debug("test_all_cmd_request_except_help_cmd")

    MockSocket.initializeMockAndMilight([
                                           BasicCommandRequest.LINK_CMD,
                                           BasicCommandRequest.UNLINK_CMD,
                                           BasicCommandRequest.ON_CMD,
                                           BasicCommandRequest.OFF_CMD,
                                           BasicCommandRequest.WIFI_BRIDGE_LAMP_ON_CMD,
                                           BasicCommandRequest.WIFI_BRIDGE_LAMP_OFF_CMD,
                                           BasicCommandRequest.WIFI_BRIDGE_LAMP_WHITE_MODE_CMD,
                                           BasicCommandRequest.WIFI_BRIDGE_LAMP_DISCO_MODE_SPEED_UP_CMD,
                                           BasicCommandRequest.WIFI_BRIDGE_LAMP_DISCO_MODE_SLOW_DOWN_CMD,
                                           BasicCommandRequest.getColorBridgeCmd(150),
                                           BasicCommandRequest.getBrightnessBridgeCmd(75),
                                           BasicCommandRequest.getDiscoModeBridgeCmd(5),
                                           BasicCommandRequest.NIGHT_MODE_CMD,
                                           BasicCommandRequest.WHITE_MODE_CMD,
                                           BasicCommandRequest.DISCO_MODE_SPEED_UP_CMD,
                                           BasicCommandRequest.DISCO_MODE_SLOW_DOWN_CMD,
                                           BasicCommandRequest.getDiscoModeCmd(5),
                                           BasicCommandRequest.getColorCmd(150),
                                           BasicCommandRequest.getBrightnessCmd(75),
                                           BasicCommandRequest.getSaturationCmd(50),
                                           BasicCommandRequest.getTemperatureCmd(25),
                                         ],
                                         [
                                           2, 2, 2, 2,
                                           1, 1, 1, 1, 1, 1, 1, 1,
                                           2, 2, 2, 2, 2, 2, 2, 2, 2,
                                         ],
                                         [
                                           True, True, True, True,
                                           True, True, True, True, True, True, True, True,
                                           True, True, True, True, True, True, True, True, True,
                                         ])

    # Request failed because nothing requested
    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((['--debug', '--ip', '127.0.0.1', '--zone', '2', '--debug',
                                 '--link',
                                 '--unlink',
                                 '--turnOn',
                                 '--turnOff',
                                 '--turnOnWifiBridgeLamp',
                                 '--turnOffWifiBridgeLamp',
                                 '--setWhiteModeBridgeLamp',
                                 '--speedUpDiscoModeBridgeLamp',
                                 '--slowDownDiscoModeBridgeLamp',
                                 '--setColorBridgeLamp', '150',
                                 '--setBrightnessBridgeLamp', '75',
                                 '--setDiscoModeBridgeLamp', '5',
                                 '--setNightMode',
                                 '--setWhiteMode',
                                 '--speedUpDiscoMode',
                                 '--slowDownDiscoMode',
                                 '--setDiscoMode', '5',
                                 '--setColor', '150',
                                 '--setBrightness', '75',
                                 '--setSaturation', '50',
                                 '--setTemperature', '25',
                                ]))
    self.assertEqual(cm.exception.code, 0)
    self.assertTrue("Ip: 127.0.0.1" in std_output)
    self.assertTrue("Zone: 2" in std_output)
    self.assertTrue("Timeout: 5.0" in std_output)
    self.assertTrue("Port: 5987" in std_output)
    self.assertTrue("Link zone 2: True" in std_output)
    self.assertTrue("Unlink zone 2: True" in std_output)
    self.assertTrue('Turn on zone 2: True' in std_output)
    self.assertTrue('Turn off zone 2: True' in std_output)
    self.assertTrue('Turn on wifi bridge lamp: True' in std_output)
    self.assertTrue('Turn off wifi bridge lamp: True' in std_output)
    self.assertTrue('Set white mode to wifi bridge: True' in std_output)
    self.assertTrue('Speed up disco mode to wifi bridge: True' in std_output)
    self.assertTrue('Slow down disco mode to wifi bridge: True' in std_output)
    self.assertTrue('Set color 150 to wifi bridge: True' in std_output)
    self.assertTrue('Set brightness 75% to the wifi bridge: True' in std_output)
    self.assertTrue('Set disco mode 5 to wifi bridge: True' in std_output)
    self.assertTrue('Set night mode to zone 2: True' in std_output)
    self.assertTrue('Set white mode to zone 2: True' in std_output)
    self.assertTrue('Speed up disco mode to zone 2: True' in std_output)
    self.assertTrue('Slow down disco mode to zone 2: True' in std_output)
    self.assertTrue('Set disco mode 5 to zone 2: True' in std_output)
    self.assertTrue('Set color 150 to zone 2: True' in std_output)
    self.assertTrue('Set brightness 75% to zone 2: True' in std_output)
    self.assertTrue('Set saturation 50% to zone 2: True' in std_output)
    self.assertTrue('Set temperature 25% to zone 2: True' in std_output)

    # Error returned by the device
    MockSocket.initializeMockAndMilight([
                                           BasicCommandRequest.LINK_CMD,
                                           BasicCommandRequest.UNLINK_CMD,
                                         ],
                                         [
                                           2, 2
                                         ],
                                         [
                                           True, False
                                         ])
    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((['--debug', '--ip', '127.0.0.1', '--zone', '2', '--debug',
                                 '--link',
                                 '--unlink',
                                 '--turnOn',
                                ]))
    self.assertNotEqual(cm.exception.code, 0)
    self.assertTrue("Link zone 2: True" in std_output)
    self.assertTrue("Unlink zone 2: False" in std_output)
    self.assertTrue("[ERROR] Request failed" in std_output)

    # Invalid input
    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((['--debug', '--ip', '127.0.0.1', '--zone', '2', '--debug',
                                 '--setColorBridgeLamp', '700',
                                ]))
    self.assertNotEqual(cm.exception.code, 0)
    self.assertTrue('[ERROR] Color must be between 0 and 255' in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((['--debug', '--ip', '127.0.0.1', '--zone', '2', '--debug',
                                 '--setBrightnessBridgeLamp', '101',
                                ]))
    self.assertNotEqual(cm.exception.code, 0)
    self.assertTrue('[ERROR] Brightness must be between 0 and 100 (in %)' in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((['--debug', '--ip', '127.0.0.1', '--zone', '2', '--debug',
                                 '--setDiscoModeBridgeLamp', '10',
                                ]))
    self.assertNotEqual(cm.exception.code, 0)
    self.assertTrue('[ERROR] Disco mode must be between 1 and 9' in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((['--debug', '--ip', '127.0.0.1', '--zone', '2', '--debug',
                                 '--setDiscoMode', '10',
                                ]))
    self.assertNotEqual(cm.exception.code, 0)
    self.assertTrue('[ERROR] Disco mode must be between 1 and 9' in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((['--debug', '--ip', '127.0.0.1', '--zone', '2', '--debug',
                                 '--setColor', '700',
                                ]))
    self.assertNotEqual(cm.exception.code, 0)
    self.assertTrue('[ERROR] Color must be between 0 and 255' in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((['--debug', '--ip', '127.0.0.1', '--zone', '2', '--debug',
                                 '--setBrightness', '101',
                                ]))
    self.assertNotEqual(cm.exception.code, 0)
    self.assertTrue('[ERROR] Brightness must be between 0 and 100 (in %)' in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((['--debug', '--ip', '127.0.0.1', '--zone', '2', '--debug',
                                 '--setSaturation', '101',
                                ]))
    self.assertNotEqual(cm.exception.code, 0)
    self.assertTrue('[ERROR] Saturation must be between 0 and 100 (in %)' in std_output)

    with self.assertRaises(SystemExit) as cm:
      with CapturingStdOut() as std_output:
        MilightWifiBridge.main((['--debug', '--ip', '127.0.0.1', '--zone', '2', '--debug',
                                 '--setTemperature', '101',
                                ]))
    self.assertNotEqual(cm.exception.code, 0)
    self.assertTrue('[ERROR] Temperature must be between 0 and 100 (in %)' in std_output)

if __name__ == '__main__':
  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)
  unittest.main()
