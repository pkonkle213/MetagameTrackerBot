import discord
from discord import ui

# 1. The final modal for Pizza input
class PizzaModal(ui.Modal, title='Second Step: Favorite Pizza'):
    def __init__(self, ice_cream: str):
        super().__init__()
        self.ice_cream = ice_cream
    pizza = ui.TextInput(label='Pizza Type', placeholder='e.g., Pepperoni...')

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Got it! You love {self.pizza.value} pizza and {self.ice_cream} ice cream.", 
            ephemeral=True
        )

# 2. The view containing the confirmation button
class ConfirmView(ui.View):
    def __init__(self, flavor: str):
        super().__init__()
        self.flavor = flavor

    @ui.button(label="Confirm & Continue", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        # A button interaction IS allowed to send a modal
        await interaction.response.send_modal(PizzaModal(self.flavor))

# 3. The initial modal for Ice Cream input
class IceCreamModal(ui.Modal, title='First Step: Ice Cream'):
    flavor = ui.TextInput(label='Ice Cream Flavor', placeholder='e.g., Vanilla...')

    async def on_submit(self, interaction: discord.Interaction):
        # Respond with a button to bridge to the next modal
        await interaction.response.send_message(
            content=f"You chose {self.flavor.value}. Click below to continue.",
            view=ConfirmView(self.flavor.value),
            ephemeral=True
        )

# 4. The Slash Command
async def send_survey(interaction: discord.Interaction):
    await interaction.response.send_modal(IceCreamModal())