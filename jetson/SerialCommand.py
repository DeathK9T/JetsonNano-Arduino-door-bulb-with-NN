import serial
import time
import sys
import struct

class Com:
	packOneByte = struct.Struct('>B').pack
	portSpeed = 0
	ARDCom = 0
	ARDPath = 0

	def __init__(self, ARDPath, portSpeed):
		self.portSpeed = portSpeed
		self.ARDPath = ARDPath
		self.ARDCom = serial.Serial(self.ARDPath, self.portSpeed, timeout = 1)
		if self.ARDCom.is_open:
			print("COM port is sucessfuly initialized")

	def writeBytes(self, *args):
		if len(args) == 1:
			if self.ARDCom.is_open:
				start = time.time()
				self.ARDCom.write(self.packOneByte(args[0]))
				end = time.time()
				print("It's took {:.4f}ms to write 1 byte variables".format((end-start)*1000))
			else:
				print("COM port can't be opened!")

	def readBytes(self, n):
		if self.ARDCom.is_open:
			start = time.time()
			resp = self.ARDCom.read(8*n)
			end = time.time()
			print("It's took {:.4f}ms to read {} bytes.\n".format((end-start)*1000, n))
			print("Read bytes are:\n")
			print(resp)
		else:
			print("COM port can't be opened!")

	def writeCmd(self,*args):
		if len(args) == 1:
			start = time.time()
			if self.ARDCom.is_open:
				self.ARDCom.write(self.packOneByte(args[0]))
			else:
				print("COM port can't be opened!")
			while not self.ARDCom.in_waiting:
				pass
			resp = self.ARDCom.read(8)
			if int(resp, 2) == (args[0]):
				print("Command sent and replied.")
				end = time.time()
				print("It's took {:.4f}ms to write and read 1 byte variables".format((end-start)*1000))
				return 1
			else:
				print("Invalid reply!")
				return 0
