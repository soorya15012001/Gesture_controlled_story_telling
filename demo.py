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

play = True
prevPlay = play

def gesture(image):
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    global prevPlay
    global play

    with mp_hands.Hands( min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        # if the hand is detected

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
            # get the landmark coordinates
                landmark_list = []
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    landmark_list.append((landmark.x, landmark.y, landmark.z))

                # check if all 5 fingertips are open
                # print("LANDMARK ", landmark_list[4][1], landmark_list[3][1], landmark_list[2][1],  landmark_list[1][1], (landmark_list[4][1] < landmark_list[3][1] < landmark_list[2][1] < landmark_list[1][1]))
                # print("LANDMARK ", landmark_list[8][1], landmark_list[7][1], landmark_list[6][1],  landmark_list[5][1],  (landmark_list[8][1] < landmark_list[7][1] < landmark_list[6][1] < landmark_list[5][1]) )
                # print("LANDMARK ", landmark_list[12][1], landmark_list[11][1], landmark_list[10][1],  landmark_list[9][1], (landmark_list[12][1] < landmark_list[11][1] < landmark_list[10][1] < landmark_list[9][1]))
                # print("LANDMARK ", landmark_list[16][1], landmark_list[15][1], landmark_list[14][1],  landmark_list[13][1], (landmark_list[16][1] < landmark_list[15][1] < landmark_list[14][1] < landmark_list[13][1]))
                # print("LANDMARK ", landmark_list[20][1], landmark_list[19][1], landmark_list[18][1],  landmark_list[17][1], (landmark_list[20][1] < landmark_list[19][1] < landmark_list[18][1] < landmark_list[17][1]))


                if (landmark_list[4][1] < landmark_list[3][1] < landmark_list[2][1] < landmark_list[1][1]) and \
                (landmark_list[8][1] < landmark_list[7][1] < landmark_list[6][1] < landmark_list[5][1]) and \
                (landmark_list[12][1] < landmark_list[11][1] < landmark_list[10][1] < landmark_list[9][1]) and \
                (landmark_list[16][1] < landmark_list[15][1] < landmark_list[14][1] < landmark_list[13][1]) and \
                (landmark_list[20][1] < landmark_list[19][1] < landmark_list[18][1] < landmark_list[17][1]):
                    play = True
                    # print("OPEN \n")
                    if(prevPlay != play):
                    # then send play
                        prevPlay = play
                        print(play)
                else:
                    # print("CLOSED \n")
                    play = False
                
                # sending play
                    if(prevPlay != play):
                        # then send play
                        print(play)
                        prevPlay = play
                        
                # draw the hand landmarks on the image
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        




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