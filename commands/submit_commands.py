from services.submit_archetype_service import OneEventDetails
from discord import Interaction, User, app_commands
from discord.ext import commands
from services.event_services import EventForData
from checks import IsStore, isMTSubmitter, HasRequiredRoles
from custom_errors import KnownError
from data.event_data import CreateEvent, GetEvents
from data.player_name_data import GetArchetypeModalDetails, GetUserName
from services.command_error_service import Error
from services.determine_archetype_input import GetArchetypeModal
from tuple_conversions import MTBRoles
from services.submit_data_workflow import SubmitEventDataWorkflow
from services.mass_archetype_workflow import SubmitMassArchetypes


class SubmitDataChecker(commands.GroupCog, name="submit"):
    """A group of commands to submit event data and archetypes"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="check", description="To test if you can submit data")
    @app_commands.guild_only()
    @IsStore()
    @app_commands.checks.cooldown(1, 300.0, key=lambda i: (i.guild_id, i.user.id))
    async def SubmitCheck(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True, thinking=False)
        issues = ["Issues I detect:"]
        objects = interaction.extras.get("db_object")
        if not interaction.guild:
            raise KnownError("How?")
        if isinstance(interaction.user, User):
            raise KnownError("Bad user. Need Member")

        if not objects:
            issues.append(
                "- The bot wasn't installed correctly, please reinstall the bot"
            )
        else:
            if not objects.store:
                issues.append("- Store not registered")
            if not isMTSubmitter(interaction.guild, interaction.user):
                issues.append("- You don't have the MTSubmitter role.")
            if not objects.game:
                issues.append("- Category not mapped to a game")
            if objects.game and not objects.format:
                issues.append("- Channel not mapped to a format")

        if len(issues) == 1:
            await interaction.followup.send(
                "Everything looks good. Please reach out to Phil to test your data"
            )
        else:
            await interaction.followup.send("\n".join(issues))

    @app_commands.command(
        name="mass_archetype", description="Submit multiple archetypes for an event"
    )
    @app_commands.guild_only()
    @HasRequiredRoles([MTBRoles.MTSubmitter.name])
    @IsStore()
    async def MassArchetypeInput(self, interaction: Interaction):
        objects = interaction.extras.get("db_object")

        if not objects or not objects.store or not objects.game or not objects.format:
            raise KnownError("No store, game, or format found.")

        await SubmitMassArchetypes(
            interaction, objects.store, objects.game, objects.format
        )

    @app_commands.command(
        name="archetype", description="Submit a player's archetype for an event"
    )
    @app_commands.guild_only()
    async def SubmitArchetypeCommand(self, interaction: Interaction):
        objects = interaction.extras.get("db_object")
        if (
            not objects
            or (not objects.store and not objects.hub)
            or not objects.game
            or not objects.format
        ):
            raise KnownError("A format must be mapped to this channel")

        user_id = interaction.user.id
        is_submitter = isMTSubmitter(interaction.guild, interaction.user)

        player = await GetArchetypeModalDetails(user_id, objects.game, objects.format)

        events = await GetEvents(
            objects.store,
            objects.hub,
            objects.game,
            objects.format,
            objects.region,
            is_submitter,
        )

        if len(events) == 0:
            raise KnownError("No events found.")

        await GetArchetypeModal(
            self.bot,
            user_id,
            events,
            interaction,
            objects.store,
            objects.hub,
            objects.game,
            objects.format,
            player.player_name,
            player.archetypes,
            is_submitter,
        )

    @app_commands.command(name="data", description="Submitting an event's data")
    @HasRequiredRoles([MTBRoles.MTSubmitter.name])
    @app_commands.guild_only()
    @IsStore()
    async def SubmitDataCommand(self, interaction: Interaction) -> None:
        objects = interaction.extras.get("db_object")

        if not objects or not objects.store or not objects.game or not objects.format:
            raise KnownError("No store, game, or format found.")

        if objects.hub:
            raise KnownError("You can't submit data from a hub.")

        event, input_type, active_interaction, is_new_event = await EventForData(
            self.bot, interaction, objects.store, objects.game, objects.format
        )

        if not event or not input_type or not active_interaction:
            await interaction.followup.send("Event canceled!", ephemeral=True)
            return

        if is_new_event:
            event_id = await CreateEvent(event, interaction.user.id)
            event = event._replace(id=event_id)

        await SubmitEventDataWorkflow(
            bot=self.bot,
            interaction=interaction,
            store=objects.store,
            game=objects.game,
            format=objects.format,
            event=event,
            input_type=input_type,
            active_interaction=active_interaction,
            submitter_id=interaction.user.id,
            is_new_event=is_new_event,
        )

    @SubmitCheck.error
    @SubmitDataCommand.error
    @SubmitArchetypeCommand.error
    async def Errors(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot: commands.Bot):
    await bot.add_cog(SubmitDataChecker(bot))
