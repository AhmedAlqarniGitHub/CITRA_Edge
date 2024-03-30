from flask import Flask, request, jsonify
import threading
import queue
import cv2
import time
import requests
import datetime
import tempfile
import sqlite3

app = Flask(__name__)
connection_queue = queue.Queue()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize the database
def init_db():
    with sqlite3.connect('cameras.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS cameras (
                id INTEGER PRIMARY KEY,
                rtsp_url TEXT NOT NULL,
                device_id TEXT NOT NULL,
                event_id TEXT NOT NULL
            )
        ''')
    print("Database Initialized")

@app.route('/cameras', methods=['GET', 'POST'])
def cameras():
    if request.method == 'POST':
        data = request.json
        with sqlite3.connect('cameras.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO cameras (rtsp_url, device_id, event_id) VALUES (?, ?, ?)', 
                           (data['rtsp_url'], data['device_id'], data['event_id']))
            conn.commit()
        connection_queue.put((data['rtsp_url'], data['device_id'], data['event_id']))
        return jsonify({'message': 'Camera added and processing started'}), 201

    if request.method == 'GET':
        with sqlite3.connect('cameras.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM cameras')
            cameras = cursor.fetchall()
        return jsonify(cameras)

@app.route('/active_threads', methods=['GET'])
def active_threads():
    return jsonify({"active_threads": threading.active_count()})

def process_stream(rtsp_url, device_id, event_id):
    rtsp_url_with_tcp = rtsp_url + "?rtsp_transport=tcp&timeout=3000"
    
    cap = cv2.VideoCapture(rtsp_url_with_tcp, cv2.CAP_FFMPEG)
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

def send_detection_results(objects, device_id, event_id):
    for object in objects:
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_image:
            cv2.imwrite(temp_image.name, object)
            
            data = {
                "cameraId": device_id,
                "detectionTime": datetime.datetime.now().isoformat(),
                "eventId": event_id,
            }
            files = {'image': (temp_image.name, open(temp_image.name, 'rb'), 'image/jpeg')}
            response = requests.post("https://emotion-detection-app-v3-bw5vqucpuq-ww.a.run.app", data=data, files=files)
            temp_image.close()
            
def detect_objects(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    return [frame[y:y+h, x:x+w] for (x, y, w, h) in faces]

def camera_listener():
    while True:
        rtsp_url, device_id, event_id = connection_queue.get()
        threading.Thread(target=process_stream, args=(rtsp_url, device_id, event_id)).start()

if __name__ == "__main__":
    init_db()
    threading.Thread(target=camera_listener, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5000)
