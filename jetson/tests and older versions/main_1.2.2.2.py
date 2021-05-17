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
from Speech import Speech
from threading import Thread
from playsound import playsound

def gstreamer_pipeline(
    capture_width=1920,
    capture_height=1080,
    display_width=820,
    display_height=616,
    framerate=30,
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

class intThread(Thread):
	new_found = [0, 0]
	founded = [False, False]
	integral = [0, 0]
	def __init__(self, founded):
		Thread.__init__(self)
		self.founded = founded
		self.daemon = True
	def run(self):
		while True:
			for i in range(0, 2):
				if self.founded[i]:
					self.integral[i] = 1
				else:
					if self.integral[i] > 0:
						self.integral[i] -= 0.1
				self.new_found[i] = self.integral[i] > 0
			time.sleep(0.063)

class camThread(Thread):
	cam_index = 0
	opt = 0
	is_headless = 0
	net = 0
	founded = 0
	time_of_lost = 0
	list_of_id = []
	def __init__(self, cam_index, opt, is_headless, net):
		Thread.__init__(self)
		self.cam_index = cam_index
		self.opt = opt
		self.is_headless = is_headless
		self.net = net
		self.daemon = True
	def run(self):
		if self.cam_index == 1:
			cap = cv2.VideoCapture(self.cam_index)
		else:
			cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
		# create video sources & outputs
		input = jetson.utils.videoSource(self.opt.input_URI, argv=sys.argv)
		output = jetson.utils.videoOutput(self.opt.output_URI, argv=sys.argv+self.is_headless)
		if cap.isOpened():
			while True:
				ret, frame = cap.read()
				ret, frame = cap.read()
				ret, frame = cap.read()
				frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
				cuda_frame = jetson.utils.cudaFromNumpy(frame_rgba)
				# detect objects in the image (with overlay)
				detections = self.net.Detect(cuda_frame, overlay=self.opt.overlay)

				for detection in detections:
					self.list_of_id.append(detection.ClassID)
				if 1 in self.list_of_id:
					self.founded = True
				else:
					self.founded = False
				self.list_of_id.clear()

				# render the image
				output.Render(cuda_frame)

				# update the title bar
				output.SetStatus("{:s} | Network {:.0f} FPS".format(self.opt.network, self.net.GetNetworkFPS()))

				# print out performance info
				#net.PrintProfilerTimes()

				# exit on input/output EOS
				if not output.IsStreaming():
					break
		else:
			print("Camera open failed")
		cap.release()
		cv2.destroyAllWindows()
			

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

	backward_cam = camThread(0, opt, is_headless, net)
	forward_cam = camThread(1, opt, is_headless, net)
	new_found = [backward_cam.founded, forward_cam.founded]
	int_thread = intThread(new_found)	
	backward_cam.start()
	forward_cam.start()
	int_thread.start()
	s = Com(ARDPath = "/dev/ttyUSB0", portSpeed = 2000000)
	speech = Speech()
	opened = False
	old_found = [False, False]
	exist = 0
	while True:
		int_thread.founded = [backward_cam.founded, forward_cam.founded]
		#Forward camera
		if int_thread.new_found[1] != old_found[1]:
			if not old_found[1]:
				print("Person founded by forward camera")
				if  not exist:
					exist = "forward"
			else:
				forward_cam.time_of_lost = time.time()
				print("Person losted on forward camera")
			old_found[1] = not old_found[1]

		#Backward camera
		if int_thread.new_found[0] != old_found[0]:
			if not old_found[0]:
				print("Person founded by backward camera")
				if not exist:
					exist = "backward"
			else:
				backward_cam.time_of_lost = time.time()
				print("Person losted on backward camera")
			old_found[0] = not old_found[0]

		#Open and close door if forward camera was 1-st
		if exist == "forward":
			#Open door
			if not opened:
				if old_found[1] and not old_found[0]:
					playsound('mp3/Open.mp3')
					if s.writeCmd(129):
						opened = True
				elif not old_found[1] and not old_found[0]:
					exist = 0
			#Close door
			else:
				if not old_found[1] and old_found[0]:
					if s.writeCmd(128):
						opened = False
				elif not old_found[1] and not old_found[0]:
					if time.time() - forward_cam.time_of_lost > 15:
						playsound('mp3/Close.mp3')
						if s.writeCmd(128):
							opened = False

		#Open and close door if backward camera was 1-st
		elif exist == "backward":
			#Open door
			if not opened:
				if old_found[0] and not old_found[1]:
					playsound('mp3/Bye.mp3')
					if s.writeCmd(129):
						opened = True
				elif not old_found[0] and not old_found[1]:
					exist = 0
			#Close door
			else:
				if not old_found[0] and old_found[1]:
					if s.writeCmd(128):
						opened = False
				elif not old_found[0] and not old_found[1]:
					if time.time() - backward_cam.time_of_lost > 15:
						playsound('mp3/Close.mp3')
						if s.writeCmd(128):
							opened = False

if __name__ == '__main__':
	main()

