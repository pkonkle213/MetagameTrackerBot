import discord
from discord.ext import commands
from discord import app_commands, Interaction
from services.store_level_service import Level1StoreIds
import settings

#TODO: This is an interesting way to get Level 2 stores, if they exist in the future
TARGET_GUILDS = [settings.TESTSTOREGUILD.id]

class ATest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @app_commands.command(name="atest",
                        description="Tests something stupid!")
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])
  async def Testing(self, interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    array = Level1StoreIds()
    print('Array:', array)
    await interaction.followup.send("Testing!")
    
async def setup(bot):
  await bot.add_cog(ATest(bot))
