import discord
from discord.ext import commands
from discord import app_commands, Interaction
import settings
from services.demonstration_functions import NewDemo
from discord_messages import Error

TARGET_GUILDS = [settings.BOTGUILD.id]

class NewDemoCommand(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="demo",
  description="Set up the database for a demonstration")
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  async def Demo(self, interaction: Interaction):
    try:
      await interaction.response.defer()
      NewDemo()
      await interaction.followup.send('All set up!')
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, exception)

async def setup(bot):
  await bot.add_cog(NewDemoCommand(bot))