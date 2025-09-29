import discord
from discord.ext import commands
from discord import app_commands, Interaction
from data_translation import ConvertMessageToData
from services.date_functions import ConvertToDate
import settings
from checks import isPhil
from services.store_services import NewStoreRegistration
from tuple_conversions import Data, Format, Game, Store

TARGET_GUILDS = [settings.TESTGUILDID]
                 
class ATest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

    self.user_info_context_menu = app_commands.ContextMenu(
      name='Get User Info',  # This is the name displayed in Discord
      callback=self.Testing # The function to call when the command is used
    )
    # Add the context menu to the bot's command tree
    self.bot.tree.add_command(self.user_info_context_menu)
  """
  @commands.Cog.listener()
  async def TestingError(self, interaction:Interaction, error:app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
      await interaction.followup.send("1st attempt to catch the error")
    else:
      await interaction.followup.send("2nd attempt to catch the error")
  """
  """@app_commands.command(name="atest",
                        description="Tests something stupid!")
  @app_commands.guild_only()
  @app_commands.guilds(*[discord.Object(id=guild_id) for guild_id in TARGET_GUILDS])"""
  #@app_commands.checks.has_role('MTSubmitter')
  async def Testing(self, interaction: Interaction, member: discord.Member):
    """Callback for the 'Get User Info' context menu command."""
    await interaction.response.send_message(
        f"User: {member.display_name}\nID: {member.id}\nJoined Discord: {member.created_at.strftime('%Y-%m-%d')}",
        ephemeral=True # Makes the message only visible to the user who invoked it
    )
    
"""
  @Testing.error
  async def OtherError(self, interaction:Interaction, error:app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
      await interaction.followup.send("3rd attempt to catch the error")
    else:
      await interaction.followup.send("4th attempt to catch the error")
    """
async def setup(bot):
  await bot.add_cog(ATest(bot))
