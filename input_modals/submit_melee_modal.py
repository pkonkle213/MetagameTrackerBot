import discord
from tuple_conversions import Event, Store, DataConverted
from services.convert_and_save_input import ConvertAndUploadMeleeTournament


class SubmitMeleeDataModal(discord.ui.Modal, title="Submit Data"):
    def __init__(self, store:Store, event: Event, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.event = event
        self.store = store
        self.converted_data: DataConverted = DataConverted(None, None, None, None, None)
        self.confirm_response = None

        self.melee_data = discord.ui.Label(
            text="Melee Tournament ID",
            component=discord.ui.TextInput(
                placeholder="Paste your Melee Tournament ID here",
                style=discord.TextStyle.short,
                required=True,
                max_length=100,
                min_length=5
            ),
        )
        self.add_item(self.melee_data)

    async def on_submit(self, interaction: discord.Interaction):
        self.interaction = interaction
        await interaction.response.defer(ephemeral=True)
        self.converted_data = ConvertAndUploadMeleeTournament(self.event, self.melee_data.value, self.store, self.file_path)