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
    if interaction.guild is None:
      await interaction.response.send_message("This command can only be used in a guild.", ephemeral=True)
    else:
      NewStoreRegistration(interaction.guild)
      await interaction.followup.send("Testing!")
    
async def setup(bot):
  print('Adding ATest')
  await bot.add_cog(ATest(bot))
