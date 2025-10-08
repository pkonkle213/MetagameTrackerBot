import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import discord
from discord.ext import commands
from discord import app_commands, Interaction
import settings

TARGET_GUILDS = [settings.TESTGUILDID]
                 
class ATest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def TestingError(self, interaction:Interaction, error:app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
      await interaction.followup.send("1st attempt to catch the error")
    else:
      await interaction.followup.send("2nd attempt to catch the error")
 
  @app_commands.command(name="atest",
                        description="Tests something stupid!")
  #@app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  @app_commands.checks.has_role('MTSubmitter') #TODO: Find a way to check the role
  async def Testing(self, interaction: Interaction):
    await interaction.response.defer()
    data = np.arange(10)
    plt.plot(data)
    thing = plt.plot(data)
    await interaction.followup.send("Hi? Testing!")
    await interaction.followup.send(file=discord.File(thing))
    
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
