#!/usr/bin/python
#
# 240120
# markus ekler
#
# example #3: 
#  - wake 
#  - assign node id to first daisy-chain member
#  - configure watchdog for extended mode and reset watchdog 
#  - enable all PCVM channels
#  - perform block voltage measurement and output result
#  - perform cvm and output results
#  - reset/send nodes to sleep
#

from tle9012dqu.registers import *
from tle9012dqu.control import *

import sys
import time


def BVM_measurement(isoUART,nodeid):
	ok,err = isoUART.writeRegister(nodeid,REG['MEAS_CTRL'],0x0e,0x21) # default values for BVM as of UserManual 3.3.2
	if not ok:
		print("ERR: writeRegister failed.")
	time.sleep(0.010) # wait for 10ms
	ok,data = isoUART.readRegister(nodeid,REG['BVM'])
	if not ok:
		print("ERR: readRegister failed.")
	else:
		bvm = data[1]*256+data[0]
		vbvm = (60.0*bvm)/0xffff
		print("BVM measurement %02x%02x = %.02fV"%(data[1],data[0],vbvm))

def PCVM_measurement(isoUART,nodeid):
	ok,err = isoUART.writeRegister(nodeid,REG['MEAS_CTRL'],0xe0,0x21) # default values for BVM as of UserManual 3.3.1
	if not ok:
		print("ERR: writeRegister failed.")
	time.sleep(0.020) # wait for 10ms
	for i in range(12):
		ok,data = isoUART.readRegister(nodeid,REG['PCVM_%i'%i])
		if not ok:
			print("ERR: readRegister failed.")
		else:
			pcvm = data[1]*256+data[0]
			vpcvm = (5.0*pcvm)/0xffff
			print("PCVM_%i measurement %02x%02x = %.02fV"%(i,data[1],data[0],vpcvm))

if __name__ == "__main__":
	# create isoUART instance
	isoUART = TLE9012DQU(prompt_serialport(baudrate=2000000))

	# wake daisy-chain
	isoUART.wake()

	# assign node id to first node
	ok,err = isoUART.assignNodeID(0x01)
	if not ok:
		print("register write access failed (errcode=%i)"%err)
	print("isoUART: node id assigned")
	time.sleep(0.1)

	# set WD_EXT in opmode (extended watchdog) and reset WD
	ok,err = isoUART.writeRegister(0x01,REG['OP_MODE'],0xc4,0x02)
	if not ok:
		print("ERR: OP_MODE register access failed")
	ok,err = isoUART.resetWDT(0x01,0x7f)
	if not ok:
		print("ERR: WD RESET failed")
	print("isoUART(1): WD set for extended mode & reset")

	# enable cell voltage measurement for all channels
	ok,err = isoUART.writeRegister(0x01,REG['PART_CONFIG'],0x0f,0xff)
	if not ok:
		print("ERR: part config write failed.")
	print("isoUART(1): PART_CONFIG - all channels enabled.")

	# perform measurement and display results
	BVM_measurement(isoUART,0x01)
	PCVM_measurement(isoUART,0x01)

	# send nodes to sleep
	isoUART.reset()
	print("isoUART(RESET): send chain to sleep.")

	# release isoUART (windows python workarround)
	if sys.platform == "win32": isoUART.ser.close()


