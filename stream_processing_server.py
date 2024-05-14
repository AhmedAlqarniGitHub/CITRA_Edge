import logging
from flask import Flask, request
import threading
import queue
import cv2
import time
import requests
from datetime import datetime, timezone
import tempfile
import pytz

# Set up logging to ignore messages less severe than WARNING
logging.basicConfig(level=logging.WARNING)


app = Flask(__name__)
connection_queue = queue.Queue()

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


@app.route('/register_camera', methods=['POST'])
def register_camera_endpoint():
    data = request.json
    print(data)
    rtsp_url = data['rtsp_url']
    device_id = data['device_id']
    event_id = data['event_id']  
    connection_queue.put((rtsp_url, device_id, event_id))
    return {"message": "Camera registered successfully"}

@app.route('/start_processing', methods=['POST'])
def start_processing_endpoint():
    data = request.json
    rtsp_url = data['rtsp_url']
    device_id = data['device_id']
    event_id = data['event_id']
    connection_queue.put((rtsp_url, device_id, event_id))
    return {"message": f"Started processing stream from device {device_id}"}

@app.route('/active_threads', methods=['GET'])
def active_threads():
    return {"active_threads": threading.active_count()}

def process_stream(rtsp_url, device_id, event_id):
    # Append the transport protocol to the RTSP URL
    rtsp_url_with_tcp = rtsp_url + "?rtsp_transport=tcp&timeout=3000"
    cap = cv2.VideoCapture(rtsp_url_with_tcp)
    if not cap.isOpened():
        print(f"Unable to open camera with URL {rtsp_url_with_tcp}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        time.sleep(2)
        detected_objects = detect_objects(frame)
        send_detection_results(detected_objects, device_id, event_id)

#rtsp://localhost:8554/mystream
def send_detection_results(objects, device_id, event_id):
    for object in objects:
        # Save the image to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_image:
            cv2.imwrite(temp_image.name, object)

            # Format the datetime to match JavaScript's `new Date()` output
            current_utc = datetime.now(timezone.utc)
            iso_format_with_milliseconds = current_utc.isoformat(timespec='milliseconds')

            # Prepare the data payload
            data = {
                "cameraId": device_id,
                "detectionTime": iso_format_with_milliseconds,
                "eventId": event_id,
            }
            print(data)
            
            # Prepare the file payload
            files = {'image': (temp_image.name, open(temp_image.name, 'rb'), 'image/jpeg')}

            # Send the POST request with data and file
            response = requests.post("https://emotion-detection-app-bw5vqucpuq-ww.a.run.app", data=data, files=files)
            print(response)

            temp_image.close()
            
def detect_objects(frame):
    # Convert the frame to grayscale (necessary for the Haarcascade classifier)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    croppedFaces = []
    # Loop over the detected faces
    for (x, y, w, h) in faces:
        # Crop the face from the frame
        cropped_face = frame[y:y+h, x:x+w]
        croppedFaces.append(cropped_face)
        
    return croppedFaces  

def camera_listener():
    while True:
        rtsp_url, device_id, event_id = connection_queue.get()
        thread = threading.Thread(target=process_stream, args=(rtsp_url, device_id, event_id))
        thread.start()

if __name__ == "__main__":
    listener_thread = threading.Thread(target=camera_listener)
    listener_thread.start()
    app.run(host='0.0.0.0', port=5000)
