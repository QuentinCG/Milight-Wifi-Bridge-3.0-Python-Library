# Milight Wifi Bridge 3.0 Python library

## What is it?

This python library is designed to be integrated in python or shell projects using any Milight 3.0 bulbs and wifi bridge (with protocol LimitlessLED Wifi Bridge v6.0).

It is multi-platform and compatible with python 2.7+ and 3+.

<img src="milight.jpg" width="800">


## Functionalities

Non-exhaustive list of MilightWifiBridge class functionalities:
  - Link/Unlink lights
  - Light on/off
  - Wifi bridge lamp on/off
  - Night light on
  - Set color
  - Set saturation
  - Set brightness
  - Set disco mode (9 available)
  - Increase/Decrease disco mode speed
  - Get Milight wifi bridge MAC address

Non-exhaustive list of shell commands:
  - Link/Unlink lights
  - Light on/off
  - Wifi bridge lamp on/off
  - Night light on
  - Set color
  - Set saturation
  - Set brightness
  - Set disco mode (9 available)
  - Increase/Decrease disco mode speed
  - Get Milight wifi bridge MAC address
  - Help


## How to install (python script and shell)

  - Connect your Milight 3.0 wifi bridge to your wifi network (install the android app and follow the instruction: https://play.google.com/store/apps/details?id=com.irainxun.wifilight&hl=fr)
  - Get IP address and port of the wifi bridge (you can for example use this software to help you: http://www.limitlessled.com/download/LimitlessLEDv4.zip)
  - Load your shell or python script


## How to use in shell

```shell
# Note: You can combine multiple requests in one command if you want

# Get help
MilightWifiBridge.py --help

# Link bulbs to a specific zone (light on the bulbs max 3sec before calling this command)
MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --link

# Unlink bulbs to a specific zone (light on the bulbs max 3sec before calling this command)
MilightWifiBridge.py --ip 192.168.1.23 --unlink

# Turn lights ON
MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --turnOn

# Turn lights OFF
MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --turnOff

# Turn wifi bridge lamp ON
MilightWifiBridge.py --ip 192.168.1.23 --turnOnWifiBridgeLamp

# Turn wifi bridge lamp OFF
MilightWifiBridge.py --ip 192.168.1.23 --turnOffWifiBridgeLamp

# Set night mode
MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --setNightMode

# Set white mode
MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --setWhiteMode

# Speed up disco mode
MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --speedUpDiscoMode

# Slow down disco mode
MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --slowDownDiscoMode

# Set specific color
MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --setColor 255

# Set brightness
MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --setBrightness 50

# Set saturation
MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --setSaturation 50

# Set temperature
MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --setTemperature 50

# Set disco mode
MilightWifiBridge.py --ip 192.168.1.23 --zone 1 --setDiscoMode 5

# Combined commands: Turn ON ALL lights (zone 0) with white mode and a brightness of 50% and a saturation of 50%
MilightWifiBridge.py --ip 192.168.1.23 --zone 0 --turnOn --setWhiteMode --setBrightness 50 --setSaturation 50
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
print("Unlink bulbs: {}".format(str(milight.link(zoneId=_zoneId))))

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

# Set specific disco mode in specific zone
print("Set disco mode {} in zone {}: {}".format(str(_discoMode), str(_zoneId), str(milight.setDiscoMode(discoMode=_discoMode, zoneId=_zoneId))))

# Speed up disco mode in specific zone
print("Speed up disco mode in zone {}: {}".format(str(_zoneId), str(milight.speedUpDiscoMode(zoneId=_zoneId))))

# Slow down disco mode in specific zone
print("Slow down disco mode in zone {}: {}".format(str(_zoneId), str(milight.slowDownDiscoMode(zoneId=_zoneId))))

# Set specific color in specific zone
print("Set color {} in zone {}: {}".format(str(_color), str(_zoneId), str(milight.setColor(color=_color, zoneId=_zoneId))))

# Set specific brightness in specific zone
print("Set brightness {} in zone {}: {}".format(str(_brightness), str(_zoneId), str(milight.setBrightness(color=_brightness, zoneId=_zoneId))))

# Set specific saturation in specific zone
print("Set saturation {} in zone {}: {}".format(str(_saturation), str(_zoneId), str(milight.setSaturation(color=_saturation, zoneId=_zoneId))))

# Set specific temperature in specific zone
print("Set temperature {} in zone {}: {}".format(str(_temperature), str(_zoneId), str(milight.setTemperature(temperature=_temperature, zoneId=_zoneId))))

# At the end, close connection with the milight wifi bridge
milight.close()
```


## License

This project is under MIT license. This means you can use it as you want (just don't delete the library header).


## Contribute

If you want to add more examples or improve the library, just create a pull request with proper commit message and right wrapping.
