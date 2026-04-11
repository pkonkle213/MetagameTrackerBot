from tuple_conversions import League
from discord_messages import MessageChannel
from services.command_error_service import Error
from discord.ext import commands
from discord import app_commands, Interaction
from services.league_services import CreateLeague, EditLeague
from checks import isStore

class LeaguesCommands(commands.GroupCog, name='league'):
  """A group of commands for managing Leagues"""

  def __init__(self, bot:commands.Bot):
     self.bot = bot

  async def OutputLeagueDetails(self, interaction: Interaction, league: League, isEdited:bool = False):
    title = "New league created!" if not isEdited else "League updated!"
    title += "\n-------------------" 
    output = f'''{title}
    League Name: {league.name}
    Start Date: {league.start_date.strftime("%m/%d/%Y")}
    End Date: {league.end_date.strftime("%m/%d/%Y")}
    Cuts to Top: {league.top_cut}
    Description: {league.description}'''

    await MessageChannel(self.bot, output, interaction.guild_id, interaction.channel_id)
  
  @app_commands.command(name='create',
                       description='Create a new league')
  @app_commands.guild_only()
  @isStore()
  @app_commands.checks.has_role('MTSubmitter')
  async def CreateLeague(self, interaction: Interaction):
    league = await CreateLeague(self.bot, interaction)
    await self.OutputLeagueDetails(interaction, league)
    
  @app_commands.command(name='edit',
                       description='Exit an existing league')
  @app_commands.guild_only()
  @app_commands.checks.has_role('MTSubmitter')
  async def EditLeague(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)
    league = await EditLeague(self.bot, interaction)
    print('League:', league)
    await self.OutputLeagueDetails(interaction, league, True)
  
  @app_commands.command(name='top',
                       description='Display the top players in a league')
  @app_commands.guild_only()
  async def TopPlayers(self, interaction: Interaction):
    ...
  
  @app_commands.command(name='metagame',
                       description='Display the metagame of a league')
  @app_commands.guild_only()
  async def LeagueMeta(self, interaction: Interaction):
    ...


  @app_commands.command(name='my_status',
                       description='Shows how you compare to the top players in a league')
  @app_commands.guild_only()
  async def MyStatus(self, interaction: Interaction):
    ...

  @CreateLeague.error
  @EditLeague.error
  @TopPlayers.error
  @LeagueMeta.error
  @MyStatus.error
  async def Errors(self,
                   interaction: Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)
  

async def setup(bot:commands.Bot):
  await bot.add_cog(LeaguesCommands(bot))