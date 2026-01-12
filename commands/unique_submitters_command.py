import discord
from discord.ext import commands
from discord import app_commands, Interaction
from settings import BOTGUILDID
from services.unique_submitter_service import GetUniqueSubmitters
from output_builder import BuildTableOutput
from checks import isPhil
from services.command_error_service import Error

class UniqueSubmitters(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='uniquesubmitters',
                        description='See how many unique submitters there are')
  @app_commands.guilds(discord.Object(id=BOTGUILDID))
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
    data, title, headers = GetUniqueSubmitters(interaction, discord_id_int)
    output = BuildTableOutput(title, headers, data)
    await interaction.followup.send(output)

  @MyEventsReported.error
  async def Errors(self,
                   interaction: discord.Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)

async def setup(bot):
  await bot.add_cog(UniqueSubmitters(bot))