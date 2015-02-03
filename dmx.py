#!/usr/bin/python

import json
from ftdi import *
import math
import time

usleep = lambda x: time.sleep(x/1000000.0)

def start():
    ftdi_set_line_property2(c, BITS_8, STOP_BIT_2, NONE, BREAK_ON)
    usleep(100)
    ftdi_set_line_property2(c, BITS_8, STOP_BIT_2, NONE, BREAK_OFF)
    usleep(15)

def go(buf):
    start()
    ftdi_write_data(c,str(buf),len(buf))

print "Initialising FTDI device"

c = ftdi_context()
ftdi_init(c)
ftdi_usb_open(c,0x0403,0x6001)
ftdi_set_baudrate(c,250000)
ftdi_setflowctrl(c,SIO_DISABLE_FLOW_CTRL)
ftdi_setrts(c,0)
ftdi_set_line_property(c, BITS_8, STOP_BIT_2, NONE)

buf = bytearray(513)

last = None

while True:
	json_data = open("/opt/spaceprobe/controller/api.json")
	data = json.load(json_data)
	json_data.close();

	if data["open"] != last:
		last = data["open"]
		print "state changed to '%s'" % ("open" if last else "closed")
	
	if data["open"]:
		for i in range(8):
			for j in range(3):
				buf[1+j+i*3] = int(math.sin(
					time.time() + 
					(j*2*math.pi/3) + 
					2*math.pi*i/8
				)*128+127)
	else:
		for i in range(8*3):
			buf[i+1] = 0

	go(buf)
	time.sleep(0.01)


