from discord.ext import commands
from discord import app_commands, Interaction
from checks import isOwner
from services.command_error_service import Error
from services.store_services import UpdateStoreDetails

class StoreProfile(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="update",
    description="Updates the store profile")
  @app_commands.guild_only()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  #@app_commands.check(isOwner)
  @app_commands.checks.has_role('MTSubmitter')
  async def UpdateProfile(self,
                          interaction: Interaction):
    """Updates all info in the store profile"""
    result = await UpdateStoreDetails(interaction)
    if result:
      await interaction.followup.send('Store profile updated!',ephemeral=True)
    else:
      await interaction.followup.send('Store profile unable to update.',ephemeral=True)
    

  @UpdateProfile.error
  async def Errors(self,
                   interaction: Interaction,
                   error: app_commands.AppCommandError):
    await Error(self.bot, interaction, error)

async def setup(bot):
  await bot.add_cog(StoreProfile(bot))