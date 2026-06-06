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

# Global μεταβλητές για τον έλεγχο του watchdog
observer = None
is_tracking = False

# Το os.path.expanduser('~') παίρνει όλο το "C:/Users/username"
user_home = os.path.expanduser('~')

# Δημιουργία ενός απλού icon σε περίπτωση που λείπει το αρχείο 'folder.png'
if os.path.exists('folder.png'):
    tray_image = Image.open('folder.png')
else:
    tray_image = Image.new('RGB', (64, 64), color='blue')

# --- Συναρτήσεις Διαχείρισης Κανόνων (JSON) ---

def load_rules():
    if not os.path.exists('rules.json'):
        return []
    with open('rules.json', 'r', encoding='utf-8') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def match_rule_and_get_dest(file_name):
    """
    Ελέγχει το αρχείο με βάση όλους τους κανόνες και επιστρέφει 
    τον προορισμό και τον τύπο του κανόνα που ταίριαξε.
    """
    rules = load_rules()
    base_name, file_extension = os.path.splitext(file_name)
    
    # 1ος Έλεγχος: name_starts
    for rule in rules:
        if rule.get('condition') == 'name_starts' and file_name.startswith(rule['value']):
            return rule['destination']
            
    # 2ος Έλεγχος: name_contains
    for rule in rules:
        if rule.get('condition') == 'name_contains' and rule['value'] in file_name:
            return rule['destination']
            
    # 3ος Έλεγχος: extension
    for rule in rules:
        if rule.get('condition') == 'extension' and rule['value'] == file_extension:
            return rule['destination']
            
    return None

# --- Βοηθητικές Συναρτήσεις ---

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

def process_file(full_path, file_name):
    """Κοινή λογική μετακίνησης για Live Tracking & Manual Organize"""
    _, file_extension = os.path.splitext(file_name)

    # Παράβλεψη προσωρινών αρχείων λήψης
    if file_extension in ['.tmp', '.crdownload', '.part'] or file_name.startswith('.'):
        return False

    time.sleep(1) # Αναμονή για να ολοκληρωθεί η γραφή του αρχείου
    if not os.path.exists(full_path):
        return False

    destination_rel = match_rule_and_get_dest(file_name)
    
    if destination_rel:
        dest_dir = os.path.join(user_home, destination_rel)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        final_path = get_unique_path(dest_dir, file_name)
        try:
            shutil.move(full_path, final_path)
            folder_name = os.path.basename(dest_dir)
            
            # Ειδοποίηση
            notification.notify(
                title="Smart Folder Automation",
                message=f"🎉 Το αρχείο {file_name} μεταφέρθηκε στα {folder_name}!",
                app_name="FolderApp",
                timeout=5 
            )                  
            write_log(f"🎉 AUTOMATION: Ταξινομήθηκε το {file_name} -> {folder_name}")
            print(f"🎉 Νέο αρχείο ταξινομήθηκε: {os.path.basename(final_path)}")
            return True
        except Exception as e:
            print(f"❌ Σφάλμα κατά τη μετακίνηση του {file_name}: {e}")
            return False
    return False

# --- Watchdog Handler ---

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            full_path = event.src_path
            file_name = os.path.basename(full_path)
            process_file(full_path, file_name)

# --- Κύρια Λογική UI Actions ---

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
        observer = Observer()
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
        
    else:
        # ORGANIZE LOGIC (Manual)
        print(f"🧹 Καθαρισμός {folder} στο: {path_to_track}")
        write_log(f"SYSTEM: Μη αυτόματος καθαρισμός στο {path_to_track}")
        moved_count = 0

        # os.scandir για καλύτερη απόδοση αντί για os.walk αν δεν θες υποφακέλους
        try:
            for entry in os.scandir(path_to_track):
                if entry.is_file():
                    if process_file(entry.path, entry.name):
                        moved_count += 1
        except Exception as e:
            print(f"❌ Σφάλμα κατά την ανάγνωση του φακέλου: {e}")
        
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
        app.deiconify()
    elif str(item) == "Exit":
        stop_tracking()
        icon.stop()
        app.quit()

def run_tray():
    menu = pystray.Menu(pystray.MenuItem("Open", check_menu), pystray.MenuItem("Exit", check_menu))
    icon = pystray.Icon("FolderOrganizer", tray_image, "Folder Organizer", menu)
    icon.run()

def withdraw_window():
    app.withdraw()
    notification.notify(
        title="Smart Folder Automation",
        message="Η εφαρμογή εκτελείται στο background (System Tray)!",
        timeout=3
    )

    

def add_rules_window():
    def add_rules():
        condition = select_condition.get()
        value = select_value.get()
        destination = select_destination.get()

        data = {"condition": condition, "value": value,"destination": destination}

        with open("rules.json", "r", encoding="utf-8") as file:
         rules = json.load(file)

        rules.append(data)

        with open('rules.json', "w", encoding="utf-8") as file:
            json.dump(rules, file, indent=4, ensure_ascii=False)

        
    app = ctk.CTk()
    app.title("Smart Folder Automation Hub - Add Rules")
    app.geometry("350x350")

    select_condition = ctk.CTkOptionMenu(app,values=['extension','name_starts','name_contains'])
    select_condition.pack(pady=20)

    select_value = ctk.CTkEntry(app,placeholder_text="Select Value: .mp3, report.......")    
    select_value.pack(pady=20)

    select_destination = ctk.CTkEntry(app,placeholder_text="Select destination(It must be a folder name in User)")
    select_destination.pack(pady=20)

    add_btn = ctk.CTkButton(app,text="Add",command=add_rules)
    add_btn.pack(pady=20)

    app.mainloop()




# --- UI Setup ---
app = ctk.CTk()

app.title("Smart Folder Automation Hub")
app.geometry("350x350")
app.protocol('WM_DELETE_WINDOW', withdraw_window)

select_action = ctk.CTkOptionMenu(app, values=["Track", "Organize"])
select_action.pack(pady=15)

select_folder_option = ctk.CTkOptionMenu(app, values=["Downloads", "Desktop"])
select_folder_option.pack(pady=15)

add_rules_btn = ctk.CTkButton(app,text="Add Rules",command=add_rules_window)
add_rules_btn.pack(pady=20)

start_btn = ctk.CTkButton(app, text="Start Action", command=thread_select_folder, fg_color="green", hover_color="darkgreen")
start_btn.pack(pady=10)

stop_btn = ctk.CTkButton(app, text="Stop Track", command=stop_tracking, fg_color="red", hover_color="darkred")
stop_btn.pack(pady=10)

status_label = ctk.CTkLabel(app, text="Status: Idle", font=("Arial", 12, "italic"))
status_label.pack(pady=10)


if __name__ == "__main__":
    threading.Thread(target=run_tray, daemon=True).start()
    app.mainloop()