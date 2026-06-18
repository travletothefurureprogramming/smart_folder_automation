import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import customtkinter as ctk
import threading
from plyer import notification
import pystray
from PIL import Image
import json
from flask import Flask, render_template_string, jsonify

observer = None
is_tracking = False
total_moved_count = 0
user_home = os.path.expanduser('~')
data_lock = threading.Lock()

template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Folder Automation Hub</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        body {
            background: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,.08);
            background: white;
            transition: transform 0.2s;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .metric-number {
            font-size: 4.5rem;
            font-weight: 700;
            color: #0d6efd;
        }
    </style>
</head>
<body>
<div class="container py-5">
    <h1 class="text-center mb-5 fw-bold text-primary">
        <i class="bi bi-cpu-fill"></i> SMART FOLDER AUTOMATION HUB
    </h1>
    <div class="row justify-content-center">
        <div class="col-lg-5 col-md-7">
            <div class="card p-5 text-center">
                <div class="mb-3">
                    <span class="badge bg-primary p-3 rounded-circle">
                        <i class="bi bi-files fs-3"></i>
                    </span>
                </div>
                <h4 class="fw-semibold mb-2">Files Moved</h4>
                <div id="count" class="metric-number">0</div>
                <p class="text-muted small">The page refreshes automatically every 3 seconds</p>
            </div>
        </div>
    </div>
</div>
<script>
const SERVER = window.location.origin;
function updateSystemInfo(){
    fetch(`${SERVER}/api/count`)
    .then(response => response.json())
    .then(data => {
        document.getElementById("count").innerHTML = data.moved_files;
    })
    .catch(err => console.error("Error connecting to API:", err));
}
updateSystemInfo();
setInterval(updateSystemInfo, 3000);
</script>
</body>
</html>
"""

if os.path.exists('folder.png'):
    tray_image = Image.open('folder.png')
else:
    tray_image = Image.new('RGB', (64, 64), color=(13, 110, 253))

if not os.path.exists("automation_log.txt"):
    with open("automation_log.txt", "w", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Automation log initialized.\n")

def is_file_locked(filepath):
    try:
        with open(filepath, 'a'):
            return False
    except IOError:
        return True

def load_rules():
    if not os.path.exists('rules.json'):
        return []
    with open('rules.json', 'r', encoding='utf-8') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def match_rule_and_get_dest(file_name):
    rules = load_rules()
    base_name, file_extension = os.path.splitext(file_name)
    
    for rule in rules:
        if rule.get('condition') == 'name_starts' and file_name.startswith(rule['value']):
            return rule['destination']
            
    for rule in rules:
        if rule.get('condition') == 'name_contains' and rule['value'] in file_name:
            return rule['destination']
            
    for rule in rules:
        if rule.get('condition') == 'extension' and rule['value'].lower() == file_extension.lower():
            return rule['destination']
            
    return None

def get_unique_path(destination_folder, file_name):
    base_name, extension = os.path.splitext(file_name)
    destination_path = os.path.join(destination_folder, file_name)
    counter = 1
    
    while os.path.exists(destination_path):
        new_name = f"{base_name}_{counter}{extension}"
        destination_path = os.path.join(destination_folder, new_name)
        counter += 1
        
    return destination_path

def write_log(event):
    with data_lock:
        with open("automation_log.txt", 'a', encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {event}\n")

def process_file(full_path, file_name):
    global total_moved_count

    _, file_extension = os.path.splitext(file_name)

    if file_extension.lower() in ['.tmp', '.crdownload', '.part'] or file_name.startswith('.'):
        return False

    time.sleep(1.5)
    if not os.path.exists(full_path):
        return False
        
    if is_file_locked(full_path):
        print(f"⏳ File {file_name} is locked. Waiting...")
        return False

    destination_rel = match_rule_and_get_dest(file_name)
    
    if destination_rel:
        dest_dir = os.path.join(user_home, destination_rel)
        if not os.path.exists(dest_dir):
            try:
                os.makedirs(dest_dir)
            except Exception as e:
                print(f"❌ Failed to create directory {dest_dir}: {e}")
                return False
            
        final_path = get_unique_path(dest_dir, file_name)
        try:
            shutil.move(full_path, final_path)
            folder_name = os.path.basename(dest_dir)

            with data_lock:
                total_moved_count += 1
            
            notification.notify(
                title="Smart Folder Automation",
                message=f"🎉 File {file_name} was moved to folder {folder_name}!",
                app_name="FolderApp",
                timeout=4
            )            
            write_log(f"AUTOMATION: Sorted {file_name} -> {folder_name}")
            print(f"🎉 New file sorted: {os.path.basename(final_path)}")
            return True
        except Exception as e:
            print(f"❌ Error moving {file_name}: {e}")
            return False
    return False

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global total_moved_count
        if not event.is_directory:
            file_name = os.path.basename(event.src_path)
            if process_file(event.src_path, file_name):
                app.after(0, lambda: status_label.configure(
                    text=f"Status: Active | Moved: {total_moved_count}"
                ))

def select_folder():
    global observer, is_tracking
    folder = select_folder_option.get()
    path_to_track = os.path.join(user_home, folder)
    action = select_action.get()
    
    if action == "Live Track":
        if is_tracking:
            print("⚠️ Tracking is already running!")
            return
            
        event_handler = MyHandler()
        observer = Observer()
        observer.schedule(event_handler, path=path_to_track, recursive=False)
    
        print(f"🚀 Tracking started at: {path_to_track}")
        write_log(f"SYSTEM: Started live tracking at {path_to_track}")
        
        notification.notify(
            title="Smart Folder Automation",
            message=f"🚀 Tracking started for folder {folder}!",
            timeout=3
        )
        
        is_tracking = True
        status_label.configure(text=f"Status: Tracking {folder}", text_color="#198754")
        observer.start()
        
    else:
        print(f"🧹 Manual cleanup of {folder} at: {path_to_track}")
        write_log(f"SYSTEM: Manual cleanup at {path_to_track}")
        moved_count = 0

        if not os.path.exists(path_to_track):
            print(f"❌ Folder {path_to_track} does not exist.")
            status_label.configure(text="Status: Folder Error", text_color="red")
            return

        try:
            for entry in os.scandir(path_to_track):
                if entry.is_file():
                    if process_file(entry.path, entry.name):
                        moved_count += 1
        except Exception as e:
            print(f"❌ Error reading folder: {e}")
        
        notification.notify(
            title=f"Cleanup {folder}!",
            message=f"🧹 Cleanup complete. Moved {moved_count} files!",
            timeout=5
        )
        status_label.configure(text=f"Status: Completed (Moved {moved_count})", text_color="#0d6efd")

def stop_tracking():
    global observer, is_tracking
    if is_tracking and observer:
        is_tracking = False
        observer.stop()
        observer.join()
        print("🛑 Tracking stopped.")
        write_log("SYSTEM: Tracking terminated by user.")
        status_label.configure(text="Status: Stopped", text_color="#dc3545")
    else:
        print("⚠️ No active tracking to stop.")

def thread_select_folder():
    threading.Thread(target=select_folder, daemon=True).start()

def check_menu(icon, item):
    if str(item) == "Open":
        app.deiconify()
    elif str(item) == "Exit":
        stop_tracking()
        icon.stop()
        app.quit()

def run_tray():
    menu = pystray.Menu(
        pystray.MenuItem("Open", check_menu), 
        pystray.MenuItem("Exit", check_menu)
    )
    icon = pystray.Icon("FolderOrganizer", tray_image, "Folder Organizer", menu)
    icon.run()

def withdraw_window():
    app.withdraw()
    notification.notify(
        title="Smart Folder Automation",
        message="App is running in the background (System Tray)!",
        timeout=3
    )

def add_rules_window():
    def add_rules():
        condition = select_condition.get()
        value = select_value.get().strip()
        destination = select_destination.get().strip()

        if not value or not destination:
            print("⚠️ Please fill in all fields!")
            return

        data = {"condition": condition, "value": value, "destination": destination}

        with data_lock:
            rules = []
            if os.path.exists("rules.json"):
                with open("rules.json", "r", encoding="utf-8") as file:
                    try:
                        rules = json.load(file)
                    except json.JSONDecodeError:
                        rules = []

            rules.append(data)

            with open('rules.json', "w", encoding="utf-8") as file:
                json.dump(rules, file, indent=4, ensure_ascii=False)
        
        print(f"✅ Rule added: {condition} -> {value} moving to {destination}")
        app_rules.destroy()

    app_rules = ctk.CTk()
    app_rules.title("Add Sorting Rules")
    app_rules.geometry("380x380")
    app_rules.resizable(False, False)

    lbl_title = ctk.CTkLabel(app_rules, text="New Rule", font=("Arial", 16, "bold"))
    lbl_title.pack(pady=15)

    select_condition = ctk.CTkOptionMenu(
        app_rules, 
        values=['extension', 'name_starts', 'name_contains']
    )
    select_condition.pack(pady=10)

    select_value = ctk.CTkEntry(
        app_rules, 
        placeholder_text="Value: .mp3, report, etc.", 
        width=250
    )    
    select_value.pack(pady=10)

    select_destination = ctk.CTkEntry(
        app_rules, 
        placeholder_text="Destination folder name", 
        width=250
    )
    select_destination.pack(pady=10)

    add_btn = ctk.CTkButton(
        app_rules, 
        text="Save Rule", 
        command=add_rules,
        fg_color="#0d6efd",
        hover_color="#0b5ed7"
    )
    add_btn.pack(pady=20)

    app_rules.mainloop()

server = Flask(__name__)

@server.route("/")
def dashboard():
    return render_template_string(template)

@server.route("/api/count", methods=["GET"])
def get_count():
    global total_moved_count
    return jsonify({"moved_files": total_moved_count})

def run_flask():
    try:
        server.run(host="0.0.0.0", port=5000, use_reloader=False)
    except Exception as e:
        print(f"❌ Error starting Flask Web Server: {e}")

app = ctk.CTk()
app.title("Smart Folder Automation Hub")
app.geometry("400x480")
app.resizable(False, False)
app.protocol('WM_DELETE_WINDOW', withdraw_window)

main_title = ctk.CTkLabel(app, text="Smart Folder Automation", font=("Arial", 18, "bold"))
main_title.pack(pady=15)

lbl_action = ctk.CTkLabel(app, text="1. Select Action:", font=("Arial", 12))
lbl_action.pack(pady=2)
select_action = ctk.CTkOptionMenu(app, values=["Live Track", "Clean Now"])
select_action.pack(pady=5)

lbl_folder = ctk.CTkLabel(app, text="2. Select Folder:", font=("Arial", 12))
lbl_folder.pack(pady=2)
select_folder_option = ctk.CTkOptionMenu(app, values=["Downloads", "Desktop"])
select_folder_option.pack(pady=5)

add_rules_btn = ctk.CTkButton(
    app, 
    text="Manage Rules", 
    command=add_rules_window,
    fg_color="#6c757d",
    hover_color="#5a6268"
)
add_rules_btn.pack(pady=15)

start_btn = ctk.CTkButton(
    app, 
    text="Start Action", 
    command=thread_select_folder, 
    fg_color="#198754", 
    hover_color="#157347"
)
start_btn.pack(pady=8)

stop_btn = ctk.CTkButton(
    app, 
    text="Stop Tracking", 
    command=stop_tracking, 
    fg_color="#dc3545", 
    hover_color="#bb2d3b"
)
stop_btn.pack(pady=8)

status_label = ctk.CTkLabel(app, text="Status: Idle", font=("Arial", 12, "italic"))
status_label.pack(pady=10)

dashboard_label = ctk.CTkLabel(
    app, 
    text="Web Dashboard: http://localhost:5000", 
    font=("Arial", 11, "bold"),
    text_color="#0d6efd"
)
dashboard_label.pack(pady=5)

if __name__ == "__main__":
    threading.Thread(target=run_tray, daemon=True).start()
    threading.Thread(target=run_flask, daemon=True).start()
    app.mainloop()