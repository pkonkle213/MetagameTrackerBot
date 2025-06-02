import discord
from discord.ext import commands
import traceback

#https://www.youtube.com/watch?v=pGBvyTziQug

class FeedbackModal(discord.ui.Modal, title="Send us your feedback"):
  fb_title = discord.ui.TextInput(
      style=discord.TextStyle.short,
      label="Title",
      required=False,
      placeholder="Give your feedback a title"
  )

  async def on_submit(self, interaction: discord.Interaction):
      """This is my summary
      Args:
          interaction (discord.Interaction): Default discordpy Interaction
      """
      channel = interaction.channel

      embed = discord.Embed(title="New Feedback",
                            description=self.message.value,
                            color=discord.Color.yellow())
      embed.set_author(name=self.user.nick)

      await channel.send(embed=embed)
      await interaction.response.send_message(f"Thank you, {self.user.nick}", ephemeral=True)

  async def on_error(self, interaction: discord.Interaction, error : Exception):
      traceback.print_tb(error.__traceback__)
    
async def NewTextInput(interaction: discord.Interaction):
  feedback_modal = FeedbackModal()
  feedback_modal.user = interaction.user
  await interaction.response.send_modal(feedback_modal)
