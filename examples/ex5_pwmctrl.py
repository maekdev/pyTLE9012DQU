#!/usr/bin/python
#
# 240223
# markus ekler
#
# example #5: 
# pwm activation to evaluate duty cycle / pwm frequency options
# with simple terminal based user interface
#

from tle9012dqu.registers import *
from tle9012dqu.control import *

import sys
import time


# config options for duty cycles & pwm in human readable format
CFGSTR_duty = ["Duty=OFF"]
for i in range(1,0x1F+1):	
	CFGSTR_duty.append("Duty=%.02f%%"%(i*3.57))
CFGSTR_duty[0x1C] = "Duty=100%%"
CFGSTR_duty[0x1D] = "???"
CFGSTR_duty[0x1E] = "???"
CFGSTR_duty[0x1F] = "Duty=100_"

CFGSTR_freq = ["PWM=OFF"]
for i in range(1,0x1F+1):
	CFGSTR_freq.append("tPWM=%ius (%.02fkHZ)" % (2*i,1000.0/(2*i)))
# eof human readable config arrays


# main function
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
		print("ERR: OP_MODE register access failed")
	ok,err = isoUART.resetWDT(0x01,0x7f)
	if not ok:
		print("ERR: WD RESET failed")
	print("isoUART(1): WD set for extended mode & reset")

	# configure PWM0 for PWM mode 0x2A80 --> PWM_PWM0/1=1 & DIR_PWM0/1=1
	ok,err = isoUART.writeRegister(0x01,REG['GPIO'],0x2A,0x80)
	if not ok: 
		print("ERR: GPIO write register failed")
	print("isoUART(1): PWM0/1 configured")		
	
	# main loop with super simple cmd interface
	running = True
	lastcommand = "+"
	pos_duty = 5
	pos_freq = 5
	while running:		
		command = input("Choose from q=QUIT / F=freq+ / f=freq- / D=duty+ / d=duty- / <ENTER>=repeat : ")
		if command == "": command = lastcommand
		elif command == "q" or command == "Q":
			running = False
			break
		lastcommand = command
		# process command
		if command == "f": 
			if pos_freq < 0x1F: pos_freq += 1
		elif command == "F": 
			if pos_freq > 0: pos_freq -= 1
		elif command == "D": 
			if pos_duty < 0x1F: pos_duty += 1
		elif command == "d": 
			if pos_duty > 0: pos_duty -= 1
		
		# send command via isoUART		
		ok,err = isoUART.writeRegister(0x01,REG['GPIO_PWM'],pos_freq,pos_duty)
		if not ok:
			print("isoUART(1): ERR write register failed (%i)" % err)
		else:
			print(" - PWM CONFIG:")
			print("     PWM_PERIOD(%02x)     -> %s"%(pos_freq,CFGSTR_freq[pos_freq]))
			print("     PWM_DUTY_CYCLE(%02x) -> %s"%(pos_duty,CFGSTR_duty[pos_duty]))
			

	# send nodes to sleep
	isoUART.reset()

	# release isoUART (windows python workarround)
	if sys.platform == "win32": isoUART.ser.close()
	
	# end
	print("All done.")
