from views.confirm_data import ConfirmData
from discord import Interaction, User, app_commands
from discord.ext import commands
from services.event_services import EventForData
from checks import IsStore, isSubmitter
from custom_errors import KnownError
from data.event_data import GetHubEvents, GetStoreEvents, CompleteEvent
from data.player_name_data import GetUserArchetypes, GetUserName
from interaction_objects import GetObjectsFromInteraction
from services.command_error_service import Error
from services.determine_archetype_input import GetArchetypeModal
from tuple_conversions import DataInputEnum, ViewButtonEnum
from services.convert_and_save_input import BuildFilePath
from input_modals.submit_data_modal import SubmitManualDataModal
from services.add_results_services import AddStandingResults, AddPairingResults

class SubmitDataChecker(commands.GroupCog, name="submit"):
  """A group of commands to submit data"""

  def __init__(self, bot:commands.Bot):
    self.bot = bot

  @app_commands.command(name="check", description="To test if you can submit data")
  @app_commands.guild_only()
  @IsStore()
  @app_commands.checks.cooldown(1, 300.0, key=lambda i: (i.guild_id, i.user.id))
  async def SubmitCheck(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True, thinking=False)
    issues = ["Issues I detect:"]
    objects = GetObjectsFromInteraction(interaction)
    if not interaction.guild:
      raise KnownError('How?')
    if isinstance(interaction.user, User):
      raise KnownError('Bad user. Need Member')

    if not objects.store:
      issues.append("- Store not registered")
    if not isSubmitter(interaction.guild, interaction.user, "MTSubmitter"):
      issues.append("- You don't have the MTSubmitter role.")
    if not objects.game:
      issues.append("- Category not mapped to a game")
    if objects.game and not objects.format:
      issues.append("- Channel not mapped to a format")

    if len(issues) == 1:
      await interaction.followup.send(
        "Everything looks good. Please reach out to Phil to test your data"
      )
    else:
      await interaction.followup.send("\n".join(issues))

  @app_commands.command(
    name="archetype", description="Submit a player's archetype for an event"
  )
  @app_commands.guild_only()
  async def SubmitArchetypeCommand(self, interaction: Interaction):
    objects = GetObjectsFromInteraction(interaction)
    userId = interaction.user.id

    if (
      (not objects.store and not objects.hub)
      or not objects.game
      or not objects.format
    ):
      raise KnownError("Insufficient information found.")

    guild_id = interaction.guild_id
    channel_id = interaction.channel_id

    if not guild_id or not channel_id:
      raise KnownError("No guild or channel found.")

    player_name = GetUserName(userId)
    player_archetypes = GetUserArchetypes(userId, objects.game, objects.format)

    if objects.hub:
      events = GetHubEvents(guild_id, channel_id)
    elif objects.store:
      events = GetStoreEvents(objects.store, objects.game, objects.format)
    else:
      raise KnownError("No store or hub found.")

    if len(events) == 0:
      raise KnownError("No events found.")

    await GetArchetypeModal(
      self.bot,
      userId,
      events,
      interaction,
      objects.game,
      objects.format,
      player_name,
      player_archetypes,
    )

  @app_commands.command(name="data", description="Submitting an event's data")
  @app_commands.checks.has_role("MTSubmitter")
  @app_commands.guild_only()
  @IsStore()
  async def SubmitDataCommand(
    self,
    interaction: Interaction
  ) -> None:
    objects = GetObjectsFromInteraction(interaction)

    if not objects.store or not objects.game or not objects.format:
      raise KnownError("No store, game, or format found.")

    if objects.hub:
      raise KnownError("You can't submit data from a hub")

    event, input_type = await EventForData(self.bot, interaction, objects.store, objects.game, objects.format)
    # TODO: I need to know if the event was created so that I can alert the channel to new data
    if not event or not input_type:
      #TODO: I don't like how this doesn't clear the last message
      await interaction.followup.send('Event canceled!', ephemeral=True)
      return
    
    # Now with the event known, I need to start a loop and present modals to input data
    save_path = BuildFilePath(objects.store, objects.game, objects.format, 'ManualInput.txt')
    cont = True
    while cont:
      match input_type:
        case DataInputEnum.Manual.value:
          modal = SubmitManualDataModal(event, save_path)
          pass

        case DataInputEnum.CSV.value:
          modal = None
          #TODO: Define the modal for csv data input
          pass

        case DataInputEnum.Melee.value:
          modal = None
          #TODO: Define the modal for melee data input
          pass

        case _:
          raise KnownError("Unknown input type")            

      await interaction.response.send_modal(modal)
      try:
        await modal.wait()
      except:
        raise KnownError("Something went wrong. Canceling data.")

      # TODO: Build table to have the user double check
      
      view = ConfirmData()
      await interaction.followup.send("Please confirm the data", ephemeral=True, view=view)
      await view.wait()

      self.confirm_response = view.action

      if self.confirm_response == ViewButtonEnum.Cancel.value:
        return
        
      data = modal.converted_data
      confirmation = modal.confirm_response  
      
      # Submit data to database
      if data.standings_data:
        AddStandingResults(event, data.standings_data, interaction.user.id)
      elif data.pairings_data:
        AddPairingResults(event, data.pairings_data, interaction.user.id, data.round_number)
      
      # If event over, update event as complete and set cont = False
      if confirmation == ViewButtonEnum.DoneComplete.value:
        cont = False
        CompleteEvent(event.id)
        
      # If event not over, set cont = False
      if confirmation == ViewButtonEnum.DoneIncomplete.value:
        cont = False
    
    await interaction.followup.send("Thank you for submitting data!", ephemeral=True)


  @SubmitCheck.error
  @SubmitDataCommand.error
  @SubmitArchetypeCommand.error
  async def Errors(
    self,
    interaction: Interaction,  
    error: app_commands.AppCommandError
  ):
    await Error(self.bot, interaction, error)

async def setup(bot:commands.Bot):
  await bot.add_cog(SubmitDataChecker(bot))
