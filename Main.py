import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import customtkinter as ctk

user = 'gregi'
documents = [".pdf",'.docx','.doc','.txt']
images = ['.jpg','.png','.jpeg','.gif','.tif,','.tiff','svg']
videos = ['.mp4','.avi','.mov','.wmv','.flv']
audio = ['.mp3','.wav','.flac','.aac']

class MyHandler(FileSystemEventHandler):
    # Χρησιμοποιούμε την on_modified γιατί ο browser αλλάζει το αρχείο όταν τελειώνει το download
    def on_modified(self, event):
        if not event.is_directory:

            
            # 1. Παίρνουμε την πλήρη διαδρομή (π.χ. C:/Downloads/photo.png)
            full_path = event.src_path
            
            # 2. Απομονώνουμε μόνο το όνομα του αρχείου (π.χ. photo.png)
            file_name = os.path.basename(full_path)
            
            # 3. Χωρίζουμε το όνομα από την κατάληξη (π.χ. '.png')
            _, file_extension = os.path.splitext(file_name)

            if file_extension in ['.tmp', '.crdownload', '.part']:
                return # Σταματάει εδώ η συνάρτηση, δεν κάνει τίποτα

            if file_extension in documents:
                shutil.move(full_path,f"C:/Users/{user}/Documents")
            elif file_extension in images:
                shutil.move(full_path,f"C:/Users/{user}/Pictures")
            elif file_extension in videos:
                shutil.move(full_path,f"C:/Users/{user}/Videos")
            elif file_extension in audio:
                shutil.move(full_path,f"C:/Users/{user}/Music")
            
            print(f"🎉 Νέο αρχείο εντοπίστηκε!")
            print(f"Όνομα: {file_name}")
            print(f"Κατάληξη: {file_extension}")
            print(f"Πλήρες Path: {full_path}")
            print("-" * 30)

def select_folder():
    folder = select_folder_option.get()
    if folder == "Downloads":
        path_to_track = f"C:/Users/{user}/Downloads" 
    
        event_handler = MyHandler()
        observer = Observer()
        observer.schedule(event_handler, path=path_to_track, recursive=False)
    
        print(f"Παρακολούθηση ξεκίνησε στο: {path_to_track}")
        observer.start()
    
        try:
         while True:
            time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    else:
        path_to_track = f"C:/Users/{user}/Desktop" 

        for (root, dirs, file) in os.walk(path_to_track):
            for f in file:
                if documents in f:
                    print(f)
                    shutil.move(dirs,f"C:/Users/{user}/Documents")
                elif images in f:
                    print(f)
                    shutil.move(dirs,f"C:/Users/{user}/Images")
                elif videos in f:
                    print(f)
                    shutil.move(dirs,f"C:/Users/{user}/Videos")
                elif audio in f:
                    print(f)
                    shutil.move(dirs,f"C:/Users/{user}/Music")

app = ctk.CTk()

app.title("Smart Folder Automation Hub")

app.geometry("300x300")

select_folder_option = ctk.CTkOptionMenu(app,values=["Downloads","Desktop"])

start_btn = ctk.CTkButton(app,command=)



if __name__ == "__main__":
    # Βάλε το δικό σου path για τα Downloads (π.χ. στα Windows)
    # Προσοχή: Χρησιμοποίησε forward slashes (/) ή διπλά backslashes (\\)
    path_to_track = f"C:/Users/{user}//Downloads" 
    
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_track, recursive=False)
    
    print(f"Παρακολούθηση ξεκίνησε στο: {path_to_track}")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()