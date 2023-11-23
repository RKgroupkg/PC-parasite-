import os

class BotEnvironmentVariable:
    def __init__(self, env_var_name):
        self.env_var_name = env_var_name
        self.initialize_bot_variable()

    def set_bot_run_status(self, value):
        """
        Set the value of the environment variable.

        Args:
            value (bool): The boolean value to set.
        """
        os.environ[self.env_var_name] = str(value)

    def get_bot_run_status(self):
        """
        Get the value of the environment variable.

        Returns:
            bool: The boolean value of the environment variable. Returns False if the variable is not set.
        """
        return os.getenv(self.env_var_name, "False").lower() == "true"

    def check_bot_run_status(self):
        """
        Check the status of the environment variable.

        Returns:
            bool: True if the variable is set to True, False otherwise.
        """
        return self.get_bot_run_status()

    def initialize_bot_variable(self):
        """
        Initialize the environment variable if it doesn't exist.
        """
        if self.env_var_name not in os.environ:
            self.set_bot_run_status(True)

# Example usage:
# Create an instance of the class
bot_env_var = BotEnvironmentVariable("NOTES_BOT_RUN")

# Check the status
if bot_env_var.check_bot_run_status():
    print("Bot is set to run.")
else:
    print("Bot is not set to run.")
