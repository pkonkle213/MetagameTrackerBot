import discord
from discord import Interaction, app_commands
from discord.ext import commands
from checks import IsStore
from custom_errors import KnownError
from data.event_data import CompleteEvent
from interaction_objects import GetObjectsFromInteraction
from services.command_error_service import Error
from services.convert_and_save_input import BuildFilePath
from services.event_services import EventForData
from input_modals.submit_data_modal import SubmitManualDataModal
from services.add_results_services import AddStandingResults, AddPairingResults
from tuple_conversions import DataInputEnum, ViewButtonEnum
from views.confirm_data import ConfirmData


class TestDataSubmission(commands.Cog):
  """Test command for the full data submission flow"""

  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(
    name="test_data_submission",
    description="Test the full data submission flow"
  )
  @app_commands.checks.has_role("MTSubmitter")
  @app_commands.guild_only()
  @IsStore()
  async def TestDataSubmissionCommand(self, interaction: Interaction) -> None:
    objects = GetObjectsFromInteraction(interaction)

    if not objects.store or not objects.game or not objects.format:
      raise KnownError("No store, game, or format found.")

    if objects.hub:
      raise KnownError("You can't submit data from a hub.")

    event, input_type, active_interaction = await EventForData(
      self.bot, interaction, objects.store, objects.game, objects.format
    )

    if not event or not input_type or not active_interaction:
      await interaction.followup.send('Event canceled!', ephemeral=True)
      return

    save_path = BuildFilePath(objects.store, objects.game, objects.format, 'ManualInput.txt')
    cont = True
    while cont:
      match input_type:
        case DataInputEnum.Manual.value:
          modal = SubmitManualDataModal(event, save_path)

        case DataInputEnum.CSV.value:
          modal = None
          # TODO: Define the modal for CSV data input

        case DataInputEnum.Melee.value:
          modal = None
          # TODO: Define the modal for Melee data input

        case _:
          raise KnownError("Unknown input type")

      await active_interaction.response.send_modal(modal)
      try:
        await modal.wait()
      except Exception:
        raise KnownError("Something went wrong. Canceling data.")

      view = ConfirmData()
      await modal.interaction.followup.send(
        "Please confirm the data", ephemeral=True, view=view
      )
      await view.wait()

      confirm_response = view.action
      active_interaction = view.interaction

      if confirm_response == ViewButtonEnum.Cancel.value:
        break

      data = modal.converted_data
      confirmation = modal.confirm_response

      if data.standings_data:
        AddStandingResults(event, data.standings_data, interaction.user.id)
      elif data.pairings_data:
        AddPairingResults(event, data.pairings_data, interaction.user.id, data.round_number)

      if confirmation == ViewButtonEnum.DoneComplete.value:
        cont = False
        CompleteEvent(event.id)

      if confirmation == ViewButtonEnum.DoneIncomplete.value:
        cont = False

    await interaction.followup.send("Thank you for submitting data!", ephemeral=True)

  @TestDataSubmissionCommand.error
  async def Errors(
    self,
    interaction: Interaction,
    error: app_commands.AppCommandError
  ):
    await Error(self.bot, interaction, error)


async def setup(bot: commands.Bot):
  await bot.add_cog(TestDataSubmission(bot))
