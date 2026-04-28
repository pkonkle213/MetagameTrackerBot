from data.player_name_data import GetUserArchetypes, GetUserName
import typing
from services.determine_archetype_input import GetUserInput
from api_calls.melee_tournaments import GetMeleeTournamentData
import settings
from input_modals.submit_data_modal import SubmitDataModal
from checks import isSubmitter, IsStore
from custom_errors import KnownError
from discord import app_commands, Interaction, Attachment
from discord.ext import commands
from discord_messages import MessageChannel
from interaction_objects import GetObjectsFromInteraction
from services.add_results_services import SubmitData
from services.command_error_service import Error
from services.message_hubs_services import MessageHubs
from tuple_conversions import InteractionObjects
from data.event_data import GetHubEvents, GetStoreEvents

class SubmitDataChecker(commands.GroupCog, name='submit'):
  """A group of commands to submit data"""

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="check",
                        description="To test if you can submit data")
  @app_commands.guild_only()
  @IsStore()
  @app_commands.checks.cooldown(1, 300.0, key=lambda i: (i.guild_id, i.user.id))
  async def SubmitCheck(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True, thinking=False)
    issues = ['Issues I detect:']
    objects = GetObjectsFromInteraction(interaction)

    if not objects.store:
      issues.append('- Store not registered')
    if not isSubmitter(interaction.guild, interaction.user, 'MTSubmitter'):
      issues.append("- You don't have the MTSubmitter role.")
    if not objects.game:
      issues.append('- Category not mapped to a game')
    if objects.game and not format:
      issues.append('- Channel not mapped to a format')

    if len(issues) == 1:
      await interaction.followup.send('Everything looks good. Please reach out to Phil to test your data')
    else:
      await interaction.followup.send('\n'.join(issues))

  @app_commands.command(name="archetype",
                        description="Submit a player's archetype for an event")
  @app_commands.guild_only()
  async def SubmitArchetypeCommand(self, interaction: Interaction):
    objects = GetObjectsFromInteraction(interaction)
    userId = interaction.user.id

    if (not objects.store and not objects.hub) or not objects.game or not objects.format:
      raise KnownError('No store, hub, game, or format found.')
    guild_id = interaction.guild_id
    channel_id = interaction.channel_id

    if not guild_id or not channel_id:
      raise KnownError('No guild or channel found.')
    
    player_name = GetUserName(userId)
    player_archetypes = GetUserArchetypes(userId, objects.game, objects.format)

    if objects.hub:
      events = GetHubEvents(guild_id, channel_id)
    elif objects.store:
      events = GetStoreEvents(objects.store, objects.game, objects.format)
    else:
      raise KnownError('No store or hub found.')

    await GetUserInput(self.bot,
                       userId,
                       events,
                       interaction,
                       objects.game,
                       objects.format,
                       player_name,
                       player_archetypes)

  @app_commands.command(
    name="data",
    description="Submitting your event's data"
  )
  @app_commands.checks.has_role('MTSubmitter')
  @app_commands.guild_only()
  @IsStore()
  async def SubmitDataCommand(
    self,
    interaction: Interaction,
    csv_file: typing.Optional[Attachment] = None,
    melee_tournament_id: str = ''
  ) -> None:
    """
    Parameters
    ----------    
    csv_file: Attachment
      The CSV file containing the event's data from CARDE.IO
      
    melee_tournament_id: str
      The Melee Tournament ID for the event
    """
    #Ensure that only one type of data is being submitted
    if csv_file and melee_tournament_id:
      raise KnownError("You can only submit a CSV file or a Melee Tournament ID, not both.")

    objects = GetObjectsFromInteraction(interaction)
    
    if not objects.store or not objects.game or not objects.format:
      raise KnownError('No store, game, or format found.') #TODO Probably needs to be more detailed
      
    data = False if csv_file or melee_tournament_id else True
    
    modal = SubmitDataModal(
      self.bot,
      objects.store,
      objects.game,
      objects.format,
      data,
      csv_file,
      melee_tournament_id
    )
    await interaction.response.send_modal(modal)
    await modal.wait()    
    

  @SubmitCheck.error
  @SubmitDataCommand.error
  @SubmitArchetypeCommand.error
  async def Errors(self, interaction: Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)


async def NewDataMessage(bot: commands.Bot,
                         interaction: Interaction,
                         isError: bool):
  if not interaction.guild or not interaction.channel:
    raise Exception("No guild or channel to this interaction??")
  message = f"""
  {'Could not submit data due to error' if isError else 'Successfully received new data'}
    Guild name: {interaction.guild.name}
    Guild id: {interaction.guild.id}
    Channel name: {interaction.channel.name}
    Channel id: {interaction.channel.id}
    Author name: {interaction.user.name}
    Author id: {interaction.user.id}
    """
  
  await MessageChannel(bot,
                       message,
                       settings.BOTGUILDID,
                       settings.BOTEVENTINPUTID)


async def setup(bot):
  await bot.add_cog(SubmitDataChecker(bot))
