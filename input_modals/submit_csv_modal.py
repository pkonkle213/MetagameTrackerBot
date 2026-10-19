import discord
from custom_errors import KnownError
from services.convert_and_save_input import ConvertAndUploadCSV
from services.submit_data_errors import EnsureConvertedResults, ReportSubmissionFailure
from tuple_conversions import DataConverted, Event


class SubmitCSVDataModal(discord.ui.Modal, title="Submit Data"):
    def __init__(self, event: Event, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.event = event
        self.converted_data: DataConverted = DataConverted(None, None, None, None, None)
        self.conversion_failed = False

        # TODO: Restore to 10 files when ready
        self.csv_data = discord.ui.Label(
            text="CSV File",
            description="Upload a CSV files for this event.",
            component=discord.ui.FileUpload(required=True, max_values=1),
        )
        self.add_item(self.csv_data)

    async def on_submit(self, interaction: discord.Interaction):
        self.interaction = interaction
        await interaction.response.defer(ephemeral=True)
        try:
            converted_csvs: list[DataConverted] = []
            for csv in self.csv_data.component.values:
                converted = await ConvertAndUploadCSV(self.event, self.file_path, csv)
                converted_csvs.append(converted)

            standings_files = [
                csv for csv in converted_csvs if csv.standings_data is not None
            ]
            if standings_files and len(converted_csvs) > 1:
                raise KnownError(
                    "Only one standings file can be submitted for an event."
                )

            if standings_files:
                self.converted_data = standings_files[0]
            else:
                self.converted_data = DataConverted(
                    [
                        pairing
                        for csv in converted_csvs
                        for pairing in (csv.pairings_data or [])
                    ],
                    None,
                    [error for csv in converted_csvs for error in (csv.errors or [])],
                    None,
                    None,
                    tuple(
                        dict.fromkeys(
                            path
                            for csv in converted_csvs
                            for path in csv.staged_source_files
                        )
                    ),
                )
            EnsureConvertedResults(self.converted_data)
        except Exception as error:
            self.conversion_failed = True
            await ReportSubmissionFailure(interaction, error, "CSV")
