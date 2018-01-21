#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  Milight 3.0 (LimitlessLED Wifi Bridge v6.0) library: Control wireless lights (Milight 3.0) with Wifi

  Note that this library was tested with Milight Wifi iBox v1 and RGBW lights. It should work with any other
  lights and bridge using Milight 3.0 / LimitlessLED v6.0 protocol.

  Non-exhaustive functionality using the python class or using this file from shell
  (launch this python file with '-h' parameter to get more information):
    - Initialize the Wifi bridge
    - Link/Unlink lights
    - Light on/off
    - Wifi bridge lamp on/off
    - Set night mode
    - Set white mode
    - Set color
    - Set saturation
    - Set brightness
    - Set disco mode (9 available)
    - Increase/Decrease disco mode speed
    - Get Milight wifi bridge MAC address
    - ...

  Used protocol: http://www.limitlessled.com/dev/ (LimitlessLED Wifi Bridge v6.0 section)
"""
__author__ = 'Quentin Comte-Gaz'
__email__ = "quentin@comte-gaz.com"
__license__ = "MIT License"
__copyright__ = "Copyright Quentin Comte-Gaz (2017)"
__python_version__ = "3.+"
__version__ = "1.0 (2017/04/10)"
__status__ = "Usable for any project"

import socket
import time
import collections
import sys, getopt
import logging
import binascii

class MilightWifiBridge:
  """Milight 3.0 Wifi Bridge class

  Calling setup() function is necessary in order to make this class work properly.
  """
  ######################### Enums #########################
  class eZone:
    ALL = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4

  class eDiscoMode:
    DISCO_1 = 1
    DISCO_2 = 2
    DISCO_3 = 3
    DISCO_4 = 4
    DISCO_5 = 5
    DISCO_6 = 6
    DISCO_7 = 7
    DISCO_8 = 8
    DISCO_9 = 9

  class eTemperature:
    WARM = 0 # 2700K
    WARM_WHITE =  8 # 3000K
    COOL_WHITE = 35 # 4000K
    DAYLIGHT = 61 # 5000K
    COOL_DAYLIGHT = 100 # 6500K


  ######################### static variables/static functions/internal struct #########################
  __START_SESSION_MSG = bytearray([0x20, 0x00, 0x00, 0x00, 0x16, 0x02, 0x62, 0x3A, 0xD5, 0xED, 0xA3, 0x01, 0xAE, 0x08,
                               0x2D, 0x46, 0x61, 0x41, 0xA7, 0xF6, 0xDC, 0xAF, 0xD3, 0xE6, 0x00, 0x00, 0x1E])

  # Response sent by the milight wifi bridge after a start session query
  # Keyword arguments:
  #   responseReceived -- (bool) Response valid
  #   mac -- (string) MAC address of the wifi bridge
  #   sessionId1 -- (int) First part of the session ID
  #   sessionId2 -- (int) Second part of the session ID
  #   sequenceNumber -- (int) Sequence number
  __START_SESSION_RESPONSE = collections.namedtuple("StartSessionResponse", "responseReceived mac sessionId1 sessionId2")

  __ON_CMD = bytearray([0x31, 0x00, 0x00, 0x08, 0x04, 0x01, 0x00, 0x00, 0x00])
  __OFF_CMD = bytearray([0x31, 0x00, 0x00, 0x08, 0x04, 0x02, 0x00, 0x00, 0x00])
  __NIGHT_MODE_CMD = bytearray([0x31, 0x00, 0x00, 0x08, 0x04, 0x05, 0x00, 0x00, 0x00])
  __WHITE_MODE_CMD = bytearray([0x31, 0x00, 0x00, 0x08, 0x05, 0x64, 0x00, 0x00, 0x00])
  __DISCO_MODE_SPEED_UP_CMD = bytearray([0x31, 0x00, 0x00, 0x08, 0x04, 0x03, 0x00, 0x00, 0x00])
  __DISCO_MODE_SLOW_DOWN_CMD = bytearray([0x31, 0x00, 0x00, 0x08, 0x04, 0x04, 0x00, 0x00, 0x00])
  __LINK_CMD = bytearray([0x3D, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00])
  __UNLINK_CMD = bytearray([0x3E, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00])

  __WIFI_BRIDGE_LAMP_ON_CMD = bytearray([0x31, 0x00, 0x00, 0x00, 0x03, 0x03, 0x00, 0x00, 0x00])
  __WIFI_BRIDGE_LAMP_OFF_CMD = bytearray([0x31, 0x00, 0x00, 0x00, 0x03, 0x04, 0x00, 0x00, 0x00])
  __WIFI_BRIDGE_LAMP_WHITE_MODE_CMD = bytearray([0x31, 0x00, 0x00, 0x00, 0x03, 0x05, 0x00, 0x00, 0x00])
  __WIFI_BRIDGE_LAMP_DISCO_MODE_SPEED_UP_CMD = bytearray([0x31, 0x00, 0x00, 0x00, 0x03, 0x02, 0x00, 0x00, 0x00])
  __WIFI_BRIDGE_LAMP_DISCO_MODE_SLOW_DOWN_CMD = bytearray([0x31, 0x00, 0x00, 0x00, 0x03, 0x01, 0x00, 0x00, 0x00])

  @staticmethod
  def __getSetBridgeLampColorCmd(color):
    """Give 'Set color for bridge lamp' command

    Keyword arguments:
      color -- (int) Color value between 0x00 and 0xFF
                     examples: 0xFF = Red, 0xD9 = Lavender, 0xBA = Blue, 0x85 = Aqua,
                               0x7A = Green, 0x54 = Lime, 0x3B = Yellow, 0x1E = Orange

    return: (bytearray) 'Set colo for bridge lamp' command
    """
    color = int(color) & 0xFF
    return bytearray([0x31, 0x00, 0x00, 0x00, 0x01, color, color, color, color])

  @staticmethod
  def __getSetColorCmd(color):
    """Give 'Set color' command

    Keyword arguments:
      color -- (int) Color value between 0x00 and 0xFF
                     examples: 0xFF = Red, 0xD9 = Lavender, 0xBA = Blue, 0x85 = Aqua,
                               0x7A = Green, 0x54 = Lime, 0x3B = Yellow, 0x1E = Orange

    return: (bytearray) 'Set color' command
    """
    color = int(color) & 0xFF
    return bytearray([0x31, 0x00, 0x00, 0x08, 0x01, color, color, color, color])

  @staticmethod
  def __getSetDiscoModeForBridgeLampCmd(mode):
    """Give 'Set disco mode for bridge lamp' command

    Keyword arguments:
      mode -- (int) Disco mode between 1 and 9

    return: (bytearray) 'Set disco mode for bridge lamp' command
    """
    mode = int(mode) & 0xFF
    if mode < 1:
      mode = 1
    elif mode > 9:
      mode = 9

    return bytearray([0x31, 0x00, 0x00, 0x00, 0x04, mode, 0x00, 0x00, 0x00])

  @staticmethod
  def __getSetDiscoModeCmd(mode):
    """Give 'Set disco mode' command

    Keyword arguments:
      mode -- (int) Disco mode between 1 and 9

    return: (bytearray) 'Set disco mode' command
    """
    mode = int(mode) & 0xFF
    if mode < 1:
      mode = 1
    elif mode > 9:
      mode = 9

    return bytearray([0x31, 0x00, 0x00, 0x08, 0x06, mode, 0x00, 0x00, 0x00])

  @staticmethod
  def __getSetBrightnessForBridgeLampCmd(brightness):
    """Give 'Set brightness for bridge lamp' command

    Keyword arguments:
      brightness -- (int) Brightness percentage between 0 and 100

    return: (bytearray) 'Set brightness for bridge lamp' command
    """
    brightness = int(brightness) & 0xFF
    if brightness < 0:
      brightness = 0
    elif brightness > 100:
      brightness = 100

    return bytearray([0x31, 0x00, 0x00, 0x00, 0x02, brightness, 0x00, 0x00, 0x00])

  @staticmethod
  def __getSetBrightnessCmd(brightness):
    """Give 'Set brightness' command

    Keyword arguments:
      brightness -- (int) Brightness percentage between 0 and 100

    return: (bytearray) 'Set brightness' command
    """
    brightness = int(brightness) & 0xFF
    if brightness < 0:
      brightness = 0
    elif brightness > 100:
      brightness = 100

    return bytearray([0x31, 0x00, 0x00, 0x08, 0x03, brightness, 0x00, 0x00, 0x00])

  @staticmethod
  def __getSetSaturationCmd(saturation):
    """Give 'Set saturation' command

    Keyword arguments:
      saturation -- (int) Saturation percentage between 0 and 100

    return: (bytearray) 'Set saturation' command
    """
    saturation = int(saturation) & 0xFF
    if saturation < 0:
      saturation = 0
    elif saturation > 100:
      saturation = 100

    return bytearray([0x31, 0x00, 0x00, 0x08, 0x02, saturation, 0x00, 0x00, 0x00])

  @staticmethod
  def __getSetTemperatureCmd(temperature):
    """Give 'Set temperature' command

    Keyword arguments:
      temperature -- (int) Temperature percentage between 0 and 100
                           0% <=> Warm white (2700K)
                           100% <=> Cool white (6500K)

    return: (bytearray) 'Set temperature' command
    """
    temperature = int(temperature) & 0xFF
    if temperature < 0:
      temperature = 0
    elif temperature > 100:
      temperature = 100

    return bytearray([0x31, 0x00, 0x00, 0x08, 0x05, temperature, 0x00, 0x00, 0x00])

  @staticmethod
  def __calculateCheckSum(command, zoneId):
    """Calculate request checksum

    Note: Request checksum is equal to SUM(all command bytes and of the zone number) & 0xFF

    Keyword arguments:
      command -- (bytearray) Command
      zoneId -- (int) Zone ID

    return: (int) Request checksum
    """
    checkSum = 0
    for byteCommand in command:
      checkSum += byteCommand
    checkSum += zoneId

    return (checkSum & 0xFF)


  ################################### INIT ####################################
  def __init__(self):
    """Class must be initialized with setup()"""
    self.close()


  ################################### SETUP ####################################
  def close(self):
    """Close connection with Milight wifi bridge"""
    self.__initialized = False
    self.__sequence_number = 0

    try:
      self.__sock.shutdown(socket.SHUT_RDWR)
      self.__sock.close()
      logging.debug("Socket closed")
    # If close before initialization, better handle attribute error
    except AttributeError:
      pass

  def setup(self, ip, port=5987, timeout_sec=5.0):
    """Initialize the class (can be launched multiple time if setup changed or module crashed)

    Keyword arguments:
      ip -- (string) IP to communication with the Milight wifi bridge
      port -- (int, optional) UDP port to communication with the Milight wifi bridge
      timeout_sec -- (int, optional) Timeout in sec for Milight wifi bridge to answer commands

    return: (bool) Milight wifi bridge initialized
    """
    # Close potential previous Milight wifi bridge session
    self.close()

    # Create new milight wifi bridge session
    try:
      self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
      self.__ip = ip
      self.__port = port
      self.__sock.connect((self.__ip, self.__port))
      self.__sock.settimeout(timeout_sec)
      self.__initialized = True
      logging.debug("UDP connection initialized with ip {} and port {}".format(str(ip), str(port)))
    except (socket.error, socket.herror, socket.gaierror, socket.timeout) as e:
      logging.error("Impossible to initialize the UDP connection with ip {} and port {}".format(str(ip), str(port)))
      pass

    return self.__initialized


  ######################### INTERNAL UTILITY FUNCTIONS #########################
  def __startSession(self):
    """Send start session request and return start session information

    return: (MilightWifiBridge.__START_SESSION_RESPONSE) Start session information containing response received,
                                                         mac address and session IDs
    """
    # Send start session request
    data_to_send = MilightWifiBridge.__START_SESSION_MSG
    logging.debug("Sending frame '{}' to {}:{}".format(str(binascii.hexlify(data_to_send)),
                                                     str(self.__ip), str(self.__port)))
    self.__sock.sendto(data_to_send, (self.__ip, self.__port))
    response = MilightWifiBridge.__START_SESSION_RESPONSE(responseReceived=False, mac="", sessionId1=-1, sessionId2=-1)

    try:
      # Receive start session response
      data, addr = self.__sock.recvfrom(1024)
      if len(data) == 22:
        # Parse valid start session response
        response = MilightWifiBridge.__START_SESSION_RESPONSE(responseReceived=True,
                                                              mac=str("{}:{}:{}:{}:{}:{}".format(format(data[7], 'x'),
                                                                                                 format(data[8], 'x'),
                                                                                                 format(data[9], 'x'),
                                                                                                 format(data[10], 'x'),
                                                                                                 format(data[11], 'x'),
                                                                                                 format(data[12], 'x'))),
                                                              sessionId1=int(data[19]),
                                                              sessionId2=int(data[20]))
        logging.debug("Start session (mac address: {}, session ID 1: {}, session ID 2: {})"
                      .format(str(response.mac), str(response.sessionId1), str(response.sessionId2)))
      else:
        logging.warning("Invalid start session response size")
    except socket.timeout:
      logging.warning("Timed out for start session response")

    return response

  def __sendRequest(self, command, zoneId):
    """Send command to a specific zone and get response (ACK from the wifi bridge)

    Keyword arguments:
      command -- (bytearray) Command
      zoneId -- (int) Zone ID

    return: (bool) Request received by the wifi bridge
    """
    returnValue = False

    # Send request only if valid parameters
    if len(bytearray(command)) == 9:
      if int(zoneId) >= 0 and int(zoneId) <= 4:
        startSessionResponse = self.__startSession()
        if startSessionResponse.responseReceived:
          # For each request, increment the sequence number (even if the session ID is regenerated)
          # Sequence number must be between 0x01 and 0xFF
          self.__sequence_number = (self.__sequence_number + 1) & 0xFF
          if self.__sequence_number == 0:
            self.__sequence_number = 1

          # Prepare request frame to send
          bytesToSend = bytearray([0x80, 0x00, 0x00, 0x00, 0x11, startSessionResponse.sessionId1,
                                   startSessionResponse.sessionId2, 0x00, int(self.__sequence_number), 0x00])
          bytesToSend += bytearray(command)
          bytesToSend += bytearray([int(zoneId), 0x00])
          bytesToSend += bytearray([int(MilightWifiBridge.__calculateCheckSum(bytearray(command), int(zoneId)))])

          # Send request frame
          logging.debug("Sending request with command '{}' with session ID 1 '{}', session ID 2 '{}' and sequence number '{}'"
                        .format(str(binascii.hexlify(command)), str(startSessionResponse.sessionId1),
                                str(startSessionResponse.sessionId2), str(self.__sequence_number)))
          self.__sock.sendto(bytesToSend, (self.__ip, self.__port))
          try:
            # Receive response frame
            data, addr = self.__sock.recvfrom(64)
            if len(data) == 8:
              if data[6] == self.__sequence_number:
                returnValue = True
                logging.debug("Received valid response for previously sent request")
              else:
                logging.warning("Invalid sequence number ack {} instead of {}".format(str(data[6]),
                                                                                      self.__sequence_number))
            else:
              logging.warning("Invalid response size {} instead of 8".format(str(len(data))))
          except socket.timeout:
            logging.warning("Timed out for response")
        else:
          logging.warning("Start session failed")
      else:
        logging.error("Invalid zone {} (must be between 0 and 4)".format(str(zoneId)))
    else:
      logging.error("Invalid command size {} instead of 9".format(str(len(bytearray(command)))))

    return returnValue


  ######################### PUBLIC FUNCTIONS #########################
  def turnOn(self, zoneId):
    """Request 'Light on' to a zone

    Keyword arguments:
      zoneId -- (int or MilightWifiBridge.eZone) Zone ID

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__ON_CMD, zoneId)
    logging.debug("Turn on zone {}: {}".format(str(zoneId), str(returnValue)))
    return returnValue

  def turnOff(self, zoneId):
    """Request 'Light off' to a zone

    Keyword arguments:
      zoneId -- (int or MilightWifiBridge.eZone) Zone ID

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__OFF_CMD, zoneId)
    logging.debug("Turn off zone {}: {}".format(str(zoneId), str(returnValue)))
    return returnValue

  def turnOnWifiBridgeLamp(self):
    """Request 'Wifi bridge lamp on' to a zone

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__WIFI_BRIDGE_LAMP_ON_CMD, 0x01)
    logging.debug("Turn on wifi bridge lamp: {}".format(str(returnValue)))
    return returnValue

  def turnOffWifiBridgeLamp(self):
    """Request 'Wifi bridge lamp off'

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__WIFI_BRIDGE_LAMP_OFF_CMD, 0x01)
    logging.debug("Turn off wifi bridge lamp: {}".format(str(returnValue)))
    return returnValue

  def setNightMode(self, zoneId):
    """Request 'Night mode' to a zone

    Keyword arguments:
      zoneId -- (int or MilightWifiBridge.eZone) Zone ID

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__NIGHT_MODE_CMD, zoneId)
    logging.debug("Set night mode to zone {}: {}".format(str(zoneId), str(returnValue)))
    return returnValue

  def setWhiteMode(self, zoneId):
    """Request 'White mode' to a zone

    Keyword arguments:
      zoneId -- (int or MilightWifiBridge.eZone) Zone ID

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__WHITE_MODE_CMD, zoneId)
    logging.debug("Set white mode to zone {}: {}".format(str(zoneId), str(returnValue)))
    return returnValue

  def setWhiteModeBridgeLamp(self):
    """Request 'White mode' to the bridge lamp

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__WIFI_BRIDGE_LAMP_WHITE_MODE_CMD, 0x01)
    logging.debug("Set white mode to wifi bridge: {}".format(str(returnValue)))
    return returnValue

  def setDiscoMode(self, discoMode, zoneId):
    """Request 'Set disco mode' to a zone

    Keyword arguments:
      discoMode -- (int or MilightWifiBridge.eDiscoMode) Disco mode (9 modes available)
      zoneId -- (int or MilightWifiBridge.eZone) Zone ID

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__getSetDiscoModeCmd(discoMode), zoneId)
    logging.debug("Set disco mode {} to zone {}: {}".format(str(discoMode), str(zoneId), str(returnValue)))
    return returnValue

  def setDiscoModeBridgeLamp(self, discoMode):
    """Request 'Set disco mode' to the bridge lamp

    Keyword arguments:
      discoMode -- (int or MilightWifiBridge.eDiscoMode) Disco mode (9 modes available)

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__getSetDiscoModeForBridgeLampCmd(discoMode), 0x01)
    logging.debug("Set disco mode {} to wifi bridge: {}".format(str(discoMode), str(returnValue)))
    return returnValue

  def speedUpDiscoMode(self, zoneId):
    """Request 'Disco mode speed up' to a zone

    Keyword arguments:
      zoneId -- (int or MilightWifiBridge.eZone) Zone ID

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__DISCO_MODE_SPEED_UP_CMD, zoneId)
    logging.debug("Speed up disco mode to zone {}: {}".format(str(zoneId), str(returnValue)))
    return returnValue

  def speedUpDiscoModeBridgeLamp(self):
    """Request 'Disco mode speed up' to the wifi bridge

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__WIFI_BRIDGE_LAMP_DISCO_MODE_SPEED_UP_CMD, 0x01)
    logging.debug("Speed up disco mode to wifi bridge: {}".format(str(returnValue)))
    return returnValue

  def slowDownDiscoMode(self, zoneId):
    """Request 'Disco mode slow down' to a zone

    Keyword arguments:
      zoneId -- (int or MilightWifiBridge.eZone) Zone ID

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__DISCO_MODE_SLOW_DOWN_CMD, zoneId)
    logging.debug("Slow down disco mode to zone {}: {}".format(str(zoneId), str(returnValue)))
    return returnValue

  def slowDownDiscoModeBridgeLamp(self):
    """Request 'Disco mode slow down' to wifi bridge

    Keyword arguments:
      zoneId -- (int or MilightWifiBridge.eZone) Zone ID

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__WIFI_BRIDGE_LAMP_DISCO_MODE_SLOW_DOWN_CMD, 0x01)
    logging.debug("Slow down disco mode to wifi bridge: {}".format(str(returnValue)))
    return returnValue

  def link(self, zoneId):
    """Request 'Link' to a zone

    Keyword arguments:
      zoneId -- (int or MilightWifiBridge.eZone) Zone ID

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__LINK_CMD, zoneId)
    logging.debug("Link zone {}: {}".format(str(zoneId), str(returnValue)))
    return returnValue

  def unlink(self, zoneId):
    """Request 'Unlink' to a zone

    Keyword arguments:
      zoneId -- (int or MilightWifiBridge.eZone) Zone ID

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__UNLINK_CMD, zoneId)
    logging.debug("Unlink zone {}: {}".format(str(zoneId), str(returnValue)))
    return returnValue

  def setColor(self, color, zoneId):
    """Request 'Set color' to a zone

    Keyword arguments:
      color -- (int) Color (between 0x00 and 0xFF)
                     examples: 0xFF = Red, 0xD9 = Lavender, 0xBA = Blue, 0x85 = Aqua,
                               0x7A = Green, 0x54 = Lime, 0x3B = Yellow, 0x1E = Orange
      zoneId -- (int or MilightWifiBridge.eZone) Zone ID

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__getSetColorCmd(color), zoneId)
    logging.debug("Set color {} to zone {}: {}".format(str(color), str(zoneId), str(returnValue)))
    return returnValue

  def setColorBridgeLamp(self, color):
    """Request 'Set color' to wifi bridge

    Keyword arguments:
      color -- (int) Color (between 0x00 and 0xFF)
                     examples: 0xFF = Red, 0xD9 = Lavender, 0xBA = Blue, 0x85 = Aqua,
                               0x7A = Green, 0x54 = Lime, 0x3B = Yellow, 0x1E = Orange

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__getSetBridgeLampColorCmd(color), 0x01)
    logging.debug("Set color {} to wifi bridge: {}".format(str(color), str(returnValue)))
    return returnValue

  def setBrightness(self, brightness, zoneId):
    """Request 'Set brightness' to a zone

    Keyword arguments:
      brightness -- (int) Brightness in percentage (between 0 and 100)
      zoneId -- (int or MilightWifiBridge.eZone) Zone ID

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__getSetBrightnessCmd(brightness), zoneId)
    logging.debug("Set brightness {}% to zone {}: {}".format(str(brightness), str(zoneId), str(returnValue)))
    return returnValue

  def setBrightnessBridgeLamp(self, brightness):
    """Request 'Set brightness' to the wifi bridge

    Keyword arguments:
      brightness -- (int) Brightness in percentage (between 0 and 100)

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__getSetBrightnessForBridgeLampCmd(brightness), 0x01)
    logging.debug("Set brightness {}% to the wifi bridge: {}".format(str(brightness), str(returnValue)))
    return returnValue

  def setSaturation(self, saturation, zoneId):
    """Request 'Set saturation' to a zone

    Keyword arguments:
      brightness -- (int) Saturation in percentage (between 0 and 100)
      zoneId -- (int or MilightWifiBridge.eZone) Zone ID

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__getSetSaturationCmd(saturation), zoneId)
    logging.debug("Set saturation {}% to zone {}: {}".format(str(saturation), str(zoneId), str(returnValue)))
    return returnValue

  def setTemperature(self, temperature, zoneId):
    """Request 'Set temperature' to a zone

    Keyword arguments:
      brightness -- (int or MilightWifiBridge.eTemperature) Temperature in percentage (between 0 and 100)
      zoneId -- (int or MilightWifiBridge.eZone) Zone ID

    return: (bool) Request received by the wifi bridge
    """
    returnValue = self.__sendRequest(MilightWifiBridge.__getSetTemperatureCmd(temperature), zoneId)
    logging.debug("Set temperature {}% ({} kelvin) to zone {}: {}"
                  .format(str(temperature), str(int(2700 + 38*temperature)), str(zoneId), str(returnValue)))
    return returnValue

  def getMacAddress(self):
    """Request the MAC address of the milight wifi bridge

    return: (string) MAC address of the wifi bridge (empty if an error occured)
    """
    returnValue = self.__startSession().mac
    logging.debug("Get MAC address: {}".format(str(returnValue)))
    return returnValue


################################# HELP FUNCTION ################################
def __help(func="", filename=__file__):
  """Show help on how to use command line milight wifi bridge functions
  Keyword arguments:
    func -- (string, optional) Command line function requiring help, none will show all function
    filename -- (string, optional) File name of the python script implementing the commands
  """
  func = func.lower()

  # Help
  if func in ("h", "help"):
    print("Give information to use all or specific milight wifi bridge commands\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" -h [command (default: none)]\r\n"
          +filename+" --help [command (default: none)]\r\n"
          +"\r\n"
          +"Example:\r\n"
          +filename+" -h \r\n"
          +filename+" -h turnOn \r\n"
          +filename+" --help \r\n"
          +filename+" --help link")
    return
  elif func == "":
    print("HELP (-h, --help): Give information to use all or specific milight wifi bridge commands")

  # Ip
  if func in ("i", "ip"):
    print("Specify milight wifi bridge IP (mandatory to use any command)\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" -i [ip]\r\n"
          +filename+" --ip [ip]\r\n"
          +"\r\n"
          +"Example:\r\n"
          +filename+" -i 192.168.1.23\r\n"
          +filename+" --ip 192.168.1.23\r\n")
    return
  elif func == "":
    print("IP (-i, --ip): Specify milight wifi bridge IP (mandatory to use any command)")

  # Port
  if func in ("p", "port"):
    print("Specify milight wifi bridge port\r\n"
          +"\r\n"
          +"Default value (if not called): 5987\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" -port [port]\r\n"
          +filename+" --port [port]\r\n"
          +"\r\n"
          +"Example:\r\n"
          +filename+" -p 1234\r\n"
          +filename+" --port 1234\r\n")
    return
  elif func == "":
    print("PORT (-p, --port): Specify milight wifi bridge port (default value: 5987)")

  # Timeout
  if func in ("t", "timeout"):
    print("Specify timeout for communication with the wifi bridge (in sec)\r\n"
          +"\r\n"
          +"Default value (if not called): 5.0\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" -t [timeout]\r\n"
          +filename+" --timeout [timeout]\r\n"
          +"\r\n"
          +"Example:\r\n"
          +filename+" -t 1\r\n"
          +filename+" --timeout 1\r\n")
    return
  elif func == "":
    print("TIMEOUT (-t, --timeout): Specify timeout for communication with the wifi bridge in sec (default value: 5.0sec)")

  # Zone
  if func in ("z", "zone"):
    print("Specify milight light zone to control\r\n"
          +"\r\n"
          +"Default value (if not called): 0\r\n"
          +"\r\n"
          +"Possible values: 0 for all zone or zone 1 to 4\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" -z [zone]\r\n"
          +filename+" --zone [zone]\r\n"
          +"\r\n"
          +"Example:\r\n"
          +filename+" -z 1\r\n"
          +filename+" --zone 1\r\n")
    return
  elif func == "":
    print("ZONE (-z, --zone): Specify milight light zone to control (default value: All zone)")

  # Get MAC address
  if func in ("m", "getmacaddress"):
    print("Get the milight wifi bridge mac address\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 -m\r\n"
          +filename+" --ip 192.168.1.23 --getMacAddress\r\n")
    return
  elif func == "":
    print("GET MAC ADDRESS (-m, --getMacAddress): Get the milight wifi bridge mac address")

  # Link
  if func in ("l", "link"):
    print("Link lights to a specific zone\r\n"
          +"\r\n"
          +"Note: In order to make this work, the light must be switch on manually max 3sec before this command\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 -l\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 --link\r\n")
    return
  elif func == "":
    print("LINK (-l, --link): Link lights to a specific zone")

  # Unlink
  if func in ("u", "unlink"):
    print("Unlink lights\r\n"
          +"\r\n"
          +"Note: In order to make this work, the light must be switch on manually max 3sec before this command\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 -u\r\n"
          +filename+" --ip 192.168.1.23 --unlink\r\n")
    return
  elif func == "":
    print("UNLINK (-u, --unlink): Unlink lights")

  # Turn lights ON
  if func in ("o", "turnon"):
    print("Turn lights on\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 -o\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 --turnOn\r\n")
    return
  elif func == "":
    print("TURN ON (-o, --turnOn): Turn lights on")

  # Turn lights OFF
  if func in ("f", "turnoff"):
    print("Turn lights off\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 -f\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 --turnOff\r\n")
    return
  elif func == "":
    print("TURN OFF (-o, --turnOff): Turn lights off")

  # Turn wifi bridge lamp ON
  if func in ("x", "turnonwifibridgelamp"):
    print("Turn wifi bridge lamp on\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 -x\r\n"
          +filename+" --ip 192.168.1.23 --turnOnWifiBridgeLamp\r\n")
    return
  elif func == "":
    print("TURN WIFI BRIDGE LAMP ON (-x, --turnOnWifiBridgeLamp): Turn wifi bridge lamp on")

  # Turn wifi bridge lamp OFF
  if func in ("y", "turnoffwifibridgelamp"):
    print("Turn wifi bridge lamp off\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 -y\r\n"
          +filename+" --ip 192.168.1.23 --turnOffWifiBridgeLamp\r\n")
    return
  elif func == "":
    print("TURN WIFI BRIDGE LAMP OFF (-y, --turnOffWifiBridgeLamp): Turn wifi bridge lamp off")

  # Set night mode
  if func in ("n", "setnightmode"):
    print("Set night mode\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 -n\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 --setNightMode\r\n")
    return
  elif func == "":
    print("SET NIGHT MODE (-n, --setNightMode): Set night mode")

  # Set white mode
  if func in ("w", "setwhitemode"):
    print("Set white mode\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 -w\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 --setWhiteMode\r\n")
    return
  elif func == "":
    print("SET WHITE MODE (-w, --setWhiteMode): Set white mode")

  # Set white mode for bridge lamp
  if func in ("j", "setwhitemodebridgelamp"):
    print("Set white mode\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 -j\r\n"
          +filename+" --ip 192.168.1.23 --setWhiteModeBridgeLamp\r\n")
    return
  elif func == "":
    print("SET WHITE MODE ON BRIDGE LAMP (-j, --setWhiteModeBridgeLamp): Set white mode on bridge lamp")

  # Speed up disco mode for bridge lamp
  if func in ("k", "speedupdiscomodebridgelamp"):
    print("Speed up disco mode for bridge lamp\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 -k\r\n"
          +filename+" --ip 192.168.1.23 --speedUpDiscoModeBridgeLamp\r\n")
    return
  elif func == "":
    print("SPEED UP DISCO MODE FOR BRIDGE LAMP (-k, --speedUpDiscoModeBridgeLamp): Speed up disco mode for bridge lamp")

  # Slow down disco mode for bridge lamp
  if func in ("q", "slowdowndiscomodebridgelamp"):
    print("Slow down disco mode for bridge lamp\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 -q\r\n"
          +filename+" --ip 192.168.1.23 --slowDownDiscoModeBridgeLamp\r\n")
    return
  elif func == "":
    print("SLOW DOWN DISCO MODE FOR BRIDGE LAMP (-q, --slowDownDiscoModeBridgeLamp): Slow down disco mode for bridge lamp")

  # Speed up disco mode
  if func in ("a", "speedupdiscomode"):
    print("Speed up disco mode\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 -a\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 --speedUpDiscoMode\r\n")
    return
  elif func == "":
    print("SPEED UP DISCO MODE (-a, --speedUpDiscoMode): Speed up disco mode")

  # Slow down disco mode
  if func in ("g", "slowdowndiscomode"):
    print("Slow down disco mode\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 -g\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 --slowDownDiscoMode\r\n")
    return
  elif func == "":
    print("SLOW DOWN DISCO MODE (-g, --slowDownDiscoMode): Slow down disco mode")

  # Set specific color
  if func in ("c", "setcolor"):
    print("Set specific color (between 0 and 255)\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 -c 255\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 --setColor 255\r\n")
    return
  elif func == "":
    print("SET COLOR (-c, --setColor): Set specific color (between 0 and 255)")

  # Set brightness
  if func in ("b", "setbrightness"):
    print("Set brightness (in %)\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 -b 50\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 --setBrightness 50\r\n")
    return
  elif func == "":
    print("SET BRIGHTNESS (-b, --setBrightness): Set brightness (in %)")

  # Set specific color for bridge lamp
  if func in ("r", "setcolorbridgelamp"):
    print("Set specific color for the bridge lamp (between 0 and 255)\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 -r 255\r\n"
          +filename+" --ip 192.168.1.23 --setColorBridgeLamp 255\r\n")
    return
  elif func == "":
    print("SET COLOR FOR THE BRIDGE LAMP (-r, --setColorBridgeLamp): Set specific color for the bridge lamp (between 0 and 255)")

  # Set brightness for bridge lamp
  if func in ("v", "setbrightnessbridgelamp"):
    print("Set brightness for the bridge lamp (in %)\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 -v 50\r\n"
          +filename+" --ip 192.168.1.23 --setBrightnessBridgeLamp 50\r\n")
    return
  elif func == "":
    print("SET BRIGHTNESS FOR THE BRIDGE LAMP (-v, --setBrightnessBridgeLamp): Set brightness for the bridge lamp(in %)")

  # Set saturation
  if func in ("s", "setsaturation"):
    print("Set saturation (in %)\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 -s 50\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 --setSaturation 50\r\n")
    return
  elif func == "":
    print("SET SATURATION (-s, --setSaturation): Set saturation (in %)")

  # Set temperature
  if func in ("s", "settemperature"):
    print("Set temperature (in %)\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 -e 50\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 --setTemperature 50\r\n")
    return
  elif func == "":
    print("SET TEMPERATURE (-e, --setTemperature): Set temperature (in %)")

  # Set disco mode
  if func in ("d", "setdiscomode"):
    print("Set disco mode (between 1 and 9)\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 -d 5\r\n"
          +filename+" --ip 192.168.1.23 --zone 1 --setDiscoMode 5\r\n")
    return
  elif func == "":
    print("SET DISCO MODE (-d, --setDiscoMode): Set disco mode (between 1 and 9)")

  # Set disco mode for bridge lamp
  if func in ("d", "setdiscomodebridgelamp"):
    print("Set disco mode for bridge lamp (between 1 and 9)\r\n"
          +"\r\n"
          +"Usage:\r\n"
          +filename+" --ip 192.168.1.23 -1 5\r\n"
          +filename+" --ip 192.168.1.23 --setDiscoModeBridgeLamp 5\r\n")
    return
  elif func == "":
    print("SET DISCO MODE FOR BRIDGE LAMP (-1, --setDiscoModeBridgeLamp): Set disco mode for bridge lamp (between 1 and 9)")


  # Add use case examples:
  if func == "":
    print("\r\n"
          +"Some examples (if ip '192.168.1.23', port is 5987):\r\n"
          +" - Get the mac address: "+filename+" --ip 192.168.1.23 --port 5987 --getMacAddress\r\n"
          +" - Set disco mode 5 in light zone 1: "+filename+" --ip 192.168.1.23 --port 5987 --zone 1 --setDiscoMode 5\r\n"
          +" - Light on zone 1: "+filename+" --ip 192.168.1.23 --port 5987 --zone 1 --lightOn\r\n"
          +" - Light off zone 1: "+filename+" --ip 192.168.1.23 --port 5987 --zone 1 --lightOff\r\n"
          +" - Light on and set with light in zone 1: "+filename+" --ip 192.168.1.23 --port 5987 --zone 1 --lightOn --setWhiteMode\r\n"
          +" - Light on all zone: "+filename+" --ip 192.168.1.23 --port 5987 --zone 0 --lightOn\r\n"
          +" - Light off all zone: "+filename+" --ip 192.168.1.23 --port 5987 --zone 0 --lightOff")


################################# MAIN FUNCTION ###############################
def main():
  """Shell Milight utility function"""

  # Set the log level (no log will be shown if "logging.CRITICAL" is used)
  logger = logging.getLogger()
  logger.setLevel(logging.CRITICAL) #Other parameters: logging.DEBUG, logging.WARNING, logging.ERROR

  ip = "" # No default IP, must be specified by the user
  port = 5987 # Default milight 3.0 port
  zone = 0 # By default, all zone are controlled
  timeout = 5.0 # By default, Wait maximum 5sec

  # Get options
  try:
    opts, args = getopt.getopt(sys.argv[1:], "i:p:t:z:hmluofxynwagc:b:s:e:d:jkqr:v:1:",
                               ["ip=", "port=", "timeout=", "zone=", "help",
                                "getMacAddress", "link", "unlink", "turnOn", "turnOff", "turnOnWifiBridgeLamp",
                                "turnOffWifiBridgeLamp", "setNightMode", "setWhiteMode", "speedUpDiscoMode", "slowDownDiscoMode",
                                "setColor=", "setBrightness=", "setSaturation=", "setTemperature=", "setDiscoMode=",
                                "setWhiteModeBridgeLamp", "speedUpDiscoModeBridgeLamp", "slowDownDiscoModeBridgeLamp",
                                "setColorBridgeLamp=", "setBrightnessBridgeLamp=", "setDiscoModeBridgeLamp="])
  except getopt.GetoptError as err:
    print("[ERROR] "+str(err))
    __help()
    sys.exit(1)

  # Show help (if requested)
  for o, a in opts:
    if o in ("-h", "--help"):
      if len(args) >= 1:
        __help(args[0])
      else:
        __help()
      sys.exit(0)

  # Get base parameters
  for o, a in opts:
    if o in ("-i", "--ip"):
      ip = str(a)
      continue
    if o in ("-p", "--port"):
      port = int(a)
      continue
    if o in ("-t", "--timeout"):
      timeout = int(a)
      continue
    if o in ("-z", "--zone"):
      zone = int(a)
      continue

  # Check base parameters
  if ip == "":
    print("[ERROR] You need to specify the ip...\r\n")
    __help("ip")
    sys.exit(1)

  if zone < 0 or zone > 4:
    print("[ERROR] You need to specify a valid zone ID (between 0 and 4)\r\n")
    __help("zone")
    sys.exit(1)

  if timeout <= 0:
    print("[ERROR] You need to specify a valid timeout (more than 0sec)\r\n")
    __help("timeout")
    sys.exit(1)

  if port <= 0:
    print("[ERROR] You need to specify a valid port (more than 0)\r\n")
    __help("port")
    sys.exit(1)

  # Show base parameters
  logging.debug("Ip: "+str(ip))
  logging.debug("Zone: "+str(zone))
  logging.debug("Timeout: "+str(timeout))
  logging.debug("Port: "+str(port))

  # Initialize Milight bridge
  milight = MilightWifiBridge()
  milight.close()
  is_init = milight.setup(ip, port, timeout)
  logging.debug("Milight bridge connection initialized with ip {}:{} : {}".format(ip, port, is_init))
  if (not is_init):
    print("[ERROR] Initialization failed, re-check the ip (and the port), use '-h' to get more information.")
    sys.exit(2)

  # Execute requested commands in the requested order
  returnValue = True
  atLeastOneRequestDone = False

  for o, a in opts:
    if o in ("-m", "--getMacAddress"):
      atLeastOneRequestDone = True
      macAddress = milight.getMacAddress()
      returnValue &= (macAddress != "")
      if macAddress != "":
        print(str(macAddress))
    elif o in ("-l", "--link"):
      atLeastOneRequestDone = True
      returnValue &= milight.link(zoneId=zone)
    elif o in ("-u", "--unlink"):
      atLeastOneRequestDone = True
      returnValue &= milight.unlink(zoneId=zone)
    elif o in ("-o", "--turnOn"):
      atLeastOneRequestDone = True
      returnValue &= milight.turnOn(zoneId=zone)
    elif o in ("-f", "--turnOff"):
      atLeastOneRequestDone = True
      returnValue &= milight.turnOff(zoneId=zone)
    elif o in ("-x", "--turnOnWifiBridgeLamp"):
      atLeastOneRequestDone = True
      returnValue &= milight.turnOnWifiBridgeLamp()
    elif o in ("-y", "--turnOffWifiBridgeLamp"):
      atLeastOneRequestDone = True
      returnValue &= milight.turnOffWifiBridgeLamp()
    elif o in ("-j", "--setWhiteModeBridgeLamp"):
      atLeastOneRequestDone = True
      returnValue &= milight.setWhiteModeBridgeLamp()
    elif o in ("-k", "--speedUpDiscoModeBridgeLamp"):
      atLeastOneRequestDone = True
      returnValue &= milight.speedUpDiscoModeBridgeLamp()
    elif o in ("-q", "--slowDownDiscoModeBridgeLamp"):
      atLeastOneRequestDone = True
      returnValue &= milight.slowDownDiscoModeBridgeLamp()
    elif o in ("-r", "--setColorBridgeLamp"):
      userColor = int(a)
      if userColor < 0 or userColor > 255:
        print("[ERROR] Color must be between 0 and 255")
        sys.exit(2)
      atLeastOneRequestDone = True
      returnValue &= milight.setColorBridgeLamp(color=userColor)
    elif o in ("-v", "--setBrightnessBridgeLamp"):
      userBrightness = int(a)
      if userBrightness < 0 or userBrightness > 100:
        print("[ERROR] Brightness must be between 0 and 100 (in %)")
        sys.exit(2)
      atLeastOneRequestDone = True
      returnValue &= milight.setBrightnessBridgeLamp(brightness=userBrightness)
    elif o in ("-1", "--setDiscoModeBridgeLamp"):
      mode = int(a)
      if mode < 1 or mode > 9:
        print("[ERROR] Disco mode must be between 1 and 9")
        sys.exit(2)
      atLeastOneRequestDone = True
      returnValue &= milight.setDiscoModeBridgeLamp(discoMode=mode)
    elif o in ("-n", "--setNightMode"):
      atLeastOneRequestDone = True
      returnValue &= milight.setNightMode(zoneId=zone)
    elif o in ("-w", "--setWhiteMode"):
      atLeastOneRequestDone = True
      returnValue &= milight.setWhiteMode(zoneId=zone)
    elif o in ("-a", "--speedUpDiscoMode"):
      atLeastOneRequestDone = True
      returnValue &= milight.speedUpDiscoMode(zoneId=zone)
    elif o in ("-g", "--slowDownDiscoMode"):
      atLeastOneRequestDone = True
      returnValue &= milight.slowDownDiscoMode(zoneId=zone)
    elif o in ("-d", "--setDiscoMode"):
      mode = int(a)
      if mode < 1 or mode > 9:
        print("[ERROR] Disco mode must be between 1 and 9")
        sys.exit(2)
      atLeastOneRequestDone = True
      returnValue &= milight.setDiscoMode(discoMode=mode, zoneId=zone)
    elif o in ("-c", "--setColor"):
      userColor = int(a)
      if userColor < 0 or userColor > 255:
        print("[ERROR] Color must be between 0 and 255")
        sys.exit(2)
      atLeastOneRequestDone = True
      returnValue &= milight.setColor(color=userColor, zoneId=zone)
    elif o in ("-b", "--setBrightness"):
      userBrightness = int(a)
      if userBrightness < 0 or userBrightness > 100:
        print("[ERROR] Brightness must be between 0 and 100 (in %)")
        sys.exit(2)
      atLeastOneRequestDone = True
      returnValue &= milight.setBrightness(brightness=userBrightness, zoneId=zone)
    elif o in ("-s", "--setSaturation"):
      userSaturation = int(a)
      if userSaturation < 0 or userSaturation > 100:
        print("[ERROR] Saturation must be between 0 and 100 (in %)")
        sys.exit(2)
      atLeastOneRequestDone = True
      returnValue &= milight.setSaturation(saturation=userSaturation, zoneId=zone)
    elif o in ("-e", "--setTemperature"):
      userTemperature = int(a)
      if userTemperature < 0 or userTemperature > 100:
        print("[ERROR] Temperature must be between 0 and 100 (in %)")
        sys.exit(2)
      atLeastOneRequestDone = True
      returnValue &= milight.setTemperature(temperature=userTemperature, zoneId=zone)

    # In case an error occured in any of the request, stop the program
    if not returnValue:
      break

  if not atLeastOneRequestDone:
    print("[ERROR] You must call one action, use '-h' to get more information.")
    sys.exit(1)
  if not returnValue:
    print("[ERROR] Request failed")
    sys.exit(1)

  if atLeastOneRequestDone and returnValue:
    sys.exit(0)

if __name__ == '__main__':
  main()
