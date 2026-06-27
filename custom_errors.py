from discord import app_commands

class KnownError(app_commands.AppCommandError):
  def __init__(self, message:str):
    self.message = message
    super().__init__(self.message)