# Milight Wifi Bridge 3.0 Python library
[![PyPI version](https://badge.fury.io/py/MilightWifiBridge.svg)](https://badge.fury.io/py/MilightWifiBridge) [![Build Status](https://travis-ci.org/QuentinCG/Milight-Wifi-Bridge-3.0-Python-Library.svg?branch=master)](https://travis-ci.org/QuentinCG/Milight-Wifi-Bridge-3.0-Python-Library) [![codecov](https://codecov.io/gh/QuentinCG/Milight-Wifi-Bridge-3.0-Python-Library/branch/master/graph/badge.svg)](https://codecov.io/gh/QuentinCG/Milight-Wifi-Bridge-3.0-Python-Library) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/171affbf02ea46d891765c2d39c56ce2)](https://www.codacy.com/manual/QuentinCG/Milight-Wifi-Bridge-3.0-Python-Library?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=QuentinCG/Milight-Wifi-Bridge-3.0-Python-Library&amp;utm_campaign=Badge_Grade) [![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://github.com/QuentinCG/Milight-Wifi-Bridge-3.0-Python-Library/blob/master/LICENSE) [![Donate](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://paypal.me/QuentinCG)[![Downloads](https://static.pepy.tech/badge/MilightWifiBridge)](https://pepy.tech/project/MilightWifiBridge)[![Downloads](https://static.pepy.tech/badge/MilightWifiBridge/month)](https://pepy.tech/project/MilightWifiBridge)

## What is it

This python library is designed to be integrated in python or shell projects using any Milight 3.0 bulbs and wifi bridge (with protocol LimitlessLED Wifi Bridge v6.0).

It is multi-platform and compatible with python 2.7+ and 3+.

<img src="https://github.com/QuentinCG/Milight-Wifi-Bridge-3.0-Python-Library/raw/master/milight.jpg" width="800">

## Functionalities

Non-exhaustive list of MilightWifiBridge class functionalities:
- Link/Unlink lights
- Light on/off
- Wifi bridge light on/off
- Set night light mode
- Set white light mode (default light) (of lights and bridge light)
- Set color (of lights and bridge light)
- Set saturation
- Set brightness (of lights and bridge light)
- Set disco mode (9 available) (of lights and bridge light)
- Increase/Decrease disco mode speed (of lights and bridge light)
- Get Milight wifi bridge MAC address

Non-exhaustive list of shell commands:
- Link/Unlink lights
- Light on/off
- Wifi bridge light on/off
- Set night light mode
- Set white light mode (default light) (of lights and bridge light)
- Set color (of lights and bridge light)
- Set saturation
- Set brightness (of lights and bridge light)
- Set disco mode (9 available) (of lights and bridge light)
- Increase/Decrease disco mode speed (of lights and bridge light)
- Get Milight wifi bridge MAC address
- Help

## How to install (python script and shell)

- Connect your Milight 3.0 wifi bridge to your wifi network (install the android app and follow the instruction: <https://play.google.com/store/apps/details?id=com.irainxun.wifilight>)
- Get IP address and port of the wifi bridge (ip can be found from your internet box, default port is 5987)
- Be sure the PC is linked to your wifi bridge (light on the bulbs max 3sec before calling `python3 MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --link`)
- Load your shell or python script

Note:
- You can install this library as a package using `pip install MilightWifiBridge` (or `python setup.py install` command in root folder).
- You can launch unit-test using `python setup.py test` command in root folder.

## How to use in shell

```shell
# Note: You can combine multiple requests in one command if you want

# Get help
python3 MilightWifiBridge.py --help

# Link bulbs to a specific zone (light on the bulbs max 3sec before calling this command)
python3 MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --link

# Unlink bulbs to a specific zone (light on the bulbs max 3sec before calling this command)
python3 MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --unlink

# Turn lights ON
python3 MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --turnOn

# Turn lights OFF
python3 MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --turnOff

# Turn wifi bridge light ON
python3 MilightWifiBridge.py --ip 192.168.1.23 --turnOnWifiBridgeLamp

# Turn wifi bridge light OFF
python3 MilightWifiBridge.py --ip 192.168.1.23 --turnOffWifiBridgeLamp

# Set night mode
python3 MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --setNightMode

# Set white mode
python3 MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --setWhiteMode

# Set white mode of the bridge light
python3 MilightWifiBridge.py --ip 192.168.1.23 --setWhiteModeBridgeLamp

# Speed up disco mode
python3 MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --speedUpDiscoMode

# Slow down disco mode
python3 MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --slowDownDiscoMode

# Speed up disco mode of the bridge light
python3 MilightWifiBridge.py --ip 192.168.1.23 --speedUpDiscoModeBridgeLamp

# Slow down disco mode of the bridge light
python3 MilightWifiBridge.py --ip 192.168.1.23 --slowDownDiscoModeBridgeLamp

# Set specific color
python3 MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --setColor 255

# Set specific color of the bridge light
python3 MilightWifiBridge.py --ip 192.168.1.23 --setColorBridgeLamp 255

# Set brightness
python3 MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --setBrightness 50

# Set brightness of the bridge light
python3 MilightWifiBridge.py --ip 192.168.1.23 --setBrightnessBridgeLamp 50

# Set saturation
python3 MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --setSaturation 50

# Set temperature
python3 MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --setTemperature 50

# Set disco mode
python3 MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --setDiscoMode 5

# Set disco mode of the bridge light
python3 MilightWifiBridge.py --ip 192.168.1.23 --setDiscoModeBridgeLamp 5

# Combined commands: Turn ON ALL lights (zone 0) with white mode, a brightness of 50% and a saturation of 50%
python3 MilightWifiBridge.py --ip 192.168.1.23 --zone 0 --turnOn --setWhiteMode --setBrightness 50 --setSaturation 50
```

## How to use in python script

Example of python script using this library:

```python
import sys
from MilightWifiBridge import MilightWifiBridge

milight = MilightWifiBridge()
_ip = "192.168.1.23"
_port = 5987
_timeout = 5.0
_zoneId = 1 # 0 for all
_discoMode = 5
_color = 0xBA # Blue
_brightness = 50 # %
_saturation = 50 # %
_temperature = 50 # %

# Create a connection with the milight wifi bridge (mandatory step)
if not milight.setup(ip=_ip, port=_port, timeout_sec=_timeout):
  print("Setup error")
  sys.exit(2)

# Show MAC address
macAddress = milight.getMacAddress()
if macAddress != "":
  print("MAC address of the milight wifi bridge: {}".format(str(macAddress)))

# Link bulbs to a zone
print("Link bulbs to zone {}: {}".format(str(_zoneId), str(milight.link(zoneId=_zoneId))))

# Unlink bulbs
print("Unlink bulbs of zone {}: {}".format(str(_zoneId), str(milight.unlink(zoneId=_zoneId))))

# Turn on bulbs in specific zone
print("Turn on bulbs in zone {}: {}".format(str(_zoneId), str(milight.turnOn(zoneId=_zoneId))))

# Turn off bulbs in specific zone
print("Turn off bulbs in zone {}: {}".format(str(_zoneId), str(milight.turnOff(zoneId=_zoneId))))

# Turn on wifi bridge lamp
print("Turn on wifi bridge lamp: {}".format(str(milight.turnOnWifiBridgeLamp())))

# Turn off wifi bridge lamp
print("Turn off wifi bridge lamp: {}".format(str(milight.turnOffWifiBridgeLamp())))

# Set night mode in specific zone
print("Set night mode in zone {}: {}".format(str(_zoneId), str(milight.setNightMode(zoneId=_zoneId))))

# Set white mode in specific zone
print("Set white mode in zone {}: {}".format(str(_zoneId), str(milight.setWhiteMode(zoneId=_zoneId))))

# Set white mode for the bridge light
print("Set white mode for the bridge light: {}".format(str(milight.setWhiteModeBridgeLamp())))

# Set specific disco mode in specific zone
print("Set disco mode {} in zone {}: {}".format(str(_discoMode), str(_zoneId), str(milight.setDiscoMode(discoMode=_discoMode, zoneId=_zoneId))))

# Speed up disco mode in specific zone
print("Speed up disco mode in zone {}: {}".format(str(_zoneId), str(milight.speedUpDiscoMode(zoneId=_zoneId))))

# Slow down disco mode in specific zone
print("Slow down disco mode in zone {}: {}".format(str(_zoneId), str(milight.slowDownDiscoMode(zoneId=_zoneId))))

# Set specific disco mode for the bridge light
print("Set disco mode {} for the bridge light: {}".format(str(_discoMode), str(milight.setDiscoModeBridgeLamp(discoMode=_discoMode))))

# Speed up disco mode for the bridge light
print("Speed up disco mode for the bridge light: {}".format(str(milight.speedUpDiscoModeBridgeLamp())))

# Slow down disco mod for the bridge light
print("Slow down disco mode for the bridge light: {}".format(str(milight.slowDownDiscoModeBridgeLamp())))

# Set specific color in specific zone
print("Set color {} in zone {}: {}".format(str(_color), str(_zoneId), str(milight.setColor(color=_color, zoneId=_zoneId))))

# Set specific color for the bridge light
print("Set color {} for the bridge light: {}".format(str(_color), str(milight.setColorBridgeLamp(color=_color))))

# Set specific brightness in specific zone
print("Set brightness {} in zone {}: {}".format(str(_brightness), str(_zoneId), str(milight.setBrightness(brightness=_brightness, zoneId=_zoneId))))

# Set specific brightness for the bridge light
print("Set brightness {} for the bridge light: {}".format(str(_brightness), str(milight.setBrightnessBridgeLamp(brightness=_brightness))))

# Set specific saturation in specific zone
print("Set saturation {} in zone {}: {}".format(str(_saturation), str(_zoneId), str(milight.setSaturation(saturation=_saturation, zoneId=_zoneId))))

# Set specific temperature in specific zone
print("Set temperature {} in zone {}: {}".format(str(_temperature), str(_zoneId), str(milight.setTemperature(temperature=_temperature, zoneId=_zoneId))))

# At the end, close connection with the milight wifi bridge
milight.close()
```

## License

This project is under MIT license. This means you can use it as you want (just don't delete the library header).

## Contribute

If you want to add more examples or improve the library, just create a pull request with proper commit message and right wrapping.
