# tle9012dqu_ctrl.py
#
# 240104
# markus ekler
#
# low-level user interface 
#  - frame generation (request/reply)
#  - serial port handler
#  - basic functions (wake, wdt)
#

from tle9012dqu.registers import *

import serial
import serial.tools.list_ports as port_list

import logging
import time

def bitreverse(b):
    # short lsb-msb reversal function
    # works with uint8
    ret = 0
    for i in range(8):
        if b & (1<<i):
            ret |= (1<<(7-i))
    return ret

def bytereverse(d):
	ret = bytearray(d)
	for i in range(len(d)):
		ret[i] = bitreverse(d[i])
	return ret
    
def crc_poly(data, n, poly, crc=0, xor_out=0):
	# just for exemplary use: can be implemented with built in CRC lib
    g = 1 << n | poly
    for d in data:
        crc ^= d << (n - 8)
        for _ in range(8):
            crc <<= 1
            if crc & (1 << n):
                crc ^= g
    return crc ^ xor_out

def CRC_calc(msg):
    # calculates 8bit CRC of TLE9012DQU payload (crc_poly = 0x1D, initial value = 0xFF, final_xor = 0xFF)
    return crc_poly(msg,8,0x1D,0xFF,xor_out=0xFF)

class request6:
	# calculates CRC checksum and provides bit-reversed structure for serial submission
	# supports two call modes
	#   req = request(b'\x1E\x80\x36\x08\x01')
	# or
	#   req = request(0x1E,0x80,0x36,0x08,0x01)
	# CRC checksum will be calculated automatically
	def __init__(self,psync,pid,paddr,pd1,pd0,pcrc=None):
		self.data = bytearray(6)
		self._data = bytearray(6)
		if isinstance(psync,bytearray):
			self.data[0:5] = psync[0:5]
		else:
			self.data[0] = psync
			self.data[1] = pid
			self.data[2] = paddr
			self.data[3] = pd1
			self.data[4] = pd0
		self.data[5] = CRC_calc(self.data[0:5]) if (pcrc==None) else (pcrc)
		for i in range(6):
			self._data[i] = bitreverse(self.data[i])

class request4:
	# calculates CRC checksum and provides bit-reversed structure for serial submission
	def __init__(self,psync,pid,paddr,pcrc=None):
		self.data = bytearray(4)
		self._data = bytearray(4)
		if isinstance(psync,bytearray):
			self.data[0:3] = psync[0:3]
		else:
			self.data[0] = psync
			self.data[1] = pid
			self.data[2] = paddr
		self.data[3] = CRC_calc(self.data[0:3]) if (pcrc==None) else (pcrc)
		for i in range(4):
			self._data[i] = bitreverse(self.data[i])

class response:
	def __init__(self,pid,paddr,pd1,pd0,pcrc):
		self.data = bytearray(5)
		self._data = bytearray(5)
		if isinstance(pid,bytearray):
			self.data[0:5] = pid[0:5]
		else:
			self.data[0] = pid
			self.data[1] = paddr
			self.data[2] = pd1
			self.data[3] = pd0 
			self.data[4] = pcrc
		for i in range(5):
			self._data[i] = self.data[i]
			self.data[i] = bitreverse(self.data[i])
	
	def close(self):
		# release serial port --> seems to be needed for python running on windows operating systems
		self.ser.close()

	def getdata(self):
		return (self.data[2]<<8)|(self.data[1])

	def crccheck(self):	
		return (self.data[4] == CRC_calc(self.data[0:4]))

def prompt_serialport(baudrate=2000000):
	print("Available Serial Ports:")
	ports = list(port_list.comports())
	for p1 in ports:
		print(" %s [%s]"%(p1.device,p1.description))
	pname = input("Enter port descriptor [%s]: "%ports[-1].device)
	if pname == "": pname = ports[-1].device
	ret = serial.Serial(port=pname,baudrate=baudrate)
	print("Serial Port [%s] successfully opened @ %iBaud" % (pname,baudrate))
	return ret

class TLE9012DQU:
	# base class to control a single or chain of TLE9012DQU
	def __init__(self,ser,timeout=0.1,debug=False):
		if debug:
			logging.basicConfig(level=logging.DEBUG,format="%(levelname)s : %(message)s")
			#logging.basicConfig(filename="debug.log",level=logging.DEBUG,format="%(asctime)s - %(levelname)s - %(message)s")
		else:
			logging.basicConfig(level=logging.ERROR,format="%(levelname)s : %(message)s")

		self.ser = ser
		self.ser.timeout = timeout 
		self.timeout = timeout # default timeout to restore

	def wake(self):
		if self.ser.baudrate > 1000000:
			self.ser.write(b'\xcc\xcc\xcc\xcc') # little workarround for PRQ-572. not ideal but works 
			logging.info("isoUART(): WAKE (high baudrate)")
		else:
			self.ser.write(b'\x55\x55')
			logging.info("isoUART(): WAKE (low baudrate)")
		time.sleep(0.008) # wait 8ms
		self.ser.flushInput() # remove serial echo

	def writeRegister(self,nodeid,addr,d1,d0):
		frame = request6(0x1e,0x80|(nodeid&0x3F),addr,d1,d0)
		self.ser.write(frame._data)
		resp = self.ser.read(6) # read echo
		if resp != frame._data:
			logging.error("writeRegister(): Missing/corrupted echo")
			#print("ERR(writeRegister): Missing/corrupted echo")
			return False,-1
		resp = self.ser.read(1) # read reply
		if resp == b'':
			logging.error("writeRegister(): Missing reply")
			return False,-2
		logging.debug("writeRegister(%02x,%02x,%02x%02x) [%02x%02x%02x%02x%02x%02x] -> Resp: %02x"%(nodeid,addr,d1,d0,frame.data[0],frame.data[1],frame.data[2],frame.data[3],frame.data[4],frame.data[5],resp[0]))
		return True,resp[0]
	
	def readRegister(self,nodeid,addr):
		frame = request4(0x1e,(nodeid&0x3F),addr)
		self.ser.write(frame._data)
		resp = self.ser.read(4)

		if resp != frame._data:
			logging.error("readRegister(): Missing/corrupted echo")
			return False,-1
		resp = self.ser.read(5) # read response
		if resp == b'':
			logging.error("readRegister(): Missing reply")
			return False,-2
		resp = bytereverse(resp)
		if (resp[0] != nodeid) or (resp[1] != addr):
			logging.error("readRegister(): malformed preamble (%02x%02x) expecting (%02x%02x)"%(resp[0],resp[1],nodeid,addr))
			return False,-3
		if resp[4] != CRC_calc(resp[0:4]):
			logging.error("readRegister(): CRC checksum error.")
			return False,-4
		logging.debug("readRegister(%02x,%02x) [%02x%02x%02x%02x] -> %02x%02x%02x%02x%02x"%(nodeid,addr,frame.data[0],frame.data[1],frame.data[2],frame.data[3],resp[0],resp[1],resp[2],resp[3],resp[4]))
		return True,[resp[3],resp[2]]
	
	def readMultiread(self,nodeid,count,timeout=0.1):
		# TODO: timeout to be implemented
		# TODO: debug logging for complete frames
		frame = request4(0x1e,nodeid,0x31)
		self.ser.write(frame._data)
		resp = self.ser.read(4)

		if resp != frame._data:
			logging.error("readMultiread(): Missing/corrupted echo")
			return False,-1
		ret = []
		for i in range(count):
			resp = self.ser.read(5) # read response
			if resp == b'':
				logging.error("readMultiread(): Missing reply")
				return False,-2
			resp = bytereverse(resp)
			if resp[4] != CRC_calc(resp[0:4]):
				logging.error("readMultiread(): CRC checksum error.")
				return False,-3
			ret.append(resp)

		return True,ret

	def reset(self):
		# this will shutdown the whole chain; wait for 2s after cmd submission
		# broadcast write @REG[OP_MODE]=0xC404
		ok,err = self.writeRegister(0xBF,0x14,0xC4,0x04)
		if ok:
			time.sleep(0.1) # delay 100ms
			return True
		return False
		
	def assignNodeID(self,nodeid):
		# set node id: addr=0x00, REG['CONFIG']=0x36, val=0x0801
		ok,err = self.writeRegister(0x00,REG['CONFIG'],0x08,nodeid)
		return ok,err
	
	def readICVID(self,nodeid):
		ok,data = self.readRegister(nodeid,REG['ICVID'])
		return ok,data
	
	def readCUSTID(self,nodeid):
		ret = bytearray(4)
		ok,data = self.readRegister(nodeid,REG['CUST_ID_1'])
		if not ok:
			return ok,data
		ret[2:4] = data
		ok,data = self.readRegister(nodeid,REG['CUST_ID_0'])
		if not ok:
			return ok,data
		ret[0:2] = data
		return True,ret
	
	def resetWDT(self,nodeid,val):
		ok,data = self.writeRegister(nodeid,REG['WDOG_CNT'],0x00,val & 0x7F)
		return ok,data
