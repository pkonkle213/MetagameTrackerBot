import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Polygon, Rectangle
import discord
from services.date_functions import ConvertToDate
from data.metagame_data import GetMetagame
from tuple_conversions import Store, Game, Format
from discord.ext import commands
from discord import app_commands, Interaction
import settings

TARGET_GUILDS = [settings.TESTGUILDID]
                 
class ATest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def TestingError(self,
                         interaction:Interaction,
                         error:app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
      await interaction.followup.send("1st attempt to catch the error")
    else:
      await interaction.followup.send("2nd attempt to catch the error")
 
  @app_commands.command(name="atest",
                        description="Tests something stupid!")
  #@app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  #@app_commands.checks.has_role('MTSubmitter') #TODO: Find a way to check the role
  async def Testing(self, interaction: discord.Interaction, message_id: str):
    """
    Edits a message with the given ID in the current channel to "this is good".
    """
    try:
      # Get the channel from the interaction
      channel = interaction.channel
      if channel is None: 
        raise Exception("Channel is None")

      # Fetch the message using its ID
      message = await channel.fetch_message(int(message_id))

      # Edit the message
      await message.edit(content="this is good")

      # Respond to the interaction to confirm
      await interaction.response.send_message(f"Message `{message_id}` edited successfully.", ephemeral=True)

    except discord.NotFound:
        await interaction.response.send_message(f"Message with ID `{message_id}` not found in this channel.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permissions to edit that message.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)    
      
  async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
        role_name = error.missing_role
        await interaction.response.send_message(
            f"You are missing the '{role_name}' role and cannot use this command.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)

async def setup(bot):
  await bot.add_cog(ATest(bot))
