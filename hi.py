import discord
from discord import ui
from discord.ext import commands

token = 'Token_Here'
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
class Dropdown(ui.ChannelSelect):
    def __init__(self):
        super().__init__()

    async def callback(self, interaction: discord.Interaction):
        selected_user = self.values[0]
        await interaction.response.send_message(f"You selected: {selected_user.mention}", ephemeral=True)

class Questionnaire(ui.Modal, title='New Modals Tutorial'):
    dropdown = ui.Label(text='Select something',
                    component=Dropdown()
                    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'You selected: {self.dropdown.component.values[0]}',
                                                ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()

@bot.tree.command()
async def modal(interaction: discord.Interaction):
    await interaction.response.send_modal(Questionnaire())

bot.run(token)
