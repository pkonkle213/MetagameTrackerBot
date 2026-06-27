from discord import Interaction, app_commands
from discord.ext import commands

from checks import IsStore, isSubmitter
from services.command_error_service import Error
from services.store_services import UpdateStoreDetails
from input_modals.update_archetype_modal import UpdateArchetypeModal
from interaction_objects import GetObjectsFromInteraction

class StoreProfile(commands.GroupCog, name="update"):
  def __init__(self, bot:commands.Bot):
    self.bot = bot

  @app_commands.command(name="archetypes", description="Mass updates archetypes")
  @app_commands.guild_only()
  @app_commands.checks.has_role("MTSubmitter")
  @IsStore()
  async def UpdateArchetypes(self, interaction: Interaction):
    objects = GetObjectsFromInteraction(interaction)
    if not objects.store or not objects.game or not objects.format:
      raise Exception("No store, game, or format found.")
    modal = UpdateArchetypeModal(self.bot, objects.store, objects.game, objects.format)
    await interaction.response.send_modal(modal)
    await modal.wait()

  @app_commands.command(name="store", description="Updates the store profile")
  @app_commands.guild_only()
  @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
  # @app_commands.check(isOwner)
  @app_commands.checks.has_role("MTSubmitter")
  @IsStore()
  async def UpdateProfile(self, interaction: Interaction):
    """Updates all info in the store profile"""
    result = await UpdateStoreDetails(interaction)
    if result:
      await interaction.followup.send("Store profile updated!", ephemeral=True)
    else:
      await interaction.followup.send(
        "Store profile unable to update.", ephemeral=True
      )

  @UpdateProfile.error
  async def Errors(
    self, interaction: Interaction, error: app_commands.AppCommandError
  ):
    await Error(self.bot, interaction, error)


async def setup(bot:commands.Bot):
  await bot.add_cog(StoreProfile(bot))
