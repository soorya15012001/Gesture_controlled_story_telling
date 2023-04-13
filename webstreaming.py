# import the necessary packages
from pyimagesearch.motion_detection.singlemotiondetector import SingleMotionDetector
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2

outputFrame = None
lock = threading.Lock()
app = Flask(__name__)
vs = VideoStream(src=0).start()
time.sleep(2.0)

@app.route("/")
def index():
	return render_template("index.html")



import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math
import numpy as np

def trendline(index,data, order=1):
    coeffs = np.polyfit(index, list(data), order)
    slope = coeffs[-2]
    return float(slope)

def gesture(image):
	mp_drawing = mp.solutions.drawing_utils
	mp_hands = mp.solutions.hands

	with mp_hands.Hands( min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
		image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
		image.flags.writeable = False
		results = hands.process(image)
		image.flags.writeable = True
		image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
		if results.multi_hand_landmarks:
			hand_landmarks = results.multi_hand_landmarks
			for hand_landmarks in results.multi_hand_landmarks:
				ppt = []
				li = []
				for landmrk in hand_landmarks.landmark:
					image_height, image_width, _ = image.shape
					cx, cy = int(landmrk.x * image_width), int(landmrk.y*image_height)
					ppt.append([cx, cy])
				for i in [ppt[4], ppt[8], ppt[12], ppt[16], ppt[20]]:
					image = cv2.circle(image, i, 5, (255,0, 0), -1)

					distance = int(math.dist(ppt[4], ppt[8]))
					if len(li) != 5:
						li.append(distance)
						print(li)
					
					elif len(li) == 5:
						resultent=trendline(range(len(li)), li)
						print(resultent)
						image = cv2.putText(image, str(resultent), (int((ppt[4][0]+ppt[8][0])/2), int((ppt[4][1]+ppt[8][1])/2)), cv2.FONT_HERSHEY_SIMPLEX, 1, [0, 255, 0], 5, cv2.LINE_AA)
						li = []


					image = cv2.line(image, ppt[4], ppt[8], [0, 255, 0], 5)


   




	return image

def detect_motion(frameCount):
	global vs, outputFrame, lock
	total = 0

	while True:
		image = vs.read()
		image = gesture(image)

		with lock:
			outputFrame = image.copy()



def generate():
	global outputFrame, lock
	while True:
		with lock:
			if outputFrame is None:
				continue
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			if not flag:
				continue
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True, default="0.0.0.0",
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=True, default="8000",
		help="ephemeral port number of the server (1024 to 65535)")
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	args = vars(ap.parse_args())
	t = threading.Thread(target=detect_motion, args=(
		args["frame_count"],))
	t.daemon = True
	t.start()
	app.run(host=args["ip"], port=args["port"], debug=True,
		threaded=True, use_reloader=False)
vs.stop()