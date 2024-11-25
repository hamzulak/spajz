import os
import time
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('file_monitor.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Global variables
original_files = {}
directory = ""  # Global variable for the directory
observer = None
monitoring_active = True

def convert_files_to_ham(directory):
    global original_files
    original_files = {}
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            if os.path.isfile(file_path):
                base, ext = os.path.splitext(file_path)
                if ext not in ['.ham', '.bhcrow']:
                    ham_path = base + '.ham'
                    if not os.path.exists(ham_path):
                        original_files[ham_path] = ext
                        try:
                            os.rename(file_path, ham_path)
                            log_message(f"Converted to .ham: {ham_path}")
                        except Exception as e:
                            log_message(f"Error processing file {file_path}: {e}")
                    else:
                        log_message(f"Skipped: {ham_path} already exists")
    return original_files

class FileRenameHandler(FileSystemEventHandler):
    def __init__(self, directory):
        self.directory = directory
        self.reverted_files = set()

    def process(self, event):
        if event.event_type == 'created':
            new_file_path = event.src_path
            if os.path.basename(new_file_path) == "volimtebabo.bhcrow":
                log_message("volimtebabo.bhcrow detected. Stopping monitoring, reverting all files, and shutting down.")
                self.stop_monitoring()
                self.revert_files()
                self.create_najvisenasvijetu_txt()
                window.after(5000, self.shutdown)
            else:
                try:
                    base, ext = os.path.splitext(new_file_path)
                    if ext not in ['.ham', '.bhcrow']:
                        ham_path = base + '.ham'
                        if os.path.exists(new_file_path):
                            os.rename(new_file_path, ham_path)
                            log_message(f"Converted to .ham: {ham_path}")
                            original_files[ham_path] = ext
                except Exception as e:
                    log_message(f"Error converting file {new_file_path}: {e}")

    def on_created(self, event):
        self.process(event)

    def stop_monitoring(self):
        global monitoring_active
        monitoring_active = False
        observer.stop()

    def revert_files(self):
        global original_files
        for ham_path, original_extension in original_files.items():
            original_path = ham_path.replace('.ham', original_extension)
            if original_path not in self.reverted_files:
                try:
                    if os.path.exists(ham_path):
                        os.rename(ham_path, original_path)
                        log_message(f"Reverted: {ham_path} -> {original_path}")
                        self.reverted_files.add(original_path)
                except Exception as e:
                    log_message(f"Error reverting file {ham_path}: {e}")

    def create_najvisenasvijetu_txt(self):
        txt_path = os.path.join(self.directory, "najvisenasvijetu.txt")
        try:
            with open(txt_path, "w") as f:
                f.write("Monitoring stopped. All files reverted to their original state.")
            log_message(f"Created: {txt_path}")
        except Exception as e:
            log_message(f"Error creating najvisenasvijetu.txt: {e}")

    def shutdown(self):
        log_message("Shutting down the application.")
        window.destroy()

def monitor_directory(directory):
    event_handler = FileRenameHandler(directory)
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()

    try:
        while monitoring_active:
            for root, _, files in os.walk(directory):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    base, ext = os.path.splitext(file_path)
                    if ext not in ['.ham', '.bhcrow']:
                        ham_path = base + '.ham'
                        if os.path.exists(file_path):
                            if not os.path.exists(ham_path):
                                os.rename(file_path, ham_path)
                                log_message(f"Converted to .ham: {ham_path}")
            time.sleep(1)
    except Exception as e:
        log_message(f"Error in monitoring loop: {e}")

def start_monitoring(directory):
    global original_files
    original_files = convert_files_to_ham(directory)
    global observer
    observer = Observer()
    monitor_directory(directory)

def on_directory_selected():
    global directory
    directory = filedialog.askdirectory()
    if directory:
        log_message(f"Monitoring directory: {directory}")
        threading.Thread(target=start_monitoring, args=(directory,), daemon=True).start()

def log_message(message):
    logger.info(message)
    text_area.insert(tk.END, message + '\n')
    text_area.yview(tk.END)

# Create the main UI window
window = tk.Tk()
window.title("HADES")
window.geometry("600x500")
window.configure(bg='black')

# Add a label and a button to ask for the directory
label = tk.Label(window, text="Select a directory to monitor:", bg='black', fg='red')
label.pack(pady=20)

button = tk.Button(window, text="Select Directory", command=on_directory_selected, bg='black', fg='red')
button.pack()

# Add a text area for logs
text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, bg='black', fg='red')
text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

# Start the GUI loop
window.mainloop()
