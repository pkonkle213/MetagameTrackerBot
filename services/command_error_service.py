from discord.ext.commands import Bot
from custom_errors import KnownError
from discord_messages import MessageChannel
from discord import app_commands, Interaction
import settings
import traceback

async def Error(bot:Bot,
                interaction:Interaction,
                error:app_commands.AppCommandError | Exception):
  print('Error type:', type(error))
  print('IsMissingRole:', isinstance(error, app_commands.errors.MissingRole))
  print('IsCommandOnCooldown:', isinstance(error, app_commands.errors.CommandOnCooldown))
  print('IsCommandInvokeError:', isinstance(error, app_commands.errors.CommandInvokeError))
  print('IsKnownError:', isinstance(error, KnownError))
  print('IsCheckFailure:', isinstance(error, app_commands.errors.CheckFailure))
  if isinstance(error, app_commands.errors.MissingRole):
    feedback = 'You do not have the required role to use this command.'
  elif isinstance(error, app_commands.errors.CommandOnCooldown):
    feedback = str(error)
  elif isinstance(error, app_commands.errors.CheckFailure):
    feedback = str(error)
  elif isinstance(error, KnownError):
    feedback = error.message
  else:
    original_error = getattr(error, 'original', error)
    error_traceback = "".join(traceback.format_exception(
        type(original_error), original_error, original_error.__traceback__
    ))
    error_traceback = error_traceback[:2000]
    feedback = "Something unexpected went wrong. It's been reported. Please try again in a few hours."
    await MessageChannel(bot,
                         error_traceback,
                         settings.BOTGUILDID,
                         settings.ERRORCHANNELID)
  try:
    await interaction.response.send_message(feedback, ephemeral=True)
  except Exception:
    await interaction.followup.send(feedback, ephemeral=True)
    