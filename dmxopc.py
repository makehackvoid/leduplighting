#!/usr/bin/python
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Reads OSC messages and pushes them out an FTDI based DMX interface
# Copyright (c) 2015 Make Hack Void

from ftdi import *
import math
import time
import os
import SocketServer
import threading

buf = bytearray(513)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	allow_reuse_address = True

class Handler(SocketServer.BaseRequestHandler):
	def handle(self):
		while True:
			header = self.buffered_read(4)
			if not header:
				break
			channel = header[0]
			command = header[1]
			length = (header[2] << 8) | header[3]
			#print channel
			#print command
			#print length
			data = self.buffered_read(length)
			if not data:
				break

			if command == 0:
				if channel == 0:
					for i in range(8):
						buf[1+i*3:1+i*3+length] = data
				elif channel >= 1 and channel <= 8:
					buf[1+(channel-1)*3:1+(channel-1)*3+length] = data

	def buffered_read(self, length):
		data = bytearray(length)
		pos = 0
		eof = False
		while pos < length:
			bytes = self.request.recv(length - pos)
			if not bytes:
				eof = True
				break
			data[pos:pos+len(bytes)] = bytes
			pos = pos + len(bytes)
		if eof:
			return False
		return data

usleep = lambda x: time.sleep(x/1000000.0)

def start():
	# http://en.wikipedia.org/wiki/DMX512#Timing
	ftdi_set_line_property2(c, BITS_8, STOP_BIT_2, NONE, BREAK_ON)
	# min break
	usleep(100)
	ftdi_set_line_property2(c, BITS_8, STOP_BIT_2, NONE, BREAK_OFF)
	# min mab
	usleep(15)

def go(buf):
	start()
	ftdi_write_data(c,str(buf),len(buf))

#os.system("rmmod ftdi_sio")
#os.system("")

c = ftdi_context()
ftdi_init(c)
ftdi_usb_open(c,0x0403,0x6001)
ftdi_set_baudrate(c,250000)
ftdi_setflowctrl(c,SIO_DISABLE_FLOW_CTRL)
ftdi_setrts(c,0)
ftdi_set_line_property(c, BITS_8, STOP_BIT_2, NONE)


server = ThreadedTCPServer(("0.0.0.0", 5000), Handler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()

while True:
	#for i in range(8):
	#	for j in range(3):
	#		buf[1+j+i*3] = int(math.sin(
	#			time.time() + 
	#			(j*2*math.pi/3) + 
	#			2*math.pi*i/8
	#		)*128+127)
		#buf[1 + 0 + i*3] = 255
		#buf[1 + 1 + i*3] = 255
		#buf[1 + 2 + i*3] = 0
	go(buf)
	time.sleep(0.01)
