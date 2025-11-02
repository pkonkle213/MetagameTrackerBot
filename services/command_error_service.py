from discord.ext.commands import Bot
from custom_errors import KnownError
from discord_messages import MessageChannel
from discord import app_commands, Interaction
import settings

async def MissingRoleError(interaction, error:app_commands.AppCommandError):
  if isinstance(error, app_commands.MissingRole):
    await interaction.response.send_message('You do not have the required role to use this command.', ephemeral=True)
  elif isinstance(error, KnownError):
    await interaction.response.send_message(error.message, ephemeral=True)
  else:
    await interaction.response.send_message('Catch this:', type(error), ephemeral=True)

async def Error(bot:Bot,
                interaction:Interaction,
                error:app_commands.AppCommandError):
  if isinstance(error, app_commands.MissingRole):
    await interaction.followup.send('You do not have the required role to use this command.', ephemeral=True)
  elif isinstance(error, app_commands.CommandOnCooldown):
    await interaction.response.send_message(str(error), ephemeral=True)
  elif isinstance(error, app_commands.CommandInvokeError):
    await interaction.followup.send(str(error.original), ephemeral=True)
  else:
    await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
    await MessageChannel(bot,
                         error,
                         settings.BOTGUILDID,
                         settings.ERRORCHANNELID)
