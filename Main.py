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

# Το os.path.expanduser('~') παίρνει όλο το "C:/Users/gregi"
user_home = os.path.expanduser('~')

documents = [".pdf", '.docx', '.doc', '.txt']
images = ['.jpg', '.png', '.jpeg', '.gif', '.tif', '.tiff', 'svg']
videos = ['.mp4', '.avi', '.mov', '.wmv', '.flv']
audio = ['.mp3', '.wav', '.flac', '.aac']

# Global μεταβλητές για τον έλεγχο του watchdog
observer = None
is_tracking = False

# Δημιουργία ενός απλού icon σε περίπτωση που λείπει το αρχείο 'folder.png'
if os.path.exists('folder.png'):
    tray_image = Image.open('folder.png')
else:
    tray_image = Image.new('RGB', (64, 64), color='blue')

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
    with open("automation_log.txt", 'a', encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {event}\n")

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            full_path = event.src_path
            file_name = os.path.basename(full_path)
            _, file_extension = os.path.splitext(file_name)

            if file_extension in ['.tmp', '.crdownload', '.part']:
                return

            time.sleep(1)
            if not os.path.exists(full_path):
                return

            dest_dir = None
            if file_extension in documents:
                dest_dir = os.path.join(user_home, "Documents")
            elif file_extension in images:
                dest_dir = os.path.join(user_home, "Pictures")
            elif file_extension in videos:
                dest_dir = os.path.join(user_home, "Videos")
            elif file_extension in audio:
                dest_dir = os.path.join(user_home, "Music")

            if dest_dir:
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                    
                final_path = get_unique_path(dest_dir, file_name)
                shutil.move(full_path, final_path)
                
                folder_name = os.path.basename(dest_dir)
                notification.notify(
                    title="Smart Folder Automation",
                    message=f"🎉 Το αρχείο {file_name} μεταφέρθηκε στα {folder_name}!",
                    app_name="FolderApp",
                    timeout=5 
                )                  
                write_log(f"🎉 LIVE: Ταξινομήθηκε το {file_name} -> {folder_name}")
                print(f"🎉 Νέο αρχείο ταξινομήθηκε: {os.path.basename(final_path)}")

def select_folder():
    global observer, is_tracking
    folder = select_folder_option.get()
    action = select_action.get()
    path_to_track = os.path.join(user_home, folder)
    
    if action == "Track":
        if is_tracking:
            print("⚠️ Η παρακολούθηση τρέχει ήδη!")
            return
            
        event_handler = MyHandler()
        observer = Observer()  # Δημιουργούμε νέο instance κάθε φορά
        observer.schedule(event_handler, path=path_to_track, recursive=False)
    
        print(f"🚀 Παρακολούθηση ξεκίνησε στο: {path_to_track}")
        write_log(f"SYSTEM: Ξεκίνησε live παρακολούθηση στο {path_to_track}")
        
        notification.notify(
            title="Smart Folder Automation",
            message=f"🚀 Η live παρακολούθηση των {folder} ξεκίνησε!",
            timeout=3
        )
        
        is_tracking = True
        status_label.configure(text=f"Status: Tracking {folder}", text_color="green")
        observer.start()
    
        try:
            while is_tracking:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        # ORGANIZE LOGIC
        print(f"🧹 Καθαρισμός {folder} στο: {path_to_track}")
        write_log(f"SYSTEM: Μη αυτόματος καθαρισμός στο {path_to_track}")
        moved_count = 0

        for (root, dirs, files) in os.walk(path_to_track):
            for file_name in files:
                full_file_path = os.path.join(root, file_name)
                _, file_extension = os.path.splitext(file_name)
                
                dest_dir = None
                if file_extension in documents:
                    dest_dir = os.path.join(user_home, "Documents")
                elif file_extension in images:
                    dest_dir = os.path.join(user_home, "Pictures")
                elif file_extension in videos:
                    dest_dir = os.path.join(user_home, "Videos")
                elif file_extension in audio:
                    dest_dir = os.path.join(user_home, "Music")

                if dest_dir:
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    final_path = get_unique_path(dest_dir, file_name)
                    shutil.move(full_file_path, final_path)
                    moved_count += 1
                    write_log(f"🧹 MANUAL: Μετακινήθηκε το {file_name}")
        
        notification.notify(
            title=f"{folder} Cleaned!",
            message=f"🧹 Ολοκληρώθηκε ο καθαρισμός. Μεταφέρθηκαν {moved_count} αρχεία!",
            timeout=5
        )
        status_label.configure(text="Status: Clean Finished", text_color="blue")

def stop_tracking():
    global observer, is_tracking
    if is_tracking and observer:
        is_tracking = False
        observer.stop()
        observer.join()
        print("🛑 Η παρακολούθηση σταμάτησε.")
        write_log("SYSTEM: Η παρακολούθηση σταμάτησε από τον χρήστη.")
        status_label.configure(text="Status: Stopped", text_color="red")
    else:
        print("⚠️ Δεν υπάρχει ενεργή παρακολούθηση για να σταματήσει.")

def thread_select_folder():
    threading.Thread(target=select_folder, daemon=True).start()

# --- System Tray Logic ---
def check_menu(icon, item):
    if str(item) == "Open":
        # Εμφάνιση ξανά του παραθύρου
        app.deiconify()
    elif str(item) == "Exit":
        stop_tracking()
        icon.stop()
        app.quit() # Κλείνει τελείως το CustomTkinter

def run_tray():
    menu = pystray.Menu(pystray.MenuItem("Open", check_menu), pystray.MenuItem("Exit", check_menu))
    icon = pystray.Icon("FolderOrganizer", tray_image, "Folder Organizer", menu)
    icon.run()

# Κλείσιμο παραθύρου στο Tray αντί για τερματισμό
def withdraw_window():
    app.withdraw() # Κρύβει το παράθυρο αλλά η εφαρμογή συνεχίζει να τρέχει
    notification.notify(
        title="Smart Folder Automation",
        message="Η εφαρμογή εκτελείται στο background (System Tray)!",
        timeout=3
    )

# --- UI Setup ---
app = ctk.CTk()
app.title("Smart Folder Automation Hub")
app.geometry("350x350")
app.protocol('WM_DELETE_WINDOW', withdraw_window) # Όταν πατάς το 'X', κρύβεται στο tray

select_action = ctk.CTkOptionMenu(app, values=["Track", "Organize"])
select_action.pack(pady=15)

select_folder_option = ctk.CTkOptionMenu(app, values=["Downloads", "Desktop"])
select_folder_option.pack(pady=15)

start_btn = ctk.CTkButton(app, text="Start Action", command=thread_select_folder, fg_color="green", hover_color="darkgreen")
start_btn.pack(pady=10)

stop_btn = ctk.CTkButton(app, text="Stop Track", command=stop_tracking, fg_color="red", hover_color="darkred")
stop_btn.pack(pady=10)

status_label = ctk.CTkLabel(app, text="Status: Idle", font=("Arial", 12, "italic"))
status_label.pack(pady=10)

if __name__ == "__main__":
    # Ξεκινάμε το System Tray σε δικό του thread για να μην μπλοκάρει το UI
    threading.Thread(target=run_tray, daemon=True).start()
    
    # Το κεντρικό loop του CustomTkinter τρέχει στο Main Thread
    app.mainloop()