import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Polygon, Rectangle
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
  #@app_commands.checks.has_role('MTSubmitter') #TODO: Find a way to check the role
  async def Testing(self, interaction: Interaction):
    await interaction.response.defer()
   
    fig, ax = plt.subplots()

    rect = Rectangle((0.2, 0.75), 0.4, 0.15, color="black", alpha=0.3)
    circ = Circle((0.7, 0.2), 0.15, color="blue", alpha=0.3)
    pgon = Polygon([[0.15, 0.15], [0.35, 0.4], [0.2, 0.6]],color="green", alpha=0.5)

    ax.add_patch(rect)
    ax.add_patch(circ)
    ax.add_patch(pgon)

    # Save this beautiful artwork for posterity!
    file_path = "shapes.jpg" #A filename will probably need to be unique as to who generated it and when. Or disposed of once used
    fig.savefig(file_path)

    with open(file_path, "rb") as f:
      pic = discord.File(f, filename=file_path)
    
    await interaction.followup.send("Hi? Testing!")
    await interaction.followup.send("Picture this", file=pic)
    
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
