from discord import Interaction, app_commands, Object
from discord.ext import commands
import timedposts.automated_paid_users as apu
import settings
from timedposts.automated_updates import UpdateDataGuild


class ForceDataGuildUpdate(commands.GroupCog, name="force_update"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="paid_objects", description="Force an update of all paid objects"
    )
    async def UpdatePaidObjects(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        try:
          await interaction.followup.send(f"Original stores: {apu.STORES}")
          apu.UpdateStores()
          await interaction.followup.send(f"New stores: {apu.STORES}")
          
          await interaction.followup.send(f"Original Hubs: {apu.HUBS}")
          apu.UpdateHubs()
          await interaction.followup.send(f"New Hubs: {apu.HUBS}")
          
          await interaction.followup.send(f"Original Paid Users: {apu.PAID_USERS}")
          apu.UpdatePaidUsers()
          await interaction.followup.send(f"New Paid Users: {apu.PAID_USERS}")
          
          await interaction.followup.send(f"Original Paid Stores: {apu.PAID_STORES}")
          apu.UpdatePaidStores()
          await interaction.followup.send(f"New Paid Stores: {apu.PAID_STORES}")
          
          await interaction.followup.send(f"Original Paid Hubs: {apu.PAID_HUBS}")
          apu.UpdatePaidHubs()
          await interaction.followup.send(f"New Paid Hubs: {apu.PAID_HUBS}")
          
          await interaction.followup.send("All paid objects successfully updated!")
        except Exception as exception:
          await interaction.followup.send(
            f"Error updating paid objects: {exception}", ephemeral=True
          )

    @app_commands.command(
        name="data_guild", description="Force an update of the data guild"
    )
    @app_commands.guilds(settings.BOTGUILDID)
    async def ForceUpdate(self, interaction: Interaction):
        await interaction.response.defer(thinking=False)
        try:
            await UpdateDataGuild(self.bot)
            await interaction.followup.send("Data guild updated!")
        except Exception as exception:
            await interaction.followup.send(f"Error updating data guild: {exception}")


async def setup(bot: commands.Bot):
    await bot.add_cog(ForceDataGuildUpdate(bot), guild=Object(settings.BOTGUILDID))
