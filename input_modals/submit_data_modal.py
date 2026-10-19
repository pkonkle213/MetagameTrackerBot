import discord

from services.convert_and_save_input import ConvertAndUploadMessage
from services.submit_data_errors import EnsureConvertedResults, ReportSubmissionFailure
from tuple_conversions import DataConverted, Event


class SubmitManualDataModal(discord.ui.Modal, title="Submit Data"):
    def __init__(self, event: Event, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.event = event
        self.converted_data: DataConverted = DataConverted(None, None, None, None, None)
        self.conversion_failed = False

        self.manual_data = discord.ui.Label(
            text="Event Data",
            component=discord.ui.TextInput(
                placeholder="Paste your data here",
                style=discord.TextStyle.paragraph,
                required=True,
                max_length=2000,
                min_length=10,
            ),
        )
        self.add_item(self.manual_data)

    async def on_submit(self, interaction: discord.Interaction):
        self.interaction = interaction
        await interaction.response.defer(thinking=True, ephemeral=True)
        try:
            self.converted_data = ConvertAndUploadMessage(
                self.event,
                self.file_path,
                self.manual_data.component.value,
            )
            EnsureConvertedResults(self.converted_data)
        except Exception as error:
            self.conversion_failed = True
            await ReportSubmissionFailure(interaction, error, "manual data")
