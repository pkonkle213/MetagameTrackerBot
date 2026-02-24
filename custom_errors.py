from discord import app_commands

#TODO: I would like a second message, one to be sent to the user and one to be sent to me in my errors channel
class KnownError(app_commands.AppCommandError):
  def __init__(self, message):
    self.message = message
    super().__init__(self.message)