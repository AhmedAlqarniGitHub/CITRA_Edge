import tkinter as tk
from tkinter import messagebox, font, ttk
import requests
import sqlite3

# Initialize SQLite Database
def init_db():
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

def register_camera():
    rtsp_url = rtsp_url_entry.get()
    device_id = device_id_entry.get()
    event_id = event_id_entry.get()

    if not rtsp_url or not device_id or not event_id:
        messagebox.showwarning("Warning", "All fields are required!")
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
            save_camera_to_db(rtsp_url, device_id, event_id)
            messagebox.showinfo("Success", "Camera registered successfully!")
            update_camera_table()
    except requests.exceptions.HTTPError as err:
        messagebox.showerror("Error", f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        messagebox.showerror("Error", f"Error occurred: {err}")

def save_camera_to_db(rtsp_url, device_id, event_id):
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

def get_thread_count():
    try:
        response = requests.get("http://localhost:5000/active_threads")
        response.raise_for_status()
        thread_count = response.json().get('active_threads')
        messagebox.showinfo("Active Threads", f"Number of active threads: {thread_count}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def update_camera_table():
    for row in camera_table.get_children():
        camera_table.delete(row)
    for row in fetch_cameras():
        camera_table.insert('', 'end', values=row)


def edit_camera():
    # Get selected item to edit
    selected_item = camera_table.selection()[0]
    if not selected_item:
        messagebox.showinfo("Info", "Please select a camera to edit.")
        return
    camera = camera_table.item(selected_item, 'values')

    # Open a new window to edit the item
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Camera")

    # Add Entry widgets for each field
    ttk.Label(edit_window, text="RTSP URL:").grid(row=0, column=0)
    rtsp_url_var = tk.StringVar(value=camera[1])
    rtsp_url_entry = ttk.Entry(edit_window, textvariable=rtsp_url_var)
    rtsp_url_entry.grid(row=0, column=1)

    ttk.Label(edit_window, text="Device ID:").grid(row=1, column=0)
    device_id_var = tk.StringVar(value=camera[2])
    device_id_entry = ttk.Entry(edit_window, textvariable=device_id_var)
    device_id_entry.grid(row=1, column=1)

    ttk.Label(edit_window, text="Event ID:").grid(row=2, column=0)
    event_id_var = tk.StringVar(value=camera[3])
    event_id_entry = ttk.Entry(edit_window, textvariable=event_id_var)
    event_id_entry.grid(row=2, column=1)

    # Save button
    save_button = ttk.Button(edit_window, text="Save", command=lambda: save_changes(selected_item, rtsp_url_var.get(), device_id_var.get(), event_id_var.get(), edit_window))
    save_button.grid(row=3, column=0, columnspan=2)

def save_changes(selected_item, rtsp_url, device_id, event_id, edit_window):
    # Update the table
    camera_table.item(selected_item, values=(camera_table.item(selected_item, "values")[0], rtsp_url, device_id, event_id))

    # Update the database
    update_db_with_changes(camera_table.item(selected_item, "values"))

    # Close the edit window
    edit_window.destroy()

    # Update the camera table view
    update_camera_table()

def update_db_with_changes(values):
    # Connect to the database
    conn = sqlite3.connect('cameras.db')
    cursor = conn.cursor()
    
    # Update the camera record
    cursor.execute('UPDATE cameras SET rtsp_url = ?, device_id = ?, event_id = ? WHERE id = ?', (values[1], values[2], values[3], values[0]))
    conn.commit()
    conn.close()
    
def check_camera_status():
    selected_item = camera_table.focus()
    if not selected_item:
        messagebox.showinfo("Info", "Please select a camera to check.")
        return
    camera = camera_table.item(selected_item)['values']
    # Implement camera status check logic here
    messagebox.showinfo("Status", f"Status check for camera {camera[2]} not implemented.")

def set_window_size(root):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width = int(screen_width * 0.8)
    height = int(screen_height * 0.8)
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f'{width}x{height}+{x}+{y}')

def connect_to_camera():
    selected_item = camera_table.focus()
    if not selected_item:
        messagebox.showinfo("Info", "Please select a camera to connect.")
        return
    camera = camera_table.item(selected_item)['values']
    rtsp_url, device_id, event_id = camera[1], camera[2], camera[3]

    data = {
        "rtsp_url": rtsp_url,
        "device_id": device_id,
        "event_id": event_id
    }

    try:
        response = requests.post("http://localhost:5000/start_processing", json=data)
        response.raise_for_status()

        if response.status_code == 200:
            messagebox.showinfo("Success", response.json().get('message', 'Started processing the stream'))
    except requests.exceptions.HTTPError as err:
        messagebox.showerror("Error", f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        messagebox.showerror("Error", f"Error occurred: {err}")


# UI Design
root = tk.Tk()
root.title("CITRA Event Manager")

style = ttk.Style(root)
style.theme_use('clam')  # or 'alt', 'default', 'classic'

# Define colors
primary_color = '#6200EE'
secondary_color = '#03DAC6'
background_color = '#121212'
text_color = '#FFFFFF'
button_color = '#3700B3'
error_color = '#CF6679'

# Configure style
style.configure('TButton', background=button_color, foreground=text_color, font=('Helvetica', 12))
style.configure('TLabel', background=background_color, foreground=text_color, font=('Helvetica', 12))
style.configure('TEntry', background='#1F1F1F', foreground=text_color, insertBackground=text_color)
style.map('TButton', background=[('active', secondary_color)])

# Layout
root.configure(bg=background_color)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# Camera Registration Frame
registration_frame = ttk.Frame(root, padding="20")
registration_frame.grid(row=0, column=0, sticky="ew")
registration_frame['borderwidth'] = 2
registration_frame['relief'] = 'ridge'

# Title Label
title_label = ttk.Label(registration_frame, text="Camera Registration", font=('Roboto', 20, 'bold'))
title_label.grid(row=0, columnspan=3, pady=(10, 20))

# RTSP URL
ttk.Label(registration_frame, text="RTSP URL:").grid(row=1, column=0, sticky='w')
rtsp_url_entry = ttk.Entry(registration_frame, width=40)
rtsp_url_entry.grid(row=1, column=1, pady=5, padx=10, sticky='ew')

# Device ID
ttk.Label(registration_frame, text="Device ID:").grid(row=2, column=0, sticky='w')
device_id_entry = ttk.Entry(registration_frame, width=40)
device_id_entry.grid(row=2, column=1, pady=5, padx=10, sticky='ew')

# Event ID
ttk.Label(registration_frame, text="Event ID:").grid(row=3, column=0, sticky='w')
event_id_entry = ttk.Entry(registration_frame, width=40)
event_id_entry.grid(row=3, column=1, pady=5, padx=10, sticky='ew')

# Register Button
register_button = ttk.Button(registration_frame, text="Register Camera", command=register_camera)
register_button.grid(row=4, column=1, pady=(10, 20), sticky='ew')

# Camera Table Frame
table_frame = ttk.Frame(root, padding="20")
table_frame.grid(row=1, column=0, sticky="nsew")
table_frame['borderwidth'] = 2
table_frame['relief'] = 'ridge'

#Camera Table
columns = ("ID", "RTSP URL", "Device ID", "Event ID")
camera_table = ttk.Treeview(table_frame, columns=columns, show='headings', height=5)
for col in columns:
    camera_table.heading(col, text=col)
    camera_table.column(col, anchor='center', width=100)
camera_table.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

#Scrollbar for Table
scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=camera_table.yview)
scrollbar.grid(row=0, column=1, sticky='ns')
camera_table.configure(yscrollcommand=scrollbar.set)

# Update the camera table with data from the database
update_camera_table()

#Buttons Frame
buttons_frame = ttk.Frame(root, padding="20")
buttons_frame.grid(row=2, column=0, sticky="ew")
buttons_frame['borderwidth'] = 2
buttons_frame['relief'] = 'ridge'

#Connect to Camera Button
connect_camera_button = ttk.Button(buttons_frame, text="Connect to Camera", command=connect_to_camera)
connect_camera_button.grid(row=0, column=0, padx=10, pady=20, sticky="ew")

#Get Thread Count Button
thread_count_button = ttk.Button(buttons_frame, text="Get Thread Count", command=get_thread_count)
thread_count_button.grid(row=0, column=1, padx=10, pady=20, sticky="ew")

#Set the main window size
root.geometry('800x600') # Width x Height

# Add Edit button
edit_button = ttk.Button(buttons_frame, text="Edit Camera", command=edit_camera)
edit_button.grid(row=0, column=2, padx=10, pady=20, sticky="ew")

# Make the layout responsive
for i in range(3):  # Update to the number of buttons you have
    buttons_frame.grid_columnconfigure(i, weight=1)
    registration_frame.grid_columnconfigure(i, weight=1)

table_frame.grid_rowconfigure(0, weight=1)
table_frame.grid_columnconfigure(0, weight=1)

# Run the application
root.mainloop()