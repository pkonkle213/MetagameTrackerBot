import discord
from discord.ext import commands
from discord import app_commands, Interaction
from settings import BOTGUILDID
from services.events_reported_services import GetMyEventsReported
from output_builder import BuildTableOutput
from checks import isPhil
from services.command_error_service import Error

TARGET_GUILDS = [BOTGUILDID]

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
    discord_id_int = 0
    if discord_id != '':
      discord_id_int = int(discord_id)
    data, title, headers = GetMyEventsReported(interaction, discord_id_int)
    output = BuildTableOutput(title, headers, data)
    await interaction.followup.send(output)
    
  @MyEventsReported.error
  async def Errors(self,
                   interaction: discord.Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)

async def setup(bot):
  await bot.add_cog(EventsReported(bot))