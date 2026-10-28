from tuple_conversions import MTBRoles, InteractionObjects
from discord import Interaction, app_commands, TextChannel
from discord.ext import commands


from checks import IsHub, IsStore, HasRequiredRoles
from custom_errors import KnownError
from data.hubs_data import GetRegions, GetHub
from input_modals.map_format_modal import MapFormatModal
from input_modals.map_game_modal import MapGameModal
from input_modals.map_region_modal import MapRegionModal
from services.command_error_service import Error
from services.map_claim_feed import MapClaimFeed


class MappingCommands(commands.GroupCog, name="map"):
    """A group of commands for mapping channels to games, formats, and claim feeds"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="archetype_feed",
        description="Map this channel as feed for submitted archetypes in this game",
    )
    @app_commands.guild_only()
    @HasRequiredRoles([MTBRoles.MTStore.name])
    @IsStore()
    async def AddClaimFeedMap(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True, thinking=False)
        objects = interaction.extras.get("db_object")
        output = await MapClaimFeed(interaction, objects)
        await interaction.followup.send(output, ephemeral=True)

    @app_commands.command(name="region", description="Map your channel to a region")
    @HasRequiredRoles([MTBRoles.MTStore.name])
    @app_commands.guild_only()
    @IsHub()
    async def AddRegionMap(self, interaction: Interaction):
        if not interaction.guild_id:
            raise KnownError("No guild found.")
        hub = await GetHub(interaction.guild_id)
        if not hub:
            raise KnownError("No hub found. Please register your hub.")
        if not hub.format_lock:
            raise KnownError("This hub does not have format locking enabled.")
        regions = await GetRegions()
        if not regions or len(regions) == 0:
            raise KnownError("No regions found. Please contact the bot owner.")
        modal = MapRegionModal(hub, regions)
        await interaction.response.send_modal(modal)
        await modal.wait()

    @app_commands.command(name="game", description="Map your category to a game")
    @HasRequiredRoles([MTBRoles.MTStore.name])
    @app_commands.guild_only()
    @IsStore()
    async def AddGameMap(self, interaction: Interaction):
        objects = interaction.extras.get("db_object")
        if not objects or not objects.store:
            raise KnownError("No store found. Please register your store.")
        channel = interaction.channel
        if not isinstance(channel, TextChannel):
            raise KnownError(
                "Cannot map a game to a category that does not have text channels"
            )
        category = channel.category
        if category is None:
            raise KnownError("Must map a game to a category")
        
        modal = await MapGameModal.create(objects.store, category_id)
        await interaction.response.send_modal(modal)
        await modal.wait()

    @app_commands.command(name="format", description="Map your channel to a format")
    @HasRequiredRoles([MTBRoles.MTStore.name])
    @app_commands.guild_only()
    @IsStore()
    async def AddFormatMap(self, interaction: Interaction):
        objects = interaction.extras.get("db_object")
        if not objects or not objects.game or not objects.store:
            raise KnownError(
                "No store or game found. Please map a game to this category first."
            )
        modal = await MapFormatModal.create(objects.store, objects.game)
        await interaction.response.send_modal(modal)
        await modal.wait()

    @AddClaimFeedMap.error
    @AddGameMap.error
    @AddFormatMap.error
    async def Errors(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot: commands.Bot):
    await bot.add_cog(MappingCommands(bot))
