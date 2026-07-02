from discord.ext import commands
from services.command_error_service import Error
import discord
from tuple_conversions import Hub

class HubProfileModal(discord.ui.Modal, title='Update Hub Profile'):
  is_submitted = False

  def __init__(self,bot:commands.Bot, hub: Hub) -> None:
    super().__init__()
    self.bot = bot

    self.hub_name = discord.ui.Label(
      text="Hub Name",
      component=discord.ui.TextInput(
        placeholder="Hub name",
        default=hub.hub_name if hub else "",
        required=True
      )
    )
    self.add_item(self.hub_name)

    self.hub_invite = discord.ui.Label(
      text="Hub Invite",
      component=discord.ui.TextInput(
        placeholder="https://discord.gg/...",
        default="",
        required=False
      )
    )
    self.add_item(self.hub_invite)

  async def on_submit(self, interaction: discord.Interaction) -> None:
    self.submitted_hub_name = self.hub_name.component.value
    self.submitted_hub_invite = self.hub_invite.component.value
    self.is_submitted = True
    await interaction.response.defer(thinking=True)


  async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
    await Error(self.bot, interaction, error)

  async def on_timeout(self) -> None:
    self.is_submitted = False