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
        self.setGeometry(100, 100, 1000, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.create_inputs()
        self.create_table()
        self.create_buttons()

        self.fetch_cameras()  # Fetch existing cameras to populate the table on startup
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

        self.event_dropdown.currentIndexChanged.connect(self.on_event_change)

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
        self.delete_button = QPushButton('Delete Camera')
        self.reconnect_button = QPushButton('Reconnect Camera')

        self.register_button.clicked.connect(self.register_camera)
        self.delete_button.clicked.connect(self.delete_camera)
        self.reconnect_button.clicked.connect(self.reconnect_camera)

        layout.addWidget(self.register_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.reconnect_button)

        self.layout.addLayout(layout)

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

    def fetch_cameras(self):
        conn = sqlite3.connect('cameras.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, rtsp_url, device_id, event_id FROM cameras')
        cameras = cursor.fetchall()
        self.table.setRowCount(0)  # Clear existing rows
        for row_number, row_data in enumerate(cameras):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        conn.close()

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
            self.camera_dropdown.addItem(camera['model'], camera['cameraId'])

    def on_event_change(self, index):
        if index >= 0:
            event = self.event_dropdown.itemData(index)
            self.update_cameras_dropdown(event['cameras'])

    def register_camera(self):
        rtsp_url = self.rtsp_url_entry.text()
        camera_id = self.camera_dropdown.currentData()
        event = self.event_dropdown.currentData()

        if not rtsp_url or not camera_id or not event:
            QMessageBox.warning(self, 'Missing Information', 'All fields are required!')
            return

        data = {
            "rtsp_url": rtsp_url,
            "device_id": camera_id,
            "event_id": event['eventId']
        }

        try:
            response = requests.post("http://localhost:5000/register_camera", json=data)
            if response.status_code == 200:
                self.save_camera_to_db(rtsp_url, camera_id, event['eventId'])
                QMessageBox.information(self, 'Success', 'Camera registered successfully!')
                self.fetch_cameras()  # Refresh the table
        except requests.exceptions.RequestException as err:
            QMessageBox.warning(self, 'Error', str(err))

    def save_camera_to_db(self, rtsp_url, camera_id, event_id):
        conn = sqlite3.connect('cameras.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO cameras (rtsp_url, device_id, event_id) VALUES (?, ?, ?)',
                       (rtsp_url, camera_id, event_id))
        conn.commit()
        conn.close()

    def get_selected_camera_id(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'Error', 'No camera selected!')
            return None
        return self.table.item(selected_row, 0).text()  # Assuming ID is in the first column

    def edit_camera(self):
        camera_id = self.get_selected_camera_id()
        if not camera_id:
            return

        # Get current values to pre-fill the dialog (optional)
        conn = sqlite3.connect('cameras.db')
        cursor = conn.cursor()
        cursor.execute('SELECT rtsp_url, device_id, event_id FROM cameras WHERE id = ?', (camera_id,))
        camera = cursor.fetchone()
        conn.close()

        if not camera:
            QMessageBox.warning(self, 'Error', 'Failed to fetch camera details!')
            return

        # Open the edit dialog
        details = EditCameraDialog.get_new_camera_details(self)
        if details:
            conn = sqlite3.connect('cameras.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE cameras SET rtsp_url = ?, device_id = ?, event_id = ? WHERE id = ?',
                        (details['rtsp_url'], details['device_id'], details['event_id'], camera_id))
            conn.commit()
            conn.close()
            self.fetch_cameras()
            QMessageBox.information(self, 'Success', 'Camera updated successfully!')

    def delete_camera(self):
        camera_id = self.get_selected_camera_id()
        if not camera_id:
            return

        conn = sqlite3.connect('cameras.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cameras WHERE id = ?', (camera_id,))
        conn.commit()
        conn.close()
        self.fetch_cameras()
        QMessageBox.information(self, 'Success', 'Camera deleted successfully!')

    def reconnect_camera(self):
        camera_id = self.get_selected_camera_id()
        if not camera_id:
            return

        conn = sqlite3.connect('cameras.db')
        cursor = conn.cursor()
        cursor.execute('SELECT rtsp_url, device_id, event_id FROM cameras WHERE id = ?', (camera_id,))
        camera = cursor.fetchone()
        conn.close()

        if not camera:
            QMessageBox.warning(self, 'Error', 'Failed to fetch camera details!')
            return

        rtsp_url, device_id, event_id = camera
        data = {
            "rtsp_url": rtsp_url,
            "device_id": device_id,
            "event_id": event_id
        }

        try:
            response = requests.post("http://localhost:5000/register_camera", json=data)
            if response.status_code == 200:
                QMessageBox.information(self, 'Success', 'Camera reconnected successfully!')
            else:
                QMessageBox.warning(self, 'Error', 'Failed to reconnect camera!')
        except requests.exceptions.RequestException as err:
            QMessageBox.warning(self, 'Error', str(err))

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
