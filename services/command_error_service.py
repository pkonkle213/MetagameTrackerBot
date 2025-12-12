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
  print('Error type:', type(error))
  print('IsMissingRole:', isinstance(error, app_commands.errors.MissingRole))
  print('IsCommandOnCooldown:', isinstance(error, app_commands.errors.CommandOnCooldown))
  print('IsCommandInvokeError:', isinstance(error, app_commands.errors.CommandInvokeError))
  print('IsKnownError:', isinstance(error, KnownError))
  if isinstance(error, app_commands.errors.MissingRole):
    feedback = 'You do not have the required role to use this command.'
  elif isinstance(error, app_commands.errors.CommandOnCooldown):
    feedback = str(error)
  elif isinstance(error, KnownError):
    feedback = error.message
  #elif isinstance(error, app_commands.errors.CommandInvokeError):
  #  feedback = str(error.original)
  else:
    feedback = "Something unexpected went wrong. It's been reported. Please try again in a few hours."
    await MessageChannel(bot,
                         error,
                         settings.BOTGUILDID,
                         settings.ERRORCHANNELID)
  try:
    await interaction.response.send_message(feedback, ephemeral=True)
  except Exception:
    await interaction.followup.send(feedback, ephemeral=True)
    