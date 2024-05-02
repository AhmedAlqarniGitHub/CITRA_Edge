import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt
import sqlite3

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_db()
        self.setWindowTitle('CITRA Event Manager')
        self.setGeometry(100, 100, 1000, 600)  # x, y, width, height

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.create_inputs()
        self.create_table()
        self.create_buttons()

        self.apply_stylesheet()
        self.show()

    def create_inputs(self):
        layout = QHBoxLayout()

        self.event_dropdown = QComboBox()
        self.camera_dropdown = QComboBox()
        self.rtsp_url_entry = QLineEdit()
        self.rtsp_url_entry.setPlaceholderText("Enter RTSP URL")
        fetch_button = QPushButton('Fetch Events and Cameras')
        fetch_button.clicked.connect(self.fetch_events_and_cameras)

        layout.addWidget(QLabel('Select Event:'))
        layout.addWidget(self.event_dropdown)
        layout.addWidget(QLabel('Select Camera:'))
        layout.addWidget(self.camera_dropdown)
        layout.addWidget(QLabel('RTSP URL:'))
        layout.addWidget(self.rtsp_url_entry)
        layout.addWidget(fetch_button)

        self.layout.addLayout(layout)

    def create_table(self):
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['ID', 'RTSP URL', 'Device ID', 'Event ID'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

    def create_buttons(self):
        layout = QHBoxLayout()
        self.register_button = QPushButton('Register Camera')
        self.edit_button = QPushButton('Edit Camera')
        self.delete_button = QPushButton('Delete Camera')
        self.reconnect_button = QPushButton('Reconnect Camera')

        self.register_button.clicked.connect(self.register_camera)
        self.edit_button.clicked.connect(self.edit_camera)
        self.delete_button.clicked.connect(self.delete_camera)
        self.reconnect_button.clicked.connect(self.reconnect_camera)

        layout.addWidget(self.register_button)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.reconnect_button)

        self.layout.addLayout(layout)
    
    # Initialize SQLite Database
    def init_db(self):
        conn = sqlite3.connect('cameras.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cameras (
                id INTEGER PRIMARY KEY,
                rtsp_url TEXT NOT NULL,
                device_id TEXT NOT NULL,
                event_id TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        
    def save_camera_to_db(self,rtsp_url, device_id, event_id):
        conn = sqlite3.connect('cameras.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO cameras (rtsp_url, device_id, event_id) VALUES (?, ?, ?)',
                    (rtsp_url, device_id, event_id))
        conn.commit()
        conn.close()
        
    def fetch_cameras():
        conn = sqlite3.connect('cameras.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, rtsp_url, device_id, event_id FROM cameras')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def fetch_events_and_cameras(self):
        response = requests.get("https://citra-api-qp4p25cifq-ww.a.run.app/events/events_with_cameras")
        if response.status_code == 200:
            events = response.json()
            self.event_dropdown.clear()
            for event in events:
                self.event_dropdown.addItem(event['name'], event)
            self.update_cameras_dropdown(events[0]['cameras'])

    def update_cameras_dropdown(self, cameras):
        self.camera_dropdown.clear()
        for camera in cameras:
            self.camera_dropdown.addItem(camera['model'], camera)

    def register_camera(self):
        rtsp_url = self.rtsp_url_entry.text()
        event_id = self.event_dropdown.currentData()
        device_id = self.camera_dropdown.currentData()

        if not rtsp_url or not event_id or not device_id:
            QMessageBox.warning(self, 'Missing Information', 'All fields are required!')
            return
        data = {
            "rtsp_url": rtsp_url,
            "device_id": device_id,
            "event_id": event_id
        }
        
        # Send POST request to the server
        try:
            response = requests.post("http://localhost:5000/register_camera", json=data)
            response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code

            if response.status_code == 200:
                self.save_camera_to_db(rtsp_url, device_id, event_id)
                QMessageBox.information(self, 'Success', 'Camera registered successfully!')
                # self.update_camera_table()
        except requests.exceptions.HTTPError as err:
            QMessageBox.warning("Error", f"HTTP error occurred: {err}")
        except requests.exceptions.RequestException as err:
            QMessageBox.warning("Error", f"Error occurred: {err}")
    

    def edit_camera(self):
        QMessageBox.information(self, 'Edit', 'Edit functionality goes here!')

    def delete_camera(self):
        QMessageBox.information(self, 'Delete', 'Delete functionality goes here!')

    def reconnect_camera(self):
        QMessageBox.information(self, 'Reconnect', 'Reconnect functionality goes here!')

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
                padding: 10px;
            }
            QComboBox, QLineEdit, QPushButton, QLabel, QTableWidget {
                min-height: 30px;
            }
            QPushButton {
                color: white;
                background-color: #007BFF;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QTableWidget {
                selection-background-color: #007BFF;
            }
        """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
