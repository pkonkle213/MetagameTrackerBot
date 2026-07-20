import discord
from discord.ext import commands
from discord import app_commands

# 1. Define the Modal for user input
class FoodModal(discord.ui.Modal, title="Enter Your Favorite Food"):
  food_input = discord.ui.TextInput(
    label="Favorite Food",
    placeholder="Type your favorite food here...",
    max_length=50
  )

  def __init__(self):
    super().__init__()
    self.food_name = None

  async def on_submit(self, interaction: discord.Interaction):
    self.food_name = self.food_input.value
    await interaction.response.send_message(f"Got it! Added `{self.food_name}` to the list.", ephemeral=True)

# 2. Define the View for the persistent button group
class FoodChoiceView(discord.ui.View):
  def __init__(self, user_id: int):
    super().__init__(timeout=None) # Set timeout as needed
    self.user_id = user_id
    self.action = None

  # Interaction check to ensure only the command author can use the buttons
  async def interaction_check(self, interaction: discord.Interaction) -> bool:
    if interaction.user.id == self.user_id:
      return True
    await interaction.response.send_message("You cannot control this menu.", ephemeral=True)
    return False

  @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
  async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.action = "cancel"
    self.stop()

  @discord.ui.button(label="Continue", style=discord.ButtonStyle.primary)
  async def continue_loop(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.action = "continue"
    self.stop()

  @discord.ui.button(label="Mark Complete", style=discord.ButtonStyle.success)
  async def mark_complete(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.action = "complete"
    self.stop()

  @discord.ui.button(label="Mark Incomplete", style=discord.ButtonStyle.secondary)
  async def mark_incomplete(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.action = "incomplete"
    self.stop()

# 3. Define the Slash Command
@app_commands.command(name="favorite_foods", description="Start your favorite food list loop")
async def favorite_foods(interaction: discord.Interaction):
  favorite_list = []
  
  while True:
    # Step A: Prompt user via Modal
    modal = FoodModal()
    await interaction.response.send_modal(modal)

    # Wait until modal is filled out
    try:
      await modal.wait()
    except Exception:
      await interaction.followup.send("Modal timed out. Exiting loop.", ephemeral=True)
      break

    # Record the food if the modal was successfully submitted
    if modal.food_name:
      favorite_list.append(modal.food_name)

    # Step B: Present the button group
    view = FoodChoiceView(user_id=interaction.user.id)
    
    # Send buttons as a followup message
    await interaction.followup.send("What would you like to do next?", view=view, ephemeral=True)
    await view.wait()

    # Step C: Handle the button press
    if view.action == "cancel":
      await interaction.followup.send("List building cancelled.", ephemeral=True)
      break
        
    elif view.action in ["complete", "incomplete"]:
      status = "Complete" if view.action == "complete" else "Incomplete"
      items_str = ", ".join(favorite_list) if favorite_list else "None"
      await interaction.followup.send(
        f"**List Status:** {status}\n**Favorite Foods:** {items_str}", 
        ephemeral=True
      )
      break
        
    elif view.action == "continue":
      # The while loop will start over and prompt the modal again
      continue