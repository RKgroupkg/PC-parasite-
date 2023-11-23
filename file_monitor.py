import time
import os 
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from discord_module import DiscordHandler
from json_read_module import JSONReader,JSONParser

from custom_logger import CustomLogger
from FLAG import BotEnvironmentVariable

class FileMonitor(FileSystemEventHandler):
    def __init__(self, discord_handler, monitored_folders, logger, ignore_list=None):
        super(FileMonitor, self).__init__()
        self.discord_handler = discord_handler
        self.monitored_folders = monitored_folders
        self.logger = logger
        self.script_directory = os.path.dirname(os.path.abspath(__file__))
        self.ignore_list = ignore_list or []


    def should_ignore_event(self, event):
        # Check if the event occurred in one of the system folders or the script's directory
        folders_to_ignore = ["C:\\Windows\\", "C:\\Program Files\\", "C:\\Program Files (x86)\\", self.script_directory]
        return any(event.src_path.lower().startswith(folder.lower()) for folder in folders_to_ignore) or \
               event.src_path.lower().endswith('.log')

    def on_any_event(self, event):
        try:
            if self.should_ignore_event(event) or event.is_directory:
                return  # Ignore system files, directory events, and log files

            event_type = event.event_type
            file_path = os.path.relpath(event.src_path, max(self.monitored_folders, key=len))

            if event_type == 'modified':
                message = f"File {file_path} has been modified."
            elif event_type == 'created':
                message = f"File {file_path} has been added."
            elif event_type == 'deleted':
                message = f"File {file_path} has been deleted."
                self.discord_handler.send_text_message(content=message)
                return
            elif event_type == 'moved':
                dest_path = os.path.relpath(event.dest_path, max(self.monitored_folders, key=len))
                if not os.path.exists(dest_path):
                    message = f"File {file_path} has been moved, but the destination file no longer exists."
                else:
                    message = f"File {file_path} has been moved to {dest_path}."
                    # Check if the file still exists before sending
                    if os.path.exists(event.src_path):
                        self.discord_handler.send_file(event.src_path, content=message)
            else:
                message = f"Unknown event type for file {file_path}: {event_type}"

            self.discord_handler.send_file(event.src_path, content=message)

        except Exception as e:
            self.logger.log_error(f"Fatal error occurred: {str(e)}")
def load_settings(json_reader, file_name):
    settings_json_string = json_reader.get_json_string(file_name)
    setting = JSONParser(settings_json_string)
    return setting

def start_file_monitoring(settings, logger, bot_env_var):
    try:
        discord_webhook_url = settings.get_value("discord_webhook_url")
        monitored_dirs = settings.get_value("monitored_dirs")
        ignore_list = settings.get_value("ignore_list", [])
        print(f"discord_webhook_url:{discord_webhook_url},monitored_dirs:{monitored_dirs},ignore_list:{ignore_list}")
        if not discord_webhook_url:
            raise ValueError("Discord webhook URL not provided in settings.")

        if not monitored_dirs:
            raise ValueError("No monitored directories specified in settings.")

        monitored_folders = [os.path.join(os.path.expanduser("~"), dir_name) for dir_name in monitored_dirs]

        discord_handler = DiscordHandler(discord_webhook_url, logger)
        event_handler = FileMonitor(discord_handler, monitored_folders, logger, ignore_list=ignore_list)
        observer = Observer()

        for folder in monitored_folders:
            observer.schedule(event_handler, path=folder, recursive=True)

        observer.start()
        logger.log("File monitoring started")
    except Exception as e:
        logger.log_error(f"Fatal error occurred: {str(e)}")

    try:
        while bot_env_var.check_bot_run_status():
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    logger.log("File monitoring stoped")   
    observer.stop()
    observer.join()


if __name__ == "__main__":
    file_name = "Malware_config"  # Replace with the actual JSON settings file
    json_reader = JSONReader(file_name)
    settings = load_settings(json_reader, "FileMonitor")


    bot_env_var = BotEnvironmentVariable("NOTES_BOT_RUN")
    logger = CustomLogger()
    
    start_file_monitoring(settings, logger, bot_env_var)
