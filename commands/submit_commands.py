import typing
from services.claim_result_services import GetUserInput, AddTheArchetype, MessageStoreFeed
from api_calls.melee_tournaments import GetMeleeTournamentData
import settings
from services.convert_and_save_input import ConvertCSVToDataErrors, ConvertModalToDataErrors, ConvertMeleeTournamentToDataErrors, ConfirmEventDetails
from checks import isSubmitter, IsStore
from custom_errors import KnownError
from discord import app_commands, Interaction, Attachment
from discord.ext import commands
from discord_messages import MessageChannel
from interaction_objects import GetObjectsFromInteraction
from services.add_results_services import SubmitData
from services.command_error_service import Error
from services.message_hubs_services import MessageHubs

class SubmitDataChecker(commands.GroupCog, name='submit'):
  """A group of commands to submit data"""

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="check",
                        description="To test if you can submit data")
  @app_commands.guild_only()
  @IsStore()
  async def SubmitCheck(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True, thinking=False)
    issues = ['Issues I detect:']
    store, game, format = GetObjectsFromInteraction(interaction)

    if not store:
      issues.append('- Store not registered')
    if not isSubmitter(interaction.guild, interaction.user, 'MTSubmitter'):
      issues.append("- You don't have the MTSubmitter role.")
    if not game:
      issues.append('- Category not mapped to a game')
    if game and not format:
      issues.append('- Channel not mapped to a format')

    if len(issues) == 1:
      await interaction.followup.send(
          'Everything looks good. Please reach out to Phil to test your data')
    else:
      await interaction.followup.send('\n'.join(issues))

  @app_commands.command(name="archetype",
                        description="Submit a player's archetype for an event")
  @app_commands.guild_only()
  @IsStore()
  async def SubmitArchetypeCommand(self, interaction: Interaction):
    store, game, format = GetObjectsFromInteraction(interaction)
    userId = interaction.user.id

    if not store or not game or not format:
      raise KnownError('No store, game, or format found.')

    player_name, event, archetype = await GetUserInput(store, game, format, userId, interaction)
    private_output, feed_output, public_output, full_event = AddTheArchetype(interaction, player_name, event, archetype, store, game, format)
    await interaction.followup.send(private_output, ephemeral=True)
    await MessageStoreFeed(self.bot,
                           feed_output,
                           interaction)
    if public_output:
      await MessageChannel(self.bot,
                           public_output,
                           interaction.guild_id,
                           interaction.channel_id)
    if full_event:
      await MessageChannel(self.bot,
                           full_event,
                           interaction.guild_id,
                           interaction.channel_id)
      name = store.store_name if store.store_name else store.discord_name
      output = f"```{name} - " + full_event[3:]
      await MessageHubs(self.bot, store, event, output)

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

    store, game, format = GetObjectsFromInteraction(interaction)
    
    if not store or not game or not format:
      raise KnownError('No store, game, or format found.') #TODO Probably needs to be more detailed
      
    if csv_file or melee_tournament_id:
      date, event_name, event_id, event_type_id = await ConfirmEventDetails(self.bot, interaction, store, game, format)
      if csv_file:
        if not csv_file.filename.endswith('.csv'):
          raise KnownError("Please upload a file with a '.csv' extension.")
        submitted_event = await ConvertCSVToDataErrors(
          self.bot,
          store,
          game,
          date,
          format,
          interaction,
          event_id,
          event_name,
          event_type_id,
          csv_file
        )
      elif melee_tournament_id:
        json_dict = GetMeleeTournamentData(melee_tournament_id, store)
        submitted_event = ConvertMeleeTournamentToDataErrors(
          store,
          game,
          format,
          melee_tournament_id,
          event_id,
          event_name,
          event_type_id,
          json_dict)
      else:
        raise Exception('And you may ask yourself, wait...how did you get here?')
    else: #To reach this means manually submitting data (MTG)
      submitted_event = await ConvertModalToDataErrors(
        self.bot,
        interaction,
        store,
        game,
        format
      )

    #Alert me to a new event either successfull or not
    failure = False
    if submitted_event.PairingData is None and submitted_event.StandingData is None:
      raise KnownError("Unable to submit due to not recognizing the data. Please try again.")
    await NewDataMessage(self.bot, interaction, failure)

    #Advise user of submission process starting
    message_type = 'standings' if submitted_event.StandingData else 'pairings'
    length = len(submitted_event.StandingData) if submitted_event.StandingData else len(submitted_event.PairingData) if submitted_event.PairingData else None
    await interaction.followup.send(
      f"Attempting to add {length} {message_type} to event",
      ephemeral=True
    )

    #Inform user of any errors in submitted data
    if submitted_event.Errors is not None and len(submitted_event.Errors) > 0:
      await interaction.followup.send('Errors:\n' + '\n'.join(submitted_event.Errors), ephemeral=True)

    #Submit the data to the database. Returning event for an announcement
    output, event = SubmitData(
      submitted_event,
      interaction.user.id
    )
    
    if output is None:
      raise KnownError("Unable to submit data. Please try again.")
    
    await interaction.followup.send(output, ephemeral=True)
    
    if event:
      await MessageChannel(
        self.bot,
        f"New data for {event.event_date.strftime('%B %-d')}'s {event.event_name} event has been submitted! Use the `/submit archetype` command to input your archetype!",
        interaction.guild_id,
        interaction.channel_id
      )
      try:
        await MessageHubs(self.bot, store, event)
      except Exception as e:
        await MessageChannel(self.bot, f"Issue messaging hubs: {e}", settings.BOTGUILDID, settings.ERRORCHANNELID)

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
