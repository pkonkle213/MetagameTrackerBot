from output_builder import BuildTableOutput
from tuple_conversions import InteractionObjects
from checks import isMTStore, isMTSubmitter
from discord import Interaction, Member, Guild
from data.commands_data import GetHereCommands, GetUserCommands
import timedposts.automated_paid_users as apu


def _BuildCommandDescriptionMessages(
    commands: list[tuple], descriptions: dict[str, str]
) -> list[str]:
    """Format command descriptions into Discord-sized messages without dropping text."""
    title = "Commands for you in this channel"
    max_body_length = 2000 - len(title) - 2
    body = "\n\n".join(
        f"{command[0]}\n{descriptions.get(command[0], '')}" for command in commands
    )
    return [
        f"{title}\n\n{body[index:index + max_body_length]}"
        for index in range(0, len(body), max_body_length)
    ] or [title]


async def GetCommandsHere(
    objects: InteractionObjects, guild: Guild, user: Member
) -> list[str]:
    is_store = bool(objects.store)
    is_hub = bool(objects.hub)
    is_game = bool(objects.game)
    is_format = bool(objects.format)
    is_region = bool(objects.region)
    user_is_submitter = isMTSubmitter(guild, user)
    user_is_store = isMTStore(guild, user)
    user_is_paid = apu.IsPaidUser(user.id)
    store_is_paid = apu.IsPaidStore(guild.id)
    hub_is_paid = apu.IsPaidHub(guild.id)
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


async def GetCommandsUser(
    objects: InteractionObjects, discord: Guild, user: Member
) -> list[str]:
    is_store = bool(objects.store)
    is_hub = bool(objects.hub)
    is_game = bool(objects.game)
    is_format = bool(objects.format)
    is_region = bool(objects.region)
    user_is_submitter = isMTSubmitter(discord, user)
    user_is_store = isMTStore(discord, user)
    user_is_paid = apu.IsPaidUser(user.id)
    store_is_paid = apu.IsPaidStore(discord.id)
    hub_is_paid = apu.IsPaidHub(discord.id)
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
    descriptions = {command[0]: command[1] for command in commands}
    return _BuildCommandDescriptionMessages(commands, descriptions)
