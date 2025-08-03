from discord import app_commands, Interaction
from discord.ext import commands
from checks import isOwner
from services.store_services import RegisterNewStore, AssignStoreOwnerRoleInBotGuild, SetPermissions
from discord_messages import Error, ErrorMessage
from psycopg2.errors import UniqueViolation
from data.store_data import DeleteStore

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
    try:
      store = RegisterNewStore(interaction, store_name)
      if store is None:
        raise Exception('Unable to register store')
      await SetPermissions(interaction)
      try:
        await AssignStoreOwnerRoleInBotGuild(self.bot, interaction)
      except Exception as exception:
        print('Unable to assign this user to the store owner role in bot guild.')
        print('Exception:', exception)
      await interaction.followup.send(f'Registered {store_name.title()} with discord {store.DiscordName.title()} with owner {interaction.user}', ephemeral=True)
    except UniqueViolation as exception:
      await interaction.followup.send("This store is already registered. If you believe this is an error, please contact the bot owner via the bot's discord.")
    except Exception as exception:
      await interaction.followup.send("Something unexpected went wrong. It's been reported. Please try again in a few hours.", ephemeral=True)
      await Error(self.bot, exception)
      success = DeleteStore(interaction.guild_id)
      if not success:
        await ErrorMessage(self.bot, f'Unable to delete store {interaction.guild_id} from database')
  
async def setup(bot):
  await bot.add_cog(RegisterStore(bot))