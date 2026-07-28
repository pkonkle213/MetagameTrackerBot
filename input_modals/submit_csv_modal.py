import discord
from tuple_conversions import Event, DataConverted
from services.convert_and_save_input import ConvertAndUploadCSV


class SubmitCSVDataModal(discord.ui.Modal, title="Submit Data"):
    def __init__(self, event: Event, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.event = event
        self.converted_data: DataConverted = DataConverted(None, None, None, None, None)

        self.csv_data = discord.ui.Label(
            text="CSV File",
            description="Upload up to 10 CSV files for this event.",
            component=discord.ui.FileUpload(required=True, max_values=10),
        )
        self.add_item(self.csv_data)

    async def on_submit(self, interaction: discord.Interaction):
        self.interaction = interaction
        await interaction.response.defer(ephemeral=True)
        converted_csvs: list[DataConverted] = []
        for csv in self.csv_data.component.values:
            converted = await ConvertAndUploadCSV(self.event, self.file_path, csv)
            converted_csvs.append(converted)

        if converted_csvs[0].standings_data is not None and len(converted_csvs) > 1:
            raise Exception("Only one standings file can be submitted for an event.")

        if converted_csvs[0].standings_data is not None:
            self.converted_data = converted_csvs[0]
        else:
            self.converted_data = DataConverted(
                [pairing for csv in converted_csvs for pairing in csv.pairings_data],
                None,
                [error for csv in converted_csvs for error in csv.errors],
                None,
                None,
            )
