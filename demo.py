# import the necessary packages
from imutils.video import VideoStream
import threading
import argparse
import time
import cv2
from flask import Flask, render_template
from flask_socketio import SocketIO
import mediapipe as mp
import numpy as np
import json
import base64



async_mode=None
outputFrame = None
lock = threading.Lock()
thread = None
app = Flask(__name__)
socketio = SocketIO(app)
play = True
prevPlay = play
prevXY = np.array([0.0,0.0])
XY = prevXY
unitVectorTranslate = None
unitVectorRotate = None
prevDistance = None
distance = prevDistance
toZoom = None

vs = VideoStream(src=0).start()
time.sleep(2.0)

@app.route("/")
def index():
    return render_template("index.html")


def gesture(image):
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    global prevPlay
    global play
    global XY
    global prevXY
    global unitVectorTranslate
    global unitVectorRotate
    global prevDistance
    global distance
    global toZoom

    with mp_hands.Hands( min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        # if the hand is detected

        if results.multi_hand_landmarks:

            left_hand_landmarks = []
            right_hand_landmarks = []

            for hand_landmarks, hand_type in zip(results.multi_hand_landmarks,results.multi_handedness):
            # get the landmark coordinates
                landmark_list = []
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    landmark_list.append((landmark.x, landmark.y, landmark.z))

                # add the landmark list to the appropriate hand list based on hand type
                if hand_type.classification[0].label == 'Left':
                    left_hand_landmarks = landmark_list
                elif hand_type.classification[0].label == 'Right':
                    right_hand_landmarks = landmark_list

                if len(left_hand_landmarks) == 0 and len(right_hand_landmarks) == 0:
                    prevDistance = None
                    distance = prevDistance
                    toZoom = None
                if len(left_hand_landmarks) != 0:
                    #ZOOM
                    if (left_hand_landmarks[8][1] < left_hand_landmarks[7][1] < left_hand_landmarks[6][1] < left_hand_landmarks[5][1]) and \
                            len(right_hand_landmarks) != 0 and \
                            (right_hand_landmarks[8][1] < right_hand_landmarks[7][1] < right_hand_landmarks[6][1] < right_hand_landmarks[5][1]) and \
                            not (right_hand_landmarks[12][1] < right_hand_landmarks[11][1] < right_hand_landmarks[10][1] < right_hand_landmarks[9][1]) and \
                            not (left_hand_landmarks[12][1] < left_hand_landmarks[11][1] < left_hand_landmarks[10][1] < left_hand_landmarks[9][1]):
                        distance = int((np.linalg.norm(np.array(left_hand_landmarks[8]) - np.array(right_hand_landmarks[8]))) * 30)
                        if prevDistance is None:
                            prevDistance = distance
                        else:
                            if (prevDistance < distance):
                                toZoom = "Zoom In"
                            elif (prevDistance > distance):
                                toZoom = "Zoom Out"
                            elif (prevDistance == distance):
                                toZoom = None
                            prevDistance = distance
                            

                    if ((left_hand_landmarks[4][1] < left_hand_landmarks[3][1] < left_hand_landmarks[2][1] < left_hand_landmarks[1][1]) and \
                            (left_hand_landmarks[8][1] < left_hand_landmarks[7][1] < left_hand_landmarks[6][1] < left_hand_landmarks[5][1]) and \
                            (left_hand_landmarks[12][1] < left_hand_landmarks[11][1] < left_hand_landmarks[10][1] < left_hand_landmarks[9][1]) and \
                            (left_hand_landmarks[16][1] < left_hand_landmarks[15][1] < left_hand_landmarks[14][1] < left_hand_landmarks[13][1]) and \
                            (left_hand_landmarks[20][1] < left_hand_landmarks[19][1] < left_hand_landmarks[18][1] < left_hand_landmarks[17][1])):
                        if len(right_hand_landmarks) != 0:
                            #ROTATION
                            if (right_hand_landmarks[8][1] < right_hand_landmarks[7][1] < right_hand_landmarks[6][1] < right_hand_landmarks[5][1]) and \
                            (right_hand_landmarks[12][1] < right_hand_landmarks[11][1] < right_hand_landmarks[10][1] < right_hand_landmarks[9][1]) and \
                                    not(right_hand_landmarks[16][1] < right_hand_landmarks[15][1] < right_hand_landmarks[14][1] < right_hand_landmarks[13][1]) :
                                #print("rotate")
                                XY = np.array([right_hand_landmarks[12][0],right_hand_landmarks[12][1]])
                                unitVectorRotate = list((XY-prevXY)/np.linalg.norm(XY-prevXY))
                                prevXY = XY
                                #print(unitVectorRotate)

                            #TRANSLATION
                            if (right_hand_landmarks[8][1] < right_hand_landmarks[7][1] < right_hand_landmarks[6][1] < right_hand_landmarks[5][1]) and \
                                not (right_hand_landmarks[12][1] < right_hand_landmarks[11][1] < right_hand_landmarks[10][1] < right_hand_landmarks[9][1]):
                                #print("translate")
                                XY = np.array([right_hand_landmarks[8][0],right_hand_landmarks[8][1]])
                                unitVectorTranslate = list((XY-prevXY)/np.linalg.norm(XY-prevXY))
                                prevXY = XY
                                #print(unitVectorTranslate)

                            #PLAY/PAUSE
                            if (right_hand_landmarks[4][1] < right_hand_landmarks[3][1] < right_hand_landmarks[2][1] < right_hand_landmarks[1][1]) and \
                            (right_hand_landmarks[8][1] < right_hand_landmarks[7][1] < right_hand_landmarks[6][1] < right_hand_landmarks[5][1]) and \
                            (right_hand_landmarks[12][1] < right_hand_landmarks[11][1] < right_hand_landmarks[10][1] < right_hand_landmarks[9][1]) and \
                            (right_hand_landmarks[16][1] < right_hand_landmarks[15][1] < right_hand_landmarks[14][1] < right_hand_landmarks[13][1]) and \
                            (right_hand_landmarks[20][1] < right_hand_landmarks[19][1] < right_hand_landmarks[18][1] < right_hand_landmarks[17][1]):
                                play = True
                                # print("OPEN \n")
                                #then send play
                                if(prevPlay != play):
                                    prevPlay = play
                                    print(play)

                            elif not(right_hand_landmarks[4][1] < right_hand_landmarks[3][1] < right_hand_landmarks[2][1] < right_hand_landmarks[1][1]) and \
                                    not(right_hand_landmarks[8][1] < right_hand_landmarks[7][1] < right_hand_landmarks[6][1] < right_hand_landmarks[5][1]) and \
                                   not (right_hand_landmarks[12][1] < right_hand_landmarks[11][1] < right_hand_landmarks[10][1] < right_hand_landmarks[9][1]) and \
                                   not (right_hand_landmarks[16][1] < right_hand_landmarks[15][1] < right_hand_landmarks[14][1] < right_hand_landmarks[13][1]) and \
                                   not (right_hand_landmarks[20][1] < right_hand_landmarks[19][1] < right_hand_landmarks[18][1] < right_hand_landmarks[17][1]):
                                # print("CLOSED \n")
                                    play = False

                                # sending play
                                    if(prevPlay != play):
                                        # then send play
                                        print(play)
                                        prevPlay = play


                # draw the hand landmarks on the image
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    api_packet = {"rotate": unitVectorRotate, "translate": unitVectorTranslate, "zoom": toZoom, "play": play}
    unitVectorTranslate = None
    unitVectorRotate = None
    toZoom = None
    print(api_packet)
    return image, api_packet


def detect_motion(frameCount):
    global vs, outputFrame, lock

    while True:
        image = vs.read()
        image,api_packet = gesture(image)

        with lock:
            outputFrame = image.copy()

        _, compressed = cv2.imencode(".jpg", outputFrame)
        outputFrameJPEG = base64.b64encode(compressed).decode('utf-8')
        socketio.emit('receive_dictionary', json.dumps(api_packet))
        socketio.sleep(0)
        socketio.emit('output_frame', outputFrameJPEG)
        socketio.sleep(0)


@socketio.on('connect')
def connect(frameCount):
     socketio.start_background_task(detect_motion, args["frame_count"])

if __name__ == '__main__':
    ap = argparse.ArgumentParser() 
    ap.add_argument("-i", "--ip", type=str, required=True, default="0.0.0.0",
        help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True, default="5500",
        help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
        help="# of frames used to construct the background model")
    args = vars(ap.parse_args())
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)

vs.stop()