#!/usr/bin/python
#
# 240120
# markus ekler
#
# example #2: 
#  - wake 
#  - assign node id to first daisy-chain member
#  - configure watchdog for extended mode and reset watchdog (this is a neat trick to keep the device alive for a long period without the need to permanently serve the watchdog)
#  - toggle gpios
#  - reset/send nodes to sleep
#

from tle9012dqu.registers import *
from tle9012dqu.control import *

import sys
import time

# very, very simple GPIOx/PWMx pin handler using global variable
class gpio:
	def __init__(self,isoUART):
		self.data = bytearray(b'\x00\x22') # default data enable 
		self.isoUART = isoUART

	def update(self):
		ok,err = self.isoUART.writeRegister(0x01,REG['GPIO'],self.data[1],self.data[0])
		return ok

	def PWM0(self,val):
		if val: self.data[1] |= 0x10
		else: self.data[1] &= 0xEF
		return self.update()
	
	def PWM1(self,val):
		if val: self.data[1] |= 0x01
		else: self.data[1] &= 0xFE
		return self.update()


if __name__ == "__main__":
	isoUART = TLE9012DQU(prompt_serialport(baudrate=2000000))

	isoUART.wake()

	ok,err = isoUART.assignNodeID(0x01)
	if not ok:
		print("register write access failed (errcode=%i)"%err)
	print("isoUART: node id assigned")
	time.sleep(0.1)

	# set WD_EXT in opmode (extended watchdog) and reset WD
	ok,err = isoUART.writeRegister(0x01,REG['OP_MODE'],0xc4,0x02)
	if not ok:
		print("set opp mode failed.")
	ok,err = isoUART.resetWDT(0x01,0x7f)
	if not ok:
		print("wd reset failed")

	print("Toggling GPIO(PWMx)")
	mygpio = gpio(isoUART)
	for i in range(5):
		mygpio.PWM0(1)
		time.sleep(1)
		mygpio.PWM0(0)
		time.sleep(1)

	# send nodes to sleep
	isoUART.reset()

	# release isoUART (windows python workarround)
	if sys.platform == "win32": isoUART.ser.close()
