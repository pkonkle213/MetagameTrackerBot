import discord
from discord.ext import commands
import datetime

class DateInput(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.TextInput(label="Day (DD)", placeholder="e.g., 01, 15, 31", min_length=1, max_length=2))
        self.add_item(discord.ui.TextInput(label="Month (MM)", placeholder="e.g., 01, 07, 12", min_length=1, max_length=2))
        self.add_item(discord.ui.TextInput(label="Year (YYYY)", placeholder="e.g., 2023, 2024", min_length=4, max_length=4))

    async def on_submit(self, interaction: discord.Interaction):
        day = int(self.children[0].value)
        month = int(self.children[1].value)
        year = int(self.children[2].value)

        try:
            date = datetime.datetime(year, month, day).strftime("%Y-%m-%d")
            await interaction.response.send_message(f"You selected the date: {date}", ephemeral=True)
        except ValueError:
             await interaction.response.send_message("Invalid date. Please enter a valid date.", ephemeral=True)

class MyDateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Select Date", style=discord.ButtonStyle.primary)
    async def date_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DateInput(title="Enter a Date"))
