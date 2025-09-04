import discord
from discord.ext import commands
from discord import app_commands, Interaction
import settings
from checks import isPhil
from services.store_services import NewStoreRegistration

TARGET_GUILDS = [settings.TESTGUILDID]
                 
class ATest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @app_commands.command(name="atest",
                        description="Tests something stupid!")
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  async def Testing(self, interaction: Interaction):
    print('Testing!')
    guild = interaction.guild
    if guild is None:
      await interaction.followup.send("No guild found!")
      return
    await NewStoreRegistration(guild)
    await interaction.followup.send("Tested!")
    
async def setup(bot):
  await bot.add_cog(ATest(bot))
