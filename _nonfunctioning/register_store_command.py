
from discord import app_commands, Interaction
from discord.ext import commands
from checks import isOwner
from services.store_services import AssignStoreOwnerRoleInBotGuild, CreateMTSubmitterRole
from services.command_error_service import Error
from psycopg2.errors import UniqueViolation
from data.store_data import DeleteStore

#TODO: This needs to move to being an "Update Store Profile" command with the new way to register stores
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
  """
    await interaction.response.defer()
    try:
      store = RegisterNewStore(interaction, store_name)
      await CreateMTSubmitterRole(interaction)
      await interaction.followup.send(f'Registered {store_name.title()} with discord {store.DiscordName.title()} with owner {interaction.user}', ephemeral=True)
      try:
        await AssignStoreOwnerRoleInBotGuild(self.bot, interaction)
      except Exception as exception:
        print('Unable to assign this user to the store owner role in bot guild.')
        print('Exception:', exception)
    except UniqueViolation:
      await interaction.followup.send("This store is already registered. If you believe this is an error, please contact the bot owner via the bot's discord.")
    except Exception as exception:
      await Error(self.bot, interaction, exception)
      DeleteStore(interaction.guild_id)


async def setup(bot):
  await bot.add_cog(RegisterStore(bot))
"""