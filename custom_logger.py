import logging
import os
import requests
from colorlog import ColoredFormatter

class CustomLogger:
    def __init__(self, discord_webhook_url="cant share",usb = False):
        self.usb = usb
        self.log_file_path = os.path.join(os.path.expanduser("~/Desktop"), "WIN config.log")
        self.discord_webhook_url = discord_webhook_url
        self.logger = self.setup_logging()

    def setup_logging(self):
        # Create a file handler
        file_handler = logging.FileHandler(self.log_file_path)
        file_formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s [%(levelname)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={
                'levelname': {
                    'DEBUG': 'bold_cyan',
                    'INFO': 'bold_green',
                    'WARNING': 'bold_yellow',
                    'ERROR': 'bold_red',
                    'CRITICAL': 'bold_red',
                },
                'asctime': {
                    'DEBUG': 'white',
                    'INFO': 'white',
                    'WARNING': 'white',
                    'ERROR': 'white',
                    'CRITICAL': 'white',
                },
            },
            reset=True,
            style='%'
        )
        if not self.usb:
            file_handler.setFormatter(file_formatter)

        # Create a stream handler (to print to console)
        stream_handler = logging.StreamHandler()
        stream_formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s [%(levelname)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={
                'levelname': {
                    'DEBUG': 'bold_cyan',
                    'INFO': 'bold_green',
                    'WARNING': 'bold_yellow',
                    'ERROR': 'bold_red',
                    'CRITICAL': 'bold_red',
                },
                'asctime': {
                    'DEBUG': 'white',
                    'INFO': 'white',
                    'WARNING': 'white',
                    'ERROR': 'white',
                    'CRITICAL': 'white',
                },
            },
            reset=True,
            style='%'
        )
        stream_handler.setFormatter(stream_formatter)

        # Get the root logger and add both handlers
        logger = logging.getLogger()
        logger.addHandler(file_handler)
        if not self.usb:    
            logger.addHandler(stream_handler)
        logger.setLevel(logging.INFO)
        logger.info("Logging configured successfully.")
        return logger

    def _send_to_discord(self, record):
        level_colors = {
            'DEBUG': 0x3498db,   # Blue
            'INFO': 0x2ecc71,    # Green
            'WARNING': 0xf1c40f, # Yellow
            'ERROR': 0xe74c3c,   # Red
        }

        payload = {
            "content": f"**{record.levelname}**: {record.getMessage()}",
            "embeds": [{
                "color": level_colors.get(record.levelname, 0x95a5a6),
                "description": f"**{record.levelname}**: {record.getMessage()}",
            }]
        }

        try:
            requests.post(self.discord_webhook_url, json=payload)
        except requests.exceptions.RequestException as e:
            print(f"Error sending message to Discord: {e}")

    def log(self, message):
        self.logger.info(message)
        log_record = self.logger.makeRecord(
            "INFO",
            logging.INFO,
            __file__,
            0,
            message,
            None,
            None,
            func=None,
        )
        self._send_to_discord(log_record)
        if self.usb:
            print(F"Info for usb monitor  :{message}")

    def log_error(self, message):
        self.logger.error(message)
        log_record = self.logger.makeRecord(
            "ERROR",
            logging.ERROR,
            __file__,
            0,
            message,
            None,
            None,
            func=None,
        )
        self._send_to_discord(log_record)
        if self.usb:
            print(F"Error for usb monitor  :{message}")

    def log_warning(self, message):
        self.logger.warning(message)
        log_record = self.logger.makeRecord(
            "WARNING",
            logging.WARNING,
            __file__,
            0,
            message,
            None,
            None,
            func=None,
        )
        self._send_to_discord(log_record)
        if self.usb:
            print(F"Error Warning for usb monitor  :{message}")

    def log_debug(self, message):
        self.logger.debug(message)
        log_record = self.logger.makeRecord(
            "DEBUG",
            logging.DEBUG,
            __file__,
            0,
            message,
            None,
            None,
            func=None,
        )
        self._send_to_discord(log_record)
        if self.usb:
            print(F"Debug for usb monitor  :{message}")

# Example usage:
if __name__ == "__main__":
    log_file_path = "Rklog.log"
    discord_webhook_url = "https://discord.com/api/webhooks/1172792490131202048/eg7QsvbdM94xDlDALtfC8ENpO-kqPAAKxNgJy2vSc8jqYDDUAlSp91TLdCcmHOHOD6Va"
    logger = CustomLogger(discord_webhook_url)

    logger.log("This is an info message.")
    logger.log_error("This is an error message.")
    logger.log_warning("This is a warning message.")
    logger.log_debug("This is a debug message.")
