from discord import app_commands, Interaction
from discord.ext import commands
from checks import isOwner
from services.store_services import RegisterNewStore, AssignStoreOwnerRoleInBotGuild, SetPermissions
from discord_messages import Error

class RegisterStore(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="register",
                                description="Register your store")
  @app_commands.check(isOwner)
  @app_commands.guild_only()
  async def Register(self, interaction: Interaction, store_name: str):
    """
    Parameters
    ----------
    store_name: string
      The name of the store
    """
    await interaction.response.defer()
    store = RegisterNewStore(interaction, store_name)
    if store is None:
      raise Exception('Unable to register store')
    await SetPermissions(interaction)
    await AssignStoreOwnerRoleInBotGuild(self.bot, interaction)
    await interaction.followup.send(f'Registered {store_name.title()} with discord {store.DiscordName.title()} with owner {interaction.user}')

  @Register.error
  async def register_error(self, interaction: Interaction, error):
    await interaction.followup.send('Unable to complete registration for the store. This has been reported.')
    await Error(interaction, error)

async def setup(bot):
  await bot.add_cog(RegisterStore(bot))