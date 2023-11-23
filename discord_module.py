import requests
import time

class DiscordHandler:
    def __init__(self, webhook_url,logger):
        self.webhook_url = webhook_url
        self.logger = logger

    def _send_request(self, payload):
        retries = 3  # Number of retry attempts
        for _ in range(retries):
            try:
                response = requests.post(self.webhook_url, json=payload)
                if response.status_code == 204:
                    return  # Request successful
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                self.logger.log_error(f"Error: {e}")
            time.sleep(5)  # Wait for 5 seconds before retrying
        self.logger.log_error("Failed to send message to Discord after multiple attempts.")

    def send_text_message(self, content, username=None, avatar_url=None):
        payload = {
            "content": content,
            "username": username,
            "avatar_url": avatar_url
        }
        self._send_request(payload)
        self.logger.log(f"Message sent to Discord: {content}")

    def send_embed(self, embed, username=None, avatar_url=None):
        payload = {
            "embeds": [embed],
            "username": username,
            "avatar_url": avatar_url
        }
        self._send_request(payload)
        self.logger.log(payload)

    def send_file(self, file_path, content=None, username=None, avatar_url=None):
        try:
            files = {"file": open(file_path, "rb")}
            payload = {
                "content": content,
                "username": username,
                "avatar_url": avatar_url
            }
            response = requests.post(self.webhook_url, data=payload, files=files)
            self.logger.log(f"File sent: {file_path};content:{content}")
            if response.status_code != 200:
                print(f"Failed to send file. Status code: {response.status_code}")
                self.logger.log_error(f"Failed to send file. Status code: {response.status_code}")
            return response
        except Exception as e:
            self.logger.log_error(f"error occurred while sending file: {str(e)}")

    def send_error_report(self, log_file_path=None):
        if log_file_path:
            self.send_file(log_file_path, "Error Report")
            self.logger.log(f"Error report sent to Discord: {log_file_path}")
        else:
            self.logger.log_error("Log file path not provided for error report.")

# Example usage of the DiscordHandler module
if __name__ == "__main__":
    webhook_url = "YOUR_WEBHOOK_URL"
    discord_handler = DiscordHandler(webhook_url)
    discord_handler.send_text_message("Hello, Discord!")
    discord_handler.send_embed({
        "title": "Embed Title",
        "description": "This is an example embed message.",
        "color": 0x00ff00
    })
    discord_handler.send_file("example.txt", "Check out this file!")
    discord_handler.send_error_report(log_file_path="C:\\Users\\vinay\\Desktop\\WIN config.log")
