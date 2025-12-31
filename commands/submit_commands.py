import typing
from services.claim_result_services import GetUserInput, AddTheArchetype, MessageStoreFeed
from api_calls.melee_tournaments import GetMeleeTournamentData
import settings
from services.convert_and_save_input import ConvertCSVToDataErrors, ConvertModalToDataErrors, ConvertMeleeTournamentToDataErrors
from checks import isSubmitter
from custom_errors import KnownError
from tuple_conversions import Standing
from discord import app_commands, Interaction, Attachment
from discord.ext import commands
from discord_messages import MessageChannel
from interaction_objects import GetObjectsFromInteraction
from services.add_results_services import SubmitCheck, SubmitData
from services.command_error_service import Error


class SubmitDataChecker(commands.GroupCog, name='submit'):
  """A group of commands to submit data"""

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="check",
                        description="To test if you can submit data")
  @app_commands.guild_only()
  @app_commands.checks.has_role('MTSubmitter')
  async def SubmitCheck(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
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
  async def SubmitArchetypeCommand(self, interaction: Interaction):
    try:
      player_name, date, archetype = await GetUserInput(interaction)
      private_output, feed_output, public_output, full_event = await AddTheArchetype(
          interaction, player_name, date, archetype)
      await interaction.followup.send(private_output, ephemeral=True)
      await MessageStoreFeed(self.bot, feed_output, interaction)
      if public_output:
        await MessageChannel(self.bot, public_output, interaction.guild_id,
                             interaction.channel_id)
      if full_event:
        await MessageChannel(self.bot, full_event, interaction.guild_id,
                             interaction.channel_id)
    except ValueError:
      await interaction.followup.send(
          "The date provided doesn't match the MM/DD/YYYY formatting. Please try again",
          ephemeral=True)
    #await interaction.response.send_message(response)

  @app_commands.command(name="data",
                        description="Submitting your event's data")
  @app_commands.checks.has_role('MTSubmitter')
  @app_commands.guild_only()
  async def SubmitDataCommand(self,
                              interaction: Interaction,
                              csv_file: typing.Optional[Attachment] = None,
                              melee_tournament_id: str = ''):
    """
    Parameters
    ----------    
    csv_file: Attachment
      The CSV file containing the event's data from CARDE.IO
      
    melee_tournament_id: str
      The Melee Tournament ID for the event
    """
    whole_event = False

    #Ensure that only one type of data is being submitted
    if csv_file and melee_tournament_id:
      raise KnownError(
          "You can only submit a CSV file or a Melee Tournament ID, not both.")

    #Get the data source from the user - respond FIRST before any slow operations
    if csv_file:
      await interaction.response.defer(ephemeral=True)
      store, game, format = SubmitCheck(interaction)  #TODO: THIS BROKE THINGS
      if not csv_file.filename.endswith('.csv'):
        raise KnownError("Please upload a file with a '.csv' extension.")
      data, errors, round_number, date = await ConvertCSVToDataErrors(
          self.bot, game, interaction, csv_file)
    elif melee_tournament_id:
      await interaction.response.defer(ephemeral=True)
      store, game, format = SubmitCheck(interaction)
      whole_event = True
      json_dict = GetMeleeTournamentData(melee_tournament_id, store)

      guild = interaction.guild
      data, errors, round_number, date = ConvertMeleeTournamentToDataErrors(
          guild, json_dict)
    else:
      # Send modal first, get interaction_objects after modal submits
      data, errors, round_number, date, store, game, format = await ConvertModalToDataErrors(
          self.bot, interaction)

    if data is None:
      print('Data is None')
      await NewDataMessage(self.bot, interaction, True)
      raise KnownError(
          "Unable to submit due to not recognizing the data. Please try again."
      )

    #Advise user of submission process starting
    message_type = 'standings' if isinstance(data[0], Standing) else 'pairings'
    await interaction.followup.send(
        f"Attempting to add {len(data)} {message_type} to event",
        ephemeral=True)

    #Inform user of any errors in submitted data
    if len(errors) > 0:
      await interaction.followup.send('Errors:\n' + '\n'.join(errors),
                                      ephemeral=True)

    #Inform me of the new event being added
    await NewDataMessage(self.bot, interaction, False)

    #Submit the data to the database. Returning event for an announcement
    output, event_created = SubmitData(
        store,
        game,
        format,
        interaction.user.id,
        data,
        date,
        round_number,
        False,  #modal.submitted_is_event_complete)
        whole_event)
    if output is None:
      raise KnownError("Unable to submit data. Please try again.")

    await interaction.followup.send(output, ephemeral=True)
    if event_created:
      await MessageChannel(
          self.bot,
          f"New data for {event_created.strftime('%B %-d')}'s event has been submitted! Use the `/submit archetype` command to input your archetype!",
          interaction.guild_id, interaction.channel_id)

  @SubmitCheck.error
  @SubmitDataCommand.error
  @SubmitArchetypeCommand.error
  async def Errors(self, interaction: Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)


async def NewDataMessage(bot: commands.Bot, interaction: Interaction,
                         isError: bool):
  message = f"""
  {'Could not submit data due to error' if isError else 'Successfully received new data'}
    Guild name: {interaction.guild.name}
    Guild id: {interaction.guild.id}
    Channel name: {interaction.channel.name}
    Channel id: {interaction.channel.id}
    Author name: {interaction.user.name}
    Author id: {interaction.user.id}
    """
  await MessageChannel(bot, message, settings.BOTGUILDID,
                       settings.BOTEVENTINPUTID)


async def setup(bot):
  await bot.add_cog(SubmitDataChecker(bot))
