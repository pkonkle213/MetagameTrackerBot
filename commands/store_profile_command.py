from discord.ext import commands
from discord import app_commands, Interaction
from checks import isOwner
from custom_errors import KnownError
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
                          interaction: Interaction,
                          store_name: str,
                          owner_name: str):
    """
    Updates the store name and owner's name in the database
    
    Parameters
    ----------

    store_name: string
      The name of the store
    owner_name: string
      The owner's preferred name
    """
    await interaction.response.defer(ephemeral=True)
    try:
      #TODO: Implement this
      result = await UpdateStoreDetails(interaction, store_name, owner_name)
      if result:
        await interaction.followup.send('Store profile updated')
      else:
        await interaction.followup.send('Unable to update the store profile')
    except KnownError as exception:
      await interaction.followup.send(exception.message, ephemeral=True)
    except Exception as exception:
      await Error(self.bot, interaction, exception)

async def setup(bot):
  await bot.add_cog(StoreProfile(bot))