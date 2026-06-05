import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import customtkinter as ctk
import threading
from plyer import notification

user = os.path.expanduser('~')
documents = [".pdf", '.docx', '.doc', '.txt']
images = ['.jpg', '.png', '.jpeg', '.gif', '.tif', '.tiff', 'svg']
videos = ['.mp4', '.avi', '.mov', '.wmv', '.flv']
audio = ['.mp3', '.wav', '.flac', '.aac']

observer = Observer()


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
    with open("automation_log.txt",'a') as f:
        f.write(f"{event}\n")

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
                dest_dir = f"C:/Users/{user}/Documents"
            elif file_extension in images:
                dest_dir = f"C:/Users/{user}/Pictures"
            elif file_extension in videos:
                dest_dir = f"C:/Users/{user}/Videos"
            elif file_extension in audio:
                dest_dir = f"C:/Users/{user}/Music"

            if dest_dir:
                final_path = get_unique_path(dest_dir, file_name)
                shutil.move(full_path, final_path)
                
                # Καθαρισμός του μηνύματος για να δείχνει μόνο το όνομα του φακέλου (π.txt. Pictures)
                folder_name = os.path.basename(dest_dir)
                notification.notify(
                    title="Smart Folder Automation",
                    message=f"🎉 Το αρχείο {file_name} μεταφέρθηκε στα {folder_name}!",
                    app_name="FolderApp",
                    timeout=5 
                )                  
                write_log(f"🎉 Νέο αρχείο ταξινομήθηκε: {os.path.basename(final_path)}")
                print(f"🎉 Νέο αρχείο ταξινομήθηκε: {os.path.basename(final_path)}")
                print("-" * 30)

def select_folder():
    folder = select_folder_option.get()
    action = select_action.get()
    if action == "Track":
        path_to_track = f"C:/Users/{user}/{folder}" 
    
        event_handler = MyHandler()
        observer.schedule(event_handler, path=path_to_track, recursive=False)
    
        print(f"Παρακολούθηση ξεκίνησε στο: {path_to_track}")
        write_log(f"Παρακολούθηση ξεκίνησε στο: {path_to_track}")
        
        notification.notify(
            title="Smart Folder Automation",
            message=f"🚀 Η live παρακολούθηση των {folder} ξεκίνησε!",
            timeout=3
        )
        
        observer.start()
    
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    else:
        path_to_track = f"C:/Users/{user}/{folder}" 
        print(f"🧹 Καθαρισμός {folder} στο: {path_to_track}")
        
        moved_count = 0  # Μετρητής για το notification

        for (root, dirs, files) in os.walk(path_to_track):
            for file_name in files:
                full_file_path = os.path.join(root, file_name)
                _, file_extension = os.path.splitext(file_name)
                
                dest_dir = None
                if file_extension in documents:
                    dest_dir = f"C:/Users/{user}/Documents"
                elif file_extension in images:
                    dest_dir = f"C:/Users/{user}/Pictures"
                elif file_extension in videos:
                    dest_dir = f"C:/Users/{user}/Videos"
                elif file_extension in audio:
                    dest_dir = f"C:/Users/{user}/Music"

                if dest_dir:
                    final_path = get_unique_path(dest_dir, file_name)
                    shutil.move(full_file_path, final_path)
                    moved_count += 1
                    write_log(f"🧹 Μετακινήθηκε από {folder}: {os.path.basename(final_path)}")
                    print(f"🧹 Μετακινήθηκε από {folder}: {os.path.basename(final_path)}")
        
        # Ειδοποίηση για τη μαζική εκκαθάριση του Desktop
        notification.notify(
            title=f"{folder} Cleaned!",
            message=f"🧹 Ολοκληρώθηκε ο καθαρισμός. Μεταφέρθηκαν {moved_count} αρχεία!",
            timeout=5
        )
        write_log(f"🧹 Ολοκληρώθηκε ο καθαρισμός. Μεταφέρθηκαν {moved_count} αρχεία!")

def thread_select_folder():
    threading.Thread(target=select_folder, daemon=True).start()

# --- UI Setup ---
app = ctk.CTk()
app.title("Smart Folder Automation Hub")
app.geometry("300x300")

select_action = ctk.CTkOptionMenu(app, values=["Track", "Organize"])
select_action.pack(pady=20)

select_folder_option = ctk.CTkOptionMenu(app, values=["Downloads", "Desktop"])
select_folder_option.pack(pady=20)

start_btn = ctk.CTkButton(app, text="Start Organize/Track", command=thread_select_folder)
start_btn.pack(pady=20)

start_btn = ctk.CTkButton(app, text="Stop track", command=observer.stop)
start_btn.pack(pady=20)

app.mainloop()