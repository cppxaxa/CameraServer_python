from ConfigurationProvider import *
import threading
import cv2
import time
import numpy as np

class NativeCameraPoller:
    def __init__(self, cameraCode):
        self.cameraCode = cameraCode
        self.loopBreak = False
        self.currFrame = None

        self.lock = threading.Lock()

    def init(self):
        self.cap = cv2.VideoCapture(self.cameraCode)

    def dispose(self):
        with self.lock:
            self.loopBreak = False
            self.cap.release()

    def getImage(self):
        with self.lock:
            return np.copy(self.currFrame)

    def pollLoop(self):
        while True:
            with self.lock:
                if self.loopBreak == False:
                    _, frame = self.cap.read()
                    self.currFrame = frame
    

class CameraPoller:
    def __init__(self, config):
        self.config = config

        if self.config['type'] == 'native':
            self.poller = NativeCameraPoller(config['cameraCode'])

        self.cameraInitialized = False
        self.imageArray = []

    def initCamera(self):
        self.poller.init()
        self.cameraInitialized = True

    def dispose(self):
        try:
            self.p._stop()
            self.poller.dispose()
        except:
            pass

    def start(self):
        if self.cameraInitialized == False:
            self.initCamera()

        self.p = threading.Thread(target=self.poller.pollLoop, args=(), daemon=True)
        self.p.start()

    def getImage(self):
        return self.poller.getImage()
    



from flask import Flask, jsonify, Response

app = Flask(__name__)

configList = ConfigurationProvider.getConfiguration('CameraConfig.txt')
webCamPollerList = []

for config in configList:
    webCamPoller = CameraPoller(config)
    webCamPoller.start()
    webCamPollerList.append(webCamPoller)

@app.route('/<string:id>', methods=['GET'])
def get(id):
    if id.endswith('.jpg'):
        id = id[0:-4]

    id = int(id)

    image = webCamPollerList[id].getImage()
    ret, encoded = cv2.imencode('.jpg', image)
    return Response(encoded.tobytes(), mimetype='image/jpg')

app.run(port=5001)