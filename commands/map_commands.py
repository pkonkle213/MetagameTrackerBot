from discord.ext import commands
from discord import app_commands, Interaction
from services.formats_services import AddStoreFormatMap, GetFormatOptions
from services.game_mapper_services import AddStoreGameMap, GetGameOptions
from select_menu_bones import SelectMenu
from services.command_error_service import Error
from services.map_claim_feed import MapClaimFeed

class MappingCommands(commands.GroupCog, name='map'):
  """A group of commands for mapping channels to games, formats, and claim feeds"""
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='archetypefeed',
                        description='Map this channel as feed for submitted archetypes in this game')
  @app_commands.checks.has_role("MTSubmitter")
  @app_commands.guild_only()
  async def AddClaimFeedMap(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    output = MapClaimFeed(interaction)
    await interaction.followup.send(output, ephemeral=True)
  
  @app_commands.command(name='game',
                        description='Map your category to a game')
  @app_commands.checks.has_role("MTSubmitter")
  @app_commands.guild_only()
  async def AddGameMap(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    message = 'Please select a game'
    placeholder = 'Choose a game'
    dynamic_options = GetGameOptions()
    result = await SelectMenu(interaction, message, placeholder, dynamic_options)
    print('Result:', result[0])
    output = AddStoreGameMap(interaction, result[0])
    await interaction.followup.send(output, ephemeral=True)


  @app_commands.command(name='format',
                    description='Map your channel to a format')
  @app_commands.checks.has_role("MTSubmitter")
  @app_commands.guild_only()
  async def AddFormatMap(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    dynamic_options = GetFormatOptions(interaction)
    if dynamic_options is None or len(dynamic_options) == 0:
      await interaction.followup.send('No formats found for this game')
    else:
      message = 'Please select a format'
      placeholder = 'Choose a format'
      result = await SelectMenu(interaction, message, placeholder, dynamic_options)
      output = await AddStoreFormatMap(interaction, result[0])
      await interaction.followup.send(output, ephemeral=True)


  @AddClaimFeedMap.error
  @AddGameMap.error
  @AddFormatMap.error
  async def Errors(self,
                 interaction: Interaction,
                 error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)
    
async def setup(bot):
  await bot.add_cog(MappingCommands(bot))