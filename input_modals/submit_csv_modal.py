from uuid import uuid4

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

        self.csv_data = discord.ui.Label(
            text="CSV File",
            description="Upload up to 10 CSV files for this event.",
            component=discord.ui.FileUpload(required=True, max_values=10),
        )
        self.add_item(self.csv_data)

    async def on_submit(self, interaction: discord.Interaction):
        self.interaction = interaction
        await interaction.response.defer(ephemeral=True)
        try:
            converted_csvs: list[DataConverted] = []
            upload_batch_id = uuid4().hex
            base_path = self.file_path.rsplit(".", 1)[0]
            for index, csv in enumerate(self.csv_data.component.values, start=1):
                upload_path = f"{base_path}_{upload_batch_id}_{index}.csv"
                converted = await ConvertAndUploadCSV(self.event, upload_path, csv)
                converted_csvs.append(converted)

            standings_files = [
                csv for csv in converted_csvs if csv.standings_data is not None
            ]
            if standings_files and len(converted_csvs) > 1:
                raise KnownError(
                    "A standings CSV must be submitted by itself."
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
