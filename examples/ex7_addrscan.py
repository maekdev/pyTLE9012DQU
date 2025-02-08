#!/usr/bin/python
#
# 240120
# markus ekler
#
# example #7: perform addr scan and evaluate response
# best to call this with output pipe log
#

from tle9012dqu.registers import *
from tle9012dqu.control import *

import sys
import time

def __readRegister(_isoUART,nid,addr):
	# modified version of .control->readRegister to just output everything
	frame = request4(0x1e,(nid&0x3F),addr)
	_isoUART.ser.write(frame._data)
	resp = _isoUART.ser.read(4)

	errcode = 0

	if resp != frame._data:
		print("ERR(readRegister): Missing/corrupted echo")
		#return False,-1
		errcode |= 0x01
	resp = _isoUART.ser.read(5) # read response
	if resp == b'':
		print("ERR(readRegister): Missing reply")
		#return False,-2
		errcode |= 0x02
		return errcode,[0xFF,0xFF],resp
	resp = bytereverse(resp)
	if (resp[0] != nid) or (resp[1] != addr):
		print("ERR(readRegister): malformed preamble (%02x%02x) expecting (%02x%02x)"%(resp[0],resp[1],nid,addr))
		#return False,-3
		errcode |= 0x04
	if resp[4] != CRC_calc(resp[0:4]):
		print("ERR(readRegister): CRC checksum error (%02x) expecting (%02x)"%(resp[4],CRC_calc(resp[0:4])))
		#return False,-4
		errcode |= 0x08
	return errcode,[resp[3],resp[2]],resp

def __writeRegister(_isoUART,nid,addr,d1,d0):
		frame = request6(0x1e,0x80|(nid&0x3F),addr,d1,d0)
		_isoUART.ser.write(frame._data)
		resp = _isoUART.ser.read(6) # read echo

		errcode = 0

		if resp != frame._data:
			print("ERR(writeRegister): Missing/corrupted echo")
			errcode |= 0x01
		resp = _isoUART.ser.read(1) # read reply
		if resp == b'':
			print("ERR(writeRegister): Missing reply")
			errcode |= 0x02
		return errcode,resp[0]



def errcodestr(e):
	s = ""
	if e == 0: return "All ok. "
	if e & 0x01: s += "Missing echo. "
	if e & 0x02: s += "Missing/empty reply. "
	if e & 0x04: s += "Malformed preamble. "
	if e & 0x08: s += "CRC fault. "
	if e & 0x10: s += "GENDIAG set. "
	if e & 0x20: s += "addr error/non existing addr. "
	if e & 0x40: s += "access error/write on ro. "
	return s

def REG_readrange(isoUART,r,nodeid=0x01):
	# read all registers in r and output diagnostic info
	res = []
	for addr in r:
		#ok,data = isoUART.readRegister(nodeid,addr)

		# trial with local modified function
		errcode,data,raw = __readRegister(isoUART,nodeid,addr)
		time.sleep(0.001)

		s = ADDR2REGNAME(addr)
		if s == None: s = "n/a"
		print("ADDR=0x%02x : %02x %02x (%s)"%(addr,data[1],data[0],s))

		# append in result log
		res.append([addr,data[1],data[0],errcode,raw])
	
	# print result in CSV compatible format
	print("Summary\n=======")
	print("ADDR;DATA;ERRCODE;ERRSTR;RAWRETURN")
	for r1 in res:
		s = ""
		for r2 in r1[4]:
			s += "%02x"%r2
		print("%02x;%02x%02x;%i;%s;%s"%(r1[0],r1[1],r1[2],r1[3],errcodestr(r1[3]),s))
		
def REG_writerange(isoUART,r,nodeid=0x01):
	# write all registers in r with previously read register content and observe response frame
	res = []
	for addr in r:
		# clear GENDIAG before write attempt
		__writeRegister(isoUART,nodeid,REG['GEN_DIAG'],0x00,0x00)
		# read register content with local modified function
		errcode1,data,raw = __readRegister(isoUART,nodeid,addr)
		time.sleep(0.001)
		# write data into same register
		errcode2,resp = __writeRegister(isoUART,nodeid,addr,data[1],data[0])

		s = ADDR2REGNAME(addr)
		if s == None: s = "n/a"
		print("ADDR=0x%02x : %02x %02x (%s) resp=%02x"%(addr,data[1],data[0],s,resp))

		# small adder for errcode handling based on response format
		# bit5: access error (write to read only bitfield)
		# bit4: address error (non existing address)
		# bit3: status flag (GENDIAG bit set)
		if resp & 0x08: errcode2 |= 0x10
		if resp & 0x10: errcode2 |= 0x20
		if resp & 0x20: errcode2 |= 0x40


		# append in result log
		res.append([addr,data[1],data[0],errcode1,raw,errcode2,resp])
	
	# print result in CSV compatible format
	print("Summary\n=======")
	print("ADDR;DATA;ERRCODE1;ERRSTR1;RAWRETURN1;RESPONSE;ERRCODE2;ERRSTR2")
	for r1 in res:
		s = ""
		for r2 in r1[4]:
			s += "%02x"%r2
		print("%02x;%02x%02x;%i;%s;%s;%02x;%02x;%s"%(r1[0],r1[1],r1[2],r1[3],errcodestr(r1[3]),s,r1[6],r1[5],errcodestr(r1[5])))
	


if __name__ == "__main__":
	# test for command line argument
	argwrite = False
	if "--write" in sys.argv:
		argwrite = True
	elif"-w" in sys.argv:
		argwrite = True

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

	r = range(256)
	#r = range(0x5B,0x5F,1)
	#r = [0,1,2,3,4,5,0x5B,0x5C]

	if argwrite:
		# write range of addresses
		REG_writerange(isoUART,r)
	else:
		# read range of addresses	
		REG_readrange(isoUART,r)


	# send nodes to sleep
	isoUART.reset()
	print("isoUART(RESET): send chain to sleep.")

	# release isoUART (windows python workarround)
	if sys.platform == "win32": isoUART.ser.close()


