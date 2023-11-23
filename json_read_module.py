import os
import json

class JSONReader:
    def __init__(self, file_name):
        self.file_name = file_name
        self.file_path = self.find_file_in_directory(file_name)
        if not self.file_path:
            self.json_data = {
        "FileMonitor": {
            "discord_webhook_url": "cant share",
            "monitored_dirs": ["Desktop", "Downloads"],
            "ignore_list": [
                "C:\\Users\\YourUsername\\Documents\\PrivateFolder",
                "C:\\Some\\Other\\Folder\\To\\Ignore"
            ]
        },
        "USBDriveMonitor": {
            "log_file_path": "Rklog.log",
            "discord_webhook_url": "cant share",
            "allowed_extensions": ["txt", "pdf", "docx", "doc", "zip"],
            "destination_folder_base": "Pendrive",
            "skip_drives": []
        },
        "DiscordBotModule": {
            "WEBHOOK_URL": "cant share",
            "token": "cant share",
            "ALLOWED_EXTENSIONS": [".txt", ".pdf", ".png", ".jpg", ".jpeg", ".mp4", ".mp3", ".mkv", ".docx", ".xls"]
        },
        "Intilize": {
            "discord_webhook_url": "cant share",
            "DISCORD_BOT_TOKEN": "cant share",
            "icon_name": "icon.png",
            "task_bar_icon_url": "https://avatars.githubusercontent.com/u/110547855?v=4"
        }
        }
    
            self.dump_json_to_file(file_name,self.json_data) #make a json file if there is none
            self.file_path = self.find_file_in_directory(file_name)


        self.data = None


    def check_valid_json(self,file_path):
        try:
            with open(file_path, 'r') as file:
                json.load(file)
            return True
        except (json.JSONDecodeError, FileNotFoundError):
            return False

    def dump_json_to_file(self,file_name, json_data):
        try:
            # Get the current working directory
            current_directory = os.getcwd()

            # Create the full path to the file
            file_path = os.path.join(current_directory, file_name)

            # Check if the file exists and has a valid JSON format
            if not self.check_valid_json(file_path):
                # If not, create the file and dump the JSON data
                with open(file_path, 'w') as file:
                    json.dump(json_data, file, indent=2)
                print(f"JSON data dumped into file '{file_name}' successfully.")
            else:
                print(f"File '{file_name}' already exists and has a valid JSON format. Skipping dump.")
        
        except Exception as e:
            print(f"An error occurred: {e}")


    def _load_data(self):
        if self.file_path is None:
            self.dump_json_to_file(self.file_name,self.json_data)

        try:
            with open(self.file_path) as f:
                self.data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON format in file: {self.file_path}") from e

    def find_file_in_directory(self, file_name):
        for root, dirs, files in os.walk("."):
            if file_name in files:
                return os.path.join(root, file_name)
        return None

    def get_value(self, key, default=None):
        if self.data is None:
            self._load_data()

        return self.data.get(key, default)

    def get_all_keys(self):
        if self.data is None:
            self._load_data()

        return list(self.data.keys())
    
    def get_json_string(self, key):
        if self.data is None:
            self._load_data()

        if key in self.data:
            return json.dumps(self.data[key])
        else:
            raise KeyError(f"Key '{key}' not found in the JSON data.")


class JSONParser:
    def __init__(self, json_string):
        self.json_string = json_string
        self.data = None

    def _load_data(self):
        try:
            self.data = json.loads(self.json_string)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError("Invalid JSON format") from e

    def get_value(self, key, default=None):
        if self.data is None:
            self._load_data()

        return self.data.get(key, default)
    
