import tkinter as tk
from tkinter import messagebox, font, ttk
import requests
import sqlite3

# Initialize SQLite Database for Cameras
def init_camera_db():
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

# Register Camera
def register_camera(rtsp_url, device_id, event_id):
    # Replace with your server's URL
    server_url = "http://your_server_address/register_camera"
    data = {"rtsp_url": rtsp_url, "device_id": device_id, "event_id": event_id}
    try:
        response = requests.post(server_url, json=data)
        response.raise_for_status()
        if response.status_code == 200:
            save_camera_to_db(rtsp_url, device_id, event_id)
            messagebox.showinfo("Success", "Camera registered successfully!")
            update_camera_table()
        else:
            messagebox.showerror("Error", "Failed to register camera.")
    except requests.RequestException as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Save Camera to Database
def save_camera_to_db(rtsp_url, device_id, event_id):
    conn = sqlite3.connect('cameras.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO cameras (rtsp_url, device_id, event_id) VALUES (?, ?, ?)',
                   (rtsp_url, device_id, event_id))
    conn.commit()
    conn.close()

# Fetch Cameras from Database
def fetch_cameras():
    conn = sqlite3.connect('cameras.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, rtsp_url, device_id, event_id FROM cameras')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Update Camera Table in UI
def update_camera_table():
    for row in camera_table.get_children():
        camera_table.delete(row)
    for row in fetch_cameras():
        camera_table.insert('', 'end', values=row)

# GUI Components for Camera Registration
def setup_camera_ui(root):
    # Camera Input Frame
    input_frame = tk.Frame(root, bg='#282c34')
    input_frame.place(relx=0.5, rely=0.2, anchor='center')

    # Input Fields and Labels
    tk.Label(input_frame, text="RTSP URL:", bg='#282c34', fg='white').grid(row=1, column=0)
    rtsp_url_entry = tk.Entry(input_frame, width=40, font=entry_font)
    rtsp_url_entry.grid(row=1, column=1)

    tk.Label(input_frame, text="Device ID:", bg='#282c34', fg='white').grid(row=2, column=0)
    device_id_entry = tk.Entry(input_frame, width=40, font=entry_font)
    device_id_entry.grid(row=2, column=1)

    tk.Label(input_frame, text="Event ID:", bg='#282c34', fg='white').grid(row=3, column=0)
    event_id_entry = tk.Entry(input_frame, width=40, font=entry_font)
    event_id_entry.grid(row=3, column=1)

    # Register Button
    register_button = tk.Button(input_frame, text="Register Camera",
                                command=lambda: register_camera(rtsp_url_entry.get(),
                                                                device_id_entry.get(),
                                                                event_id_entry.get()),
                                bg='#98c379', fg='white', font=button_font)
    register_button.grid(row=4, columnspan=2, pady=10)

    # Camera Table
    columns = ("ID", "RTSP URL", "Device ID", "Event ID")
    global camera_table
    camera_table = ttk.Treeview(root, columns=columns, show='headings')
    for col in columns:
        camera_table.heading(col, text=col)
        camera_table.column(col, anchor='center')
    camera_table.place(relx=0.5, rely=0.5, anchor='center')

    # Update the camera table initially
    update_camera_table()

# Main Window
root = tk.Tk()
root.title("CITRA Event Manager")

# Set Window Size
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
width = int(screen_width * 0.8)
height = int(screen_height * 0.8)
x = (screen_width - width) // 2
y = (screen_height - height) // 2
root.geometry(f"{width}x{height}+{x}+{y}")

# Fonts
entry_font = font.Font(size=12)
button_font = font.Font(size=12, weight="bold")

# Part 2: Server Registration and List Update

# Continuing from the existing imports and main window setup
# ...

def init_server_db():
    conn = sqlite3.connect('servers.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY,
            server_url TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Register Server
def register_server(server_url):
    # Here, add logic to validate the server URL or send a test request
    # For simplicity, we're directly saving it to the database
    save_server_to_db(server_url)
    messagebox.showinfo("Success", "Server registered successfully!")
    update_server_table()

# Save Server to Database
def save_server_to_db(server_url):
    conn = sqlite3.connect('servers.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO servers (server_url) VALUES (?)', (server_url,))
    conn.commit()
    conn.close()

# Fetch Servers from Database
def fetch_servers():
    conn = sqlite3.connect('servers.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, server_url FROM servers')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Update Server Table in UI
def update_server_table():
    for row in server_table.get_children():
        server_table.delete(row)
    for row in fetch_servers():
        server_table.insert('', 'end', values=row)

# GUI Components for Server Registration
def setup_server_ui(root):
    # Server Input Frame
    server_input_frame = tk.Frame(root, bg='#282c34')
    server_input_frame.place(relx=0.5, rely=0.7, anchor='center')

    # Input Fields and Labels for Server URL
    tk.Label(server_input_frame, text="Server URL:", bg='#282c34', fg='white').grid(row=1, column=0)
    global server_url_entry
    server_url_entry = tk.Entry(server_input_frame, width=40, font=entry_font)
    server_url_entry.grid(row=1, column=1)

    # Register Server Button
    register_server_button = tk.Button(server_input_frame, text="Register Server",
                                       command=lambda: register_server(server_url_entry.get()),
                                       bg='#61afef', fg='white', font=button_font)
    register_server_button.grid(row=2, columnspan=2, pady=10)

    # Server Table
    server_columns = ("ID", "Server URL")
    global server_table
    server_table = ttk.Treeview(root, columns=server_columns, show='headings')
    for col in server_columns:
        server_table.heading(col, text=col)
        server_table.column(col, anchor='center')
    server_table.place(relx=0.5, rely=0.8, anchor='center')

    # Update the server table initially
    update_server_table()

# Part 3: Connectivity Check for Cameras and Servers

# Check Camera Status
def check_camera_status():
    # Placeholder for camera status check logic
    # Implement actual connectivity test (e.g., ping test or RTSP request)
    messagebox.showinfo("Status", "Camera status check not implemented.")

# Check Server Status
def check_server_status():
    # Placeholder for server status check logic
    # Implement actual connectivity test (e.g., HTTP request to server)
    messagebox.showinfo("Status", "Server status check not implemented.")

# Add buttons for checking status to the main window
check_camera_status_button = tk.Button(root, text="Check Camera Status",
                                       command=check_camera_status, bg='#e06c75', fg='white', font=button_font)
check_camera_status_button.place(relx=0.3, rely=0.9, anchor='center')

check_server_status_button = tk.Button(root, text="Check Server Status",
                                       command=check_server_status, bg='#e06c75', fg='white', font=button_font)
check_server_status_button.place(relx=0.7, rely=0.9, anchor='center')

# ...

# Initialize the database for cameras and servers
init_camera_db()
init_server_db()

# Setup UI
setup_camera_ui(root)
setup_server_ui(root)

# ...

# Start the Application
root.mainloop()
