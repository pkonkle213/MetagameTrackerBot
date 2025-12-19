import discord
from discord import app_commands
from discord.ext import commands

# Define the list of allowed user IDs (replace with actual IDs)
ALLOWED_USER_IDS = {
    153591222148136970,  #Adrian
    #505548744444477441, #Me
}

# Define a custom check function
def is_allowed_user():
  async def predicate(interaction: discord.Interaction) -> bool:
    if interaction.user.id in ALLOWED_USER_IDS:
      return True
    # If the check fails, an app_commands.CheckFailure exception is raised
    # which you can handle in an error handler.
    return False

  return app_commands.check(predicate)
