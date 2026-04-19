from input_modals.map_region_modal import MapRegionModal
from data.hubs_data import GetRegions
from custom_errors import KnownError
from input_modals.map_game_modal import MapGameModal
from input_modals.map_format_modal import MapFormatModal
from interaction_objects import GetObjectsFromInteraction
from discord.ext import commands
from discord import app_commands, Interaction
from services.formats_services import AddStoreFormatMap, GetFormatOptions
from services.game_mapper_services import AddStoreGameMap, GetGameOptions
from services.command_error_service import Error
from data.interaction_data import GetHub
from services.map_claim_feed import MapClaimFeed
from checks import isPhil, IsStore, IsHub

class MappingCommands(commands.GroupCog, name='map'):
  """A group of commands for mapping channels to games, formats, and claim feeds"""
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='archetype_feed',
                        description='Map this channel as feed for submitted archetypes in this game')
  @app_commands.checks.has_role("MTSubmitter")
  @app_commands.guild_only()
  @IsStore()
  async def AddClaimFeedMap(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True, thinking=False)
    output = MapClaimFeed(interaction)
    await interaction.followup.send(output, ephemeral=True)


  @app_commands.command(name='region',
                       description='Map your channel to a region')
  @app_commands.checks.has_role("MTSubmitter")
  @app_commands.guild_only()
  @IsHub()
  async def AddRegionMap(self, interaction: Interaction):
    if not interaction.guild_id:
      raise KnownError('No guild found.')
    hub = GetHub(interaction.guild_id)
    if not hub:
      raise KnownError('No hub found. Please register your hub.')
    if not hub.format_lock:
      raise KnownError('This hub does not have format locking enabled.')
    regions = GetRegions(hub)
    if not regions or len(regions) == 0:
      raise KnownError('No regions found. Please contact the bot owner.')
    modal = MapRegionModal(hub, regions)
    await interaction.response.send_modal(modal)
    await modal.wait()

  
  @app_commands.command(name='game',
                        description='Map your category to a game')
  @app_commands.checks.has_role("MTSubmitter")
  @app_commands.guild_only()
  @IsStore()
  async def AddGameMap(self, interaction: Interaction):
    store, game, format = GetObjectsFromInteraction(interaction)
    modal = MapGameModal(store)
    await interaction.response.send_modal(modal)
    await modal.wait()
    
  @app_commands.command(name='format',
                    description='Map your channel to a format')
  @app_commands.checks.has_role("MTSubmitter")
  @app_commands.guild_only()
  @IsStore()
  async def AddFormatMap(self, interaction: Interaction):
    store, game, format = GetObjectsFromInteraction(interaction)
    if not game:
      raise KnownError('No game found. Please map a game to this category first.')
    modal = MapFormatModal(store, game)
    await interaction.response.send_modal(modal)
    await modal.wait()

  @AddClaimFeedMap.error
  @AddGameMap.error
  @AddFormatMap.error
  async def Errors(self,
                 interaction: Interaction,
                 error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)
    
async def setup(bot):
  await bot.add_cog(MappingCommands(bot))