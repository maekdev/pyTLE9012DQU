# pyTLE9012DQU
python library to control one or multiple Infineon TLE9012DQU BMS ICs

## Table of Contents
- [Installation](#Installation)
- [Introduction](#Introduction)
- [Hardware](#Hardware)

## Installation
If your python environment includes setuptools, you can get the library with the following command:
```bash
python -m pip install “pyTLE9012DQU”
```
Or alternatively, you can just place the subfolder pyTLE9012DQU into your project’s source folder.

## Introduction
The library is using python-serial to connect to any serial port of your PC and enables you to control one or multiple Infineon BMS cell management devices (TLE9012DQU) in a chain.
Basic low-level functions are provided for bus handling (wake), device enumeration and register control.

In this way you can build and test applications with just a few lines of code while you have complete access to all device capabilities.
There are some examples of the basic functionality (see examples subfolder), but to give you an idea: here’s a short code snippet to read and display a device’s manufacturer and version id:

```python
from tle9012dqu.registers import *
from tle9012dqu.control import *

isoUART = TLE9012DQU(prompt_serialport(baudrate=2000000))
isoUART.wake() # wake the BMS IC
isoUART.assignNodeID(0x01) # assign addr to first BMS IC
err,data = isoUART.readICVID(0x01) # read 
print(“manufacturer: %02x\nversion_id: %02x”%(data[1],data[0]))
```

## Hardware
On your PC you’ll most likely connect to your hardware using a USB-to-Serial converter. 
I’ve tested the library with some common USB-to-Serial products, but it should work with any device on the market:
- FTDI FT2232H 
- CH340
- Cypress CY7
- BluePill with virtual serial ports firmware (e.g. bluepill-serial-monster)

If you have access to Infineon Evaluation Boards, then you should use the TLE9015DQU isoUART Transceiver Board in combination with one or multiple TLE9012DQU Sensing Boards as shown in the picture below. 
![SystemSetup1](https://raw.githubusercontent.com/maekdev/maekdev/main/media/pyTLE9012DQU/SystemSetup1.jpg)
The TLE9015DQU provides a galvanically isolated isoUART interface to communicate with your BMS ICs.
If you don’t have a transceiver board, then you can access the first TLE9012DQU in a chain directly with your USB-to-Serial-Device. TLE9012DQU evaluation boards are intended to be used as isolated chained devices; to enable direct UART connection two small hardware changes are necessary. Then you can setup a system as depicted below.
![SystemSetup2](https://raw.githubusercontent.com/maekdev/maekdev/main/media/pyTLE9012DQU/SystemSetup2.jpg)
*Attention: Be aware that if you connect real LiIon cells to your hardware with this setup, your cell pack minus connection is connected directly to your PC GND. 
This might cause damage to you or your property, if you don’t know what you’re doing. Better use the TLE9015DQU or consider learning proper safety measures in handling lithium ion cells and consider using an USB isolator.*

![USB_Isolator](https://raw.githubusercontent.com/maekdev/maekdev/main/media/pyTLE9012DQU/USB_Isolator.jpg)

Here’s some more detailed description of the Infineon Evaluation Boards: 

TLE9012DQU
![TLE9012DQU_Evalboard](https://raw.githubusercontent.com/maekdev/maekdev/main/media/pyTLE9012DQU/TLE9012DQU_evalboard.jpg)

TLE9015DQU
![TLE9015DQU_Evalboard](https://raw.githubusercontent.com/maekdev/maekdev/main/media/pyTLE9012DQU/TLE9015DQU_evalboard.jpg)

By the way, if you don’t want to buy the Infineon Evaluationboards, then you can also build your own TLE9012DQU board and a low-cost USB-to-isoUART converter based on a simple TLE9015DQU board + bluepill. Instructions and code can be found (soon here on this) repository.
