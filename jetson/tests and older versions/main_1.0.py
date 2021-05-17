#
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import jetson.inference
import jetson.utils
import base64
import argparse
import sys
import time
import cv2
import threading
import numpy as np
from PIL import Image
import io
from SerialCommand import Com
from threading import Thread

def gstreamer_pipeline(
    capture_width=1920,#3280
    capture_height=1080,#2464
    display_width=820,#820
    display_height=616,#616
    framerate=30,#21
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


'''class SendThread(Thread):
	s = Com(ARDPath = "/dev/ttyUSB0", portSpeed = 2000000)
	old_found = False
	new_found = False
	opened = False
	time_of_found = 0
	def __init__(self):
		Thread.__init__(self)
		#self.daemon = True
	def run(self):
		while True:
			if self.new_found != self.old_found:
				if not self.old_found:
					self.time_of_found = time.time()
					print("Person founded")
				else:
					print("Person losted")
				self.old_found = self.new_found
			self.new_found = False

			if not self.opened and self.old_found:
				if self.s.writeCmd(129):
					self.opened = True
				else:
					pass
			elif self.opened and not self.old_found:
				if(time.time()-self.time_of_found <10):
					pass
				else:
					if self.s.writeCmd(128):
						self.opened = False
					else:
						pass'''
			

def main():
# parse the command line
	parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
		                         formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage() +
		                         jetson.utils.videoSource.Usage() + jetson.utils.videoOutput.Usage() + jetson.utils.logUsage())

	parser.add_argument("input_URI", type=str, default="", nargs='?', help="URI of the input stream")
	parser.add_argument("output_URI", type=str, default="", nargs='?', help="URI of the output stream")
	parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
	parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are: 'box', 'labels', 'conf', 'none'")
	parser.add_argument("--threshold", type=float, default=0.9, help="minimum detection threshold to use") 

	is_headless = ["--headless"] if sys.argv[0].find('console.py') != -1 else [""]

	try:
		opt = parser.parse_known_args()[0]
	except:
		print("")
		parser.print_help()
		sys.exit(0)

	# load the object detection network
	net = jetson.inference.detectNet(opt.network, sys.argv, opt.threshold)

	cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)#"nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080,format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert !  appsink")
	#cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)


	# create video sources & outputs
	input = jetson.utils.videoSource(opt.input_URI, argv=sys.argv)
	output = jetson.utils.videoOutput(opt.output_URI, argv=sys.argv+is_headless)

	#send_thread = SendThread()
	#send_thread.start()

	# process frames until the user exits
	while True:
		# capture the next image
		#img = input.Capture()
		ret, frame = cap.read()
		ret, frame = cap.read()
		ret, frame = cap.read()
		frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
		cuda_frame = jetson.utils.cudaFromNumpy(frame_rgba)
		# detect objects in the image (with overlay)
		detections = net.Detect(cuda_frame, overlay=opt.overlay)

		# print the detections
		#print("detected {:d} objects in image".format(len(detections)))
			
		for detection in detections:
			print(detection)
			#if detection.ClassID == 1:
				#print('1')
				#send_thread.new_found = True
		
		# render the image
		output.Render(cuda_frame)

		# update the title bar
		output.SetStatus("{:s} | Network {:.0f} FPS".format(opt.network, net.GetNetworkFPS()))

		# print out performance info
		#net.PrintProfilerTimes()

		# exit on input/output EOS
		if not output.IsStreaming():
			break

if __name__ == '__main__':
	main()

