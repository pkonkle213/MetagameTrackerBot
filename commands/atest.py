from timedposts.automated_check_events import EventCheck
import json
import requests
import discord
from discord.ext import commands
from discord import app_commands, Interaction
import settings

TARGET_GUILDS = [settings.TESTGUILDID]
                 
class ATest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  """
  @app_commands.command()
  async def fruits(self, interaction: Interaction, fruit: str):
      await interaction.response.send_message(f'Your favourite fruit seems to be {fruit}')

  @fruits.autocomplete('fruit')
  async def fruits_autocomplete(
    self,   
      interaction: Interaction,
      current: str,
  ) -> list[app_commands.Choice[str]]:
      fruits = ['Banana', 'Pineapple', 'Apple', 'Watermelon', 'Melon', 'Cherry']
      return [
          app_commands.Choice(name=fruit, value=fruit)
          for fruit in fruits if current.lower() in fruit.lower()
      ]
  """
  
  @app_commands.command(name="atest",
                        description="Tests something stupid!")
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  #@app_commands.checks.has_role('MTSubmitter')
  async def Testing(self,
                    interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await EventCheck(self.bot)
    await interaction.followup.send("Testing.")

  @Testing.error
  async def on_tree_error(self,
                          interaction: Interaction,
                          error: app_commands.AppCommandError):
    await interaction.response.send_message(str(error))

async def setup(bot):
  await bot.add_cog(ATest(bot))
