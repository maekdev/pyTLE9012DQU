#!/usr/bin/python
#
# 240106
# markus ekler
#
# example #1: wake, assign node id to first daisy-chain member, read IC identifier and unique ID
#

from tle9012dqu.registers import *
from tle9012dqu.control import *

import sys
import time

if __name__ == "__main__":
	isoUART = TLE9012DQU(prompt_serialport(baudrate=2000000),debug=True)

	isoUART.wake()

	ok,err = isoUART.assignNodeID(0x01)
	if not ok:
		print("ERR: register write access failed (errcode=%i)"%err)
	print("isoUART: node id assigned")
	time.sleep(0.1)

	ok,data = isoUART.readICVID(0x01)
	if not ok:
		print("ERR: read ic identifier failed (errcode=%i)"%err)
	print("isoUART(1): manufacturer 0x%02x / version_id 0x%02x"%(data[1],data[0])) 

	ok,data = isoUART.readCUSTID(0x01)
	if not ok:
		print("ERR: read cust id failed (errcode=%i)"%data)
	print("isoUART(1)/read cust id: [%02x%02x] [%02x%02x]"%(data[0],data[1],data[2],data[3]))

	isoUART.reset()
	print("isoUART: daisy-chain nodes reset")

	# release isoUART (windows python workarround)
	if sys.platform == "win32": isoUART.ser.close()



