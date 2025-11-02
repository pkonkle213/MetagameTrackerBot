import discord
from discord import app_commands
from discord.ext import commands
from services.personal_history_service import GetPersonalStandingsHistory, GetPersonalPairingsHistory
from services.store_level_service import LEVELINFSTORES
from services.command_error_service import Error

TARGET_GUILD_IDS = LEVELINFSTORES

class PersonalHistoryCommands(commands.GroupCog, name='history'):
  """A group of commands for getting personal history"""
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='standings', description='Your history according to standings')
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in LEVELINFSTORES])
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  async def GetPersonalStandingsHistory(self,
                                        interaction:discord.Interaction,
                                        start_date: str = '',
                                        end_date: str = ''):
    """
    Parameters
    ----------
    start_date: string
      Beginning of Date Range (MM/DD/YYYY)
    end_date: string
      End of Date Range (MM/DD/YYYY)
    """
      
    await interaction.response.defer(ephemeral=True)
    output = GetPersonalStandingsHistory(interaction, start_date, end_date)
    await interaction.followup.send(output, ephemeral=True)

  @app_commands.command(name='pairings', description='Your history according to pairings')
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in LEVELINFSTORES])
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  async def GetPersonalPairingsHistory(self,
                                        interaction:discord.Interaction,
                                        start_date: str = '',
                                        end_date: str = ''):
    """
    Parameters
    ----------
    start_date: string
      Beginning of Date Range (MM/DD/YYYY)
    end_date: string
      End of Date Range (MM/DD/YYYY)
    """

    await interaction.response.defer(ephemeral=True)
    output = GetPersonalPairingsHistory(interaction, start_date, end_date)
    await interaction.followup.send(output, ephemeral=True)


  @GetPersonalStandingsHistory.error
  @GetPersonalPairingsHistory.error
  async def Errors(self,
                 interaction: discord.Interaction,
                 error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)

async def setup(bot):
  await bot.add_cog(PersonalHistoryCommands(bot))