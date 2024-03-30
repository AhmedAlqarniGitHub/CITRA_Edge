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

# ... (Continue with the rest of camera database functions)
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
        
# Initialize SQLite Database for Servers
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

# ... (Continue with the rest of server database functions)
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

# Main Application
class CITRAEventManager(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("CITRA Event Manager")


        self.init_ui()
        

    def init_ui(self):

        # Set Window Size and Position
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = int(screen_width * 0.8)
        height = int(screen_height * 0.8)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Tab Control
        tab_control = ttk.Notebook(self)

        camera_tab = tk.Frame(tab_control, bg='#282c34')
        server_tab = tk.Frame(tab_control, bg='#282c34')
        connectivity_tab = tk.Frame(tab_control, bg='#282c34')

        entry_font = font.Font(size=16)
        button_font = font.Font(size=16, weight="bold")
        
        tab_control.add(camera_tab, text='Cameras')
        tab_control.add(server_tab, text='Servers')
        tab_control.add(connectivity_tab, text='Connectivity')
        tab_control.pack(expand=1, fill="both")

        # Setup UI for each tab
        self.setup_camera_ui(camera_tab, entry_font, button_font)
        self.setup_server_ui(server_tab, entry_font, button_font)
        self.setup_connectivity_ui(connectivity_tab, button_font)

        # Initialize databases
        init_camera_db()
        init_server_db()

    # Define the UI setup functions for each tab
    def setup_camera_ui(self, parent, entry_font, button_font):
        # ... (Same as the setup_camera_ui function but adjusted for the parent argument)
        # Camera Input Frame
        input_frame = tk.Frame(self, bg='#282c34')
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
        camera_table = ttk.Treeview(self, columns=columns, show='headings')
        for col in columns:
            camera_table.heading(col, text=col)
            camera_table.column(col, anchor='center')
        camera_table.place(relx=0.5, rely=0.5, anchor='center')

        # Update the camera table initially
        update_camera_table()
    
    def setup_server_ui(self, parent, entry_font, button_font):
        # ... (Same as the setup_server_ui function but adjusted for the parent argument)
        # Server Input Frame
        server_input_frame = tk.Frame(self, bg='#282c34')
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
        server_table = ttk.Treeview(self, columns=server_columns, show='headings')
        for col in server_columns:
            server_table.heading(col, text=col)
            server_table.column(col, anchor='center')
        server_table.place(relx=0.5, rely=0.8, anchor='center')

        # Update the server table initially
        update_server_table()

    def setup_connectivity_ui(self, parent, button_font):
        # Add buttons for checking status
        check_camera_status_button = tk.Button(parent, text="Check Camera Status",
                                               command=self.check_camera_status, bg='#e06c75', fg='white', font=button_font)
        check_camera_status_button.pack(pady=10)

        check_server_status_button = tk.Button(parent, text="Check Server Status",
                                               command=self.check_server_status, bg='#e06c75', fg='white', font=button_font)
        check_server_status_button.pack(pady=10)

    # Define other functions like check_camera_status, check_server_status etc.
    def check_camera_status():
        # Placeholder for camera status check logic
        # Implement actual connectivity test (e.g., ping test or RTSP request)
        messagebox.showinfo("Status", "Camera status check not implemented.")

    # Check Server Status
    def check_server_status():
        # Placeholder for server status check logic
        # Implement actual connectivity test (e.g., HTTP request to server)
        messagebox.showinfo("Status", "Server status check not implemented.")


# Start the Application
if __name__ == "__main__":
    app = CITRAEventManager()
    app.mainloop()
