import discord
from discord.ext import commands
from discord import app_commands, Interaction
import settings
from services.events_reported_services import GetMyEventsReported
from output_builder import BuildTableOutput
from checks import isPhil
from discord_messages import Error

TARGET_GUILDS = [settings.BOTGUILD.id]

class EventsReported(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='eventsreported',
                        description='See how well events are reported')
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  @app_commands.check(isPhil)
  async def MyEventsReported(self, interaction: Interaction, discord_id:str = ''):
    '''
    Parameters:
    ----------
    discord_id: string
      The discord id of the store to check
    '''
    await interaction.response.defer()
    try:
      discord_id_int = 0
      if discord_id != '':
        discord_id_int = int(discord_id)
      data, title, headers = GetMyEventsReported(interaction, discord_id_int)
      output = BuildTableOutput(title, headers, data)
      await interaction.followup.send(output)
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, exception)

async def setup(bot):
  await bot.add_cog(EventsReported(bot))