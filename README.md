# SMART FOLDER AUTOMATION HUB
#### A smart open-source tool with Python which is running in backgroud and organize automatic the Downloads and Desktop folders.

### Our app

<img width="881" height="456" alt="Screenshot 2026-06-06 131843" src="https://github.com/user-attachments/assets/3fbdbda4-ea22-468f-9f8e-548bdcd43241" />
<img width="433" height="477" alt="Screenshot 2026-06-06 131831" src="https://github.com/user-attachments/assets/3966915c-ca32-44d1-b71d-0449f936de1b" />

### Features

* Track and organize files for Desktop and Downloads folders
* Add custom rules
* Add rules not only for extension but also for start with and contains

### Platform Support

* Windows
* Mac/Linux (Coming Soon!)

### Tech Stack

* **Language:** Python 3.11
* **Core Libraries:** watchdog, shutil
* **Interface Tool:** Customtkinter

### Install Instructions - How to run

#### Windows:

1. Download the release from github( All files: Main.exe, rules.json, automation_log.txt
2. Open the .exe and organize your life

#### For Developers (Running from Source):

1. Clone the repo: git clone [https://github.com/travletothefurureprogramming/smart_folder_automation](https://github.com/travletothefurureprogramming/smart_folder_automation)

2. Install requirements: pip install watchdog customtkinter

3. Run: cd source
   
4. Run: python Main.py

## How To Use

### Clean Now

Use **Clean Now** to instantly organize files that are already inside your Downloads or Desktop folder.

1. Select **Clean Now**
2. Select a folder (Downloads/Desktop)
3. Click **Start Action**

The app will scan the folder and move files according to the built-in and custom rules.

---

### Live Track

Use **Live Track** for automatic real-time organization.

1. Select **Live Track**
2. Select a folder (Downloads/Desktop)
3. Click **Start Action**

The app will continue running in the background and automatically organize new files as they appear.

Example:

* PDF → Documents
* JPG/PNG → Pictures
* MP4 → Videos
* MP3 → Music

---

### Default Rules Included

The application ships with ready-to-use rules for common file types:

* Documents (.pdf, .docx, .doc, .txt)
* Pictures (.jpg, .jpeg, .png, .gif, .svg, .tif, .tiff)
* Videos (.mp4, .avi, .mov, .wmv, .flv)
* Music (.mp3, .wav, .flac, .aac)

You can add your own custom rules anytime using the **Manage Rules** button.


### Key Quality of Life Improvements
The Smart Folder Automation Hub is designed to eliminate digital clutter and streamline your workflow through three core pillars:

1. **Automated Organization:** Say goodbye to manual sorting. The tool runs in the background, continuously monitoring your specified folders and organizing files the moment they land, saving you time and mental effort.

2. **Highly Customizable:** Every user has a different workflow. With the rules.json file, you have full control. Define your own rules based on file extensions, keywords, or specific patterns to ensure the automation fits your personal needs perfectly.

3. **Transparent Logging:** Stay in control of your data. Every action taken by the automation is recorded in automation_log.txt. This provides peace of mind, allowing you to audit file movements and ensure everything is placed exactly where it should be.


### License
This project is licensed under the MIT License. See the LICENSE file for more details. Copyright (c) 2026 Γρηγόριος Ιωσηφίδης
