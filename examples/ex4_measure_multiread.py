#!/usr/bin/python
#
# 240201
# markus ekler
#
# example #4: 
#  - wake 
#  - assign node id to first daisy-chain member
#  - configure watchdog for extended mode and reset watchdog 
#  - enable all PCVM channels
#  - perform bvm and cvm
#  - configure and perform multiread for result registers and dsiplay results
#  - reset/send nodes to sleep
#

from tle9012dqu.registers import *
from tle9012dqu.control import *

import sys
import time

def _get_voltage(frame):
	# simple calculation function as aid for human readable display of results
	addr = frame[1]
	if addr == REG['BVM']:
		bvm = frame[2]*256+frame[3]
		return (60.0*bvm)/0xffff
	elif addr >= REG['PCVM_0'] and addr <= REG['PCVM_11']:
		pcvm = frame[2]*256+frame[3]
		return (5.0*pcvm)/0xffff
	return 0.0

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

	# perform measurement (bvm & pcvm)
	ok,err = isoUART.writeRegister(0x01,REG['MEAS_CTRL'],0xee,0x21) 
	if not ok:
		print("ERR: writeRegister failed.")
	time.sleep(0.010) # wait for 10ms
	print("isoUART(1): MEAS_CTRL measurement done.")
	
	# configure multiread
	ok,err = isoUART.writeRegister(0x01,REG['MULTI_READ_CFG'],0x00,0x1C)
	if not ok:
		print("ERR: writeRegister failed.")

	# perform multiread and display results
	ok,data = isoUART.readMultiread(0x01,13)
	if not ok:
		print("ERR: Multiread failed %i"%data)
	#print(data)
	for d1 in data:
		print("Node(%i): REG(%i) [%s] 0x%02x%02x (%.02fV)" % (d1[0],d1[1],ADDR2REGNAME(d1[1]),d1[3],d1[2],_get_voltage(d1)))

	# send nodes to sleep
	isoUART.reset()
	print("isoUART(RESET): send chain to sleep.")

	# release isoUART (windows python workarround)
	if sys.platform == "win32": isoUART.ser.close()

