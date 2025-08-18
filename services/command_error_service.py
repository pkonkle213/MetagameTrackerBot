from discord.ext import commands
from discord_messages import MessageChannel
import settings

async def MissingRoleError(interaction, error):
  if isinstance(error, commands.MissingRole):
    await interaction.response.send_message('You do not have the required role to use this command.', ephemeral=True)
  else:
    await interaction.response.send_message('Catch this:', type(error), ephemeral=True)

async def Error(bot, interaction, error):
  await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
  await MessageChannel(bot,
                       error,
                       settings.BOTGUILDID,
                       settings.ERRORCHANNELID)