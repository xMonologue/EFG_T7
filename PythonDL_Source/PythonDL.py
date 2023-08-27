import os
import sys
import shutil
import psutil
import zipfile
import threading
import time
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout, QProgressBar, QSizePolicy, QFileDialog, QMainWindow
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon, QPixmap
import webbrowser
import qdarktheme
import requests
import urllib.request
from bs4 import BeautifulSoup

global first_click, extract_error, stopped, cancel_button, extract_done
first_click = True
extract_error = False
stopped = False
cancel_button = False
extract_done = False

def update_progress_bar(current_size, file_size, progress_bar):
    if file_size is not None:
        progress = 0
        progress = int((int(current_size) / int(file_size)) * 100)
        progress_bar.setValue(progress)

def popup_message(title, message, icon=QMessageBox.Warning):
    popup = QMessageBox()
    popup.setWindowTitle(title)
    popup.setText(message)
    popup.setIcon(icon)
    popup.exec_()

def get_download_size(url):
    try:
        d = urllib.request.urlopen( url )
        return d.info()['Content-Length']
    except Exception as E:
        print(f"Error getting file size: {E}")
    
    return None

def get_workshop_item_info(workshop_id):
    url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
    response = requests.get(url)
    response.raise_for_status()
    content = response.text
    soup = BeautifulSoup(content, "html.parser")
    mod_name = soup.find("div", class_="workshopItemTitle").text.strip()

    return mod_name

def download_file(url, destination):
    if os.path.exists(destination):
        resume_byte_pos = os.path.getsize(destination)
    else:
        resume_byte_pos = 0

    headers = {'Range': f'bytes={resume_byte_pos}-'}

    while True:
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=5)
            response.raise_for_status()

            with open(destination, 'ab') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"File downloaded to {destination}")
            return
        except (requests.RequestException, ConnectionError) as e:
            print(f"Error occurred during download: {e}")
            if os.path.exists(destination):
                resume_byte_pos = os.path.getsize(destination)
                headers = {'Range': f'bytes={resume_byte_pos}-'}
                print(f"Resuming download from byte position {resume_byte_pos}...")
            else:
                return

def extract_progress(file_size, folder_name_path, progress_bar, label_file_size):
    time.sleep(1)
    progress_bar.setValue(0)
    
    while not extract_done:
        try:
            current_size = sum(os.path.getsize(os.path.join(folder_name_path, f)) for f in os.listdir(folder_name_path))

            if os.path.exists(f"./{folder_name_path}/zone"):
                current_size = sum(os.path.getsize(os.path.join(f"./{folder_name_path}/zone", f)) for f in os.listdir(f"./{folder_name_path}/zone"))

            update_progress_bar(current_size, file_size, progress_bar)

            label_file_size.setText(f"Extract size: {sizeof_fmt(current_size)}/{sizeof_fmt(int(file_size))}")

            QCoreApplication.processEvents()
        except Exception as error:
            print(f"Error extracting bar: {error}")

        time.sleep(0.5)

def download_item(url, destination_folder, progress_bar, speed_label, label_file_size, item_size, button_download):
    download = True

    file_name = url.split("/")[-1]
    workshop_id = file_name[:-4]

    item_type = url.split("/")[-2]
    output_dir = f"./{item_type}/{workshop_id}"

    if os.path.exists(f"./{item_type}/{file_name}"):
        try:
            item_size = get_download_size(url)
        except Exception as E:
            print(f"Error getting file size: {E}")
        zip_size = os.path.getsize(f"./{item_type}/{file_name}")
        if int(item_size) == int(zip_size):
            download = False
        else:
            os.remove(f"./{item_type}/{file_name}")

    if download == True:
        try:
            download_file(url, f"./{item_type}/{file_name}")            
        except Exception as E:
            print(f"Error downloading files: {E}")
    
    try:
        if os.path.exists(f"./{item_type}/{workshop_id}"):
            shutil.rmtree(f"./{item_type}/{workshop_id}")

        if not os.path.exists(f"./{item_type}"):
            os.makedirs(f"./{item_type}")

        os.chdir(f"./{item_type}")
    except Exception as E:
        print(f"Error removing old files: {E}")
    
    global extract_error
    global stopped
    global extract_done
    stopped = True
    extract_done = False

    try:
        with zipfile.ZipFile(f"./{file_name}") as zip:
            folder = zip.namelist()[0]
            if "/" in folder:
                folder = folder.replace('/', '')
            
            print(folder)
            extract_folder = f"./{folder}"
            uncompress_size = sum((file.file_size for file in zip.infolist()))
            
            free = psutil.disk_usage(".").free
            if(int(free) < int(uncompress_size)):
                popup_message("Error", "You do not have enought space to extract this mod. \nFree up some space and try again.")
                extract_error = True
                button_download.setText("Extract")
                return

            progress_thread = threading.Thread(target=extract_progress, args=(uncompress_size, extract_folder, progress_bar, label_file_size))
            progress_thread.daemon = True
            progress_thread.start()
            
            zip.extractall(f"./")
            progress_bar.setValue(100)
    except Exception as E:
        print(f"Error extracting files: {E}")

    extract_done = True
    time.sleep(2)
    if os.path.exists(f"./{file_name}"):
        try:
            os.remove(f"./{file_name}")
        except Exception as E:
            print(f"Error removing old files: {E}")
            
    progress_bar.setValue(100) #hotfix random bar visual issue
    label_file_size.setText(f"Extract size: {sizeof_fmt(uncompress_size)}/{sizeof_fmt(int(uncompress_size))}") #hotfix random size visual issue

    popup_message("Succeess!", "Map installed correctly! \nBo3 will be restarted to add the mod in your collection. \n\nThis will be changed later on to work without restart.")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'PythonDL.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as E:
        print(f"Error closing sofware files: {E}")

def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def check_and_update_progress(file_size, folder_name_path, progress_bar, speed_label, label_file_size, url):
    if os.path.exists(folder_name_path):
        current_size = os.path.getsize(f"{folder_name_path}")

    start_time = time.time()
    opened = False
    file_name = url.split("/")[-1]
    while not stopped:
        try:
            if os.path.exists(folder_name_path):
                current_size = os.path.getsize(f"{folder_name_path}")
                update_progress_bar(current_size, file_size, progress_bar)
                label_file_size.setText(f"Download size: {sizeof_fmt(current_size)}/{sizeof_fmt(int(file_size))}")

        except Exception as error:
            print(f"Error download bar: {error}")

        QCoreApplication.processEvents()

        time.sleep(0.5)

class DownloadThread(QThread):
    finished = pyqtSignal()

    def __init__(self, url, destination_folder, progress_bar, label_speed, label_file_size, item_size, button_download):
        super().__init__()
        self.url = url
        self.destination_folder = destination_folder
        self.progress_bar = progress_bar
        self.label_speed = label_speed
        self.label_file_size = label_file_size
        self.item_size = item_size
        self.button_download = button_download

    def run(self):
        download_item(self.url, self.destination_folder, self.progress_bar, self.label_speed, self.label_file_size, self.item_size, self.button_download)
        self.finished.emit()

class mod_installer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle('PythonDL Mod Downloader')
        self.setGeometry(100, 100, 400, 100)
        self.download = True
        if os.path.exists('bo3.ico'):
            self.setWindowIcon(QIcon('bo3.ico'))
        
        if os.path.exists("PythonDL.txt"):
            with open("PythonDL.txt", "r") as file:
                self.url = file.read()
            os.remove("pythonDL.txt") #delete fastdl url just in case - Uncomment when ready
            try:
                file_name = self.url.split("/")[-1]
                self.item_type = self.url.split("/")[-2]
                self.item_size = get_download_size(self.url)
                self.mod_name = file_name[:-4]
                self.mod_name = get_workshop_item_info(self.mod_name)
            except Exception as error:
                print(f"Error getting file name: {error}")

        layout = QVBoxLayout()

        Info_speed = QHBoxLayout()

        self.label_speed = QLabel(self.mod_name)

        Info_speed.addWidget(self.label_speed, 3)

        self.label_file_size = QLabel(f"Download size: 0B/{sizeof_fmt(int(self.item_size))}")
        Info_speed.addWidget(self.label_file_size, 1)

        InfoWidget = QWidget()
        InfoWidget.setLayout(Info_speed)
        layout.addWidget(InfoWidget)

        self.buttons_layout = QHBoxLayout()

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar, 75)
        self.progress_bar.setValue(0)

        self.download_button = QPushButton("Download")

        file_name = self.url.split("/")[-1]
        self.item_type = self.url.split("/")[-2]

        if os.path.exists(f"./{self.item_type}/{file_name}"):
            item_size = get_download_size(self.url)
            zip_size = os.path.getsize(f"./{self.item_type}/{file_name}")
            if int(item_size) == int(zip_size):
                self.download_button = QPushButton("Extract")
                self.download = False

        self.download_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.download_button.clicked.connect(self.download_mod)
        self.buttons_layout.addWidget(self.download_button, 75)

        layout.addLayout(self.buttons_layout)

        self.setLayout(layout)

    def download_mod(self):
        file_name = self.url.split("/")[-1]
        global cancel_button
        if cancel_button == False or extract_error == False:
            if extract_error == False:
                free = psutil.disk_usage(".").free
                if(int(free) < int(self.item_size)):
                    popup_message("Error", "You do not have enought space to download this mod. \nFree up some space and try again. \n\n Keep in mind you need also space to extract the downloaded archive! ")
                    return

            self.destination_folder = f"./{self.item_type}/{file_name}"
            self.download_thread = DownloadThread(self.url, self.destination_folder, self.progress_bar, self.label_speed, self.label_file_size, self.item_size, self.download_button)
            self.download_thread.start()

            if self.download:
                self.progress_thread = threading.Thread(target=check_and_update_progress, args=(self.item_size, self.destination_folder, self.progress_bar, self.label_speed, self.label_file_size, self.url))
                self.progress_thread.daemon = True
                self.progress_thread.start()

            self.download_button.setText("Cancel")
            cancel_button = True

        elif cancel_button == True:
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'PythonDL.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except Exception as error:
                print(f"Error: {error}")
            
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()
    window = mod_installer()
    window.show()

    sys.exit(app.exec_())
