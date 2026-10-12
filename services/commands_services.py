from output_builder import BuildTableOutput
from tuple_conversions import MTBRoles
from checks import isMTStore, HasRequiredRoles, isMTSubmitter
from discord import Interaction
from data.interaction_data import GetObjectsFromInteraction
from data.commands_data import GetHereCommands, GetUserCommands
import timedposts.automated_paid_users as apu


async def GetCommandsHere(interaction: Interaction) -> str:
    objects = await GetObjectsFromInteraction(interaction)
    is_store = bool(objects.store)
    is_hub = bool(objects.hub)
    is_game = bool(objects.game)
    is_format = bool(objects.format)
    is_region = bool(objects.region)
    user_is_submitter = isMTSubmitter(interaction.guild, interaction.user)
    user_is_store = isMTStore(interaction.guild, interaction.user)
    user_is_paid = apu.IsPaidUser(interaction.user.id)
    store_is_paid = apu.IsPaidStore(interaction.guild_id)
    hub_is_paid = apu.IsPaidHub(interaction.guild_id)
    commands = await GetHereCommands(
        is_store,
        is_hub,
        is_game,
        is_format,
        is_region,
        user_is_submitter,
        user_is_store,
        user_is_paid,
        store_is_paid,
        hub_is_paid,
    )
    output = BuildTableOutput(
        "Commands in this channel", ["Name", "Requirement"], commands
    )
    return output


async def GetCommandsUser(interaction: Interaction) -> str:
    objects = await GetObjectsFromInteraction(interaction)
    is_store = bool(objects.store)
    is_hub = bool(objects.hub)
    is_game = bool(objects.game)
    is_format = bool(objects.format)
    is_region = bool(objects.region)
    user_is_submitter = isMTSubmitter(interaction.guild, interaction.user)
    user_is_store = isMTStore(interaction.guild, interaction.user)
    user_is_paid = apu.IsPaidUser(interaction.user.id)
    store_is_paid = apu.IsPaidStore(interaction.guild_id)
    hub_is_paid = apu.IsPaidHub(interaction.guild_id)
    commands = await GetUserCommands(
        is_store,
        is_hub,
        is_game,
        is_format,
        is_region,
        user_is_submitter,
        user_is_store,
        user_is_paid,
        store_is_paid,
        hub_is_paid,
    )
    output = BuildTableOutput("Commands in this channel", ["Name"], commands)
    return output
