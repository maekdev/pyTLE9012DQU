#!/usr/bin/python
#
# 240517
# markus ekler
#
# example #6:
# automatic scan of isoUART chain + output
# 
#  - wake
#  - assign node ids until fail (-> get number of nodes)
#  - read UID of nodes (for identification)
#  - print summary
#

from tle9012dqu.registers import *
from tle9012dqu.control import *

import sys

if __name__ == "__main__":
	isoUART = TLE9012DQU(prompt_serialport(baudrate=2000000))

	isoUART.wake()

	nodes = 0
	ok = True
	while ok:
		ok,err = isoUART.assignNodeID(nodes+1)
		if ok: nodes += 1
	time.sleep(0.1)
	
	for i in range(nodes):
		ok,custid= isoUART.readCUSTID(i+1)
		if not ok:
			print("ERR: read cust id failed (errcode=%i)"%data)
		ok,icvid = isoUART.readICVID(i+1)
		print("isoUART(%i): VERSIONID=0x%02x MANUFACTID=0x%02x CUSTID=0x%02x%02x%02x%02x"%(i+1,icvid[0],icvid[1],custid[0],custid[1],custid[2],custid[3]))

	print("Detected (%i) nodes on isoUART daisy-chain."%nodes)

	# release isoUART (windows python workarround)
	if sys.platform == "win32": isoUART.ser.close()



