from custom_errors import KnownError
from output_builder import BuildTableOutput
from tuple_conversions import MTBRoles, InteractionObjects
from checks import isMTStore, HasRequiredRoles, isMTSubmitter
from discord import Interaction, Member, Guild, app_commands
from data.commands_data import GetHereCommands, GetUserCommands
import timedposts.automated_paid_users as apu


def _GetSlashCommandDescriptions(
    tree: app_commands.CommandTree,
) -> dict[str, str]:
    descriptions: dict[str, str] = {}

    def add_command(command: app_commands.Command | app_commands.Group) -> None:
        if isinstance(command, app_commands.Group):
            for child in command.commands:
                add_command(child)
            return

        descriptions[f"/{command.qualified_name}"] = command.description

    for command in tree.get_commands():
        if isinstance(command, app_commands.ContextMenu):
            continue
        add_command(command)

    return descriptions


def _BuildCommandDescriptionMessages(
    commands: list[tuple[str, ...]], descriptions: dict[str, str]
) -> list[str]:
    heading = "Commands available to you"
    max_body_length = 2000 - len(heading) - 2
    messages: list[str] = []
    current = ""

    def flush() -> None:
        nonlocal current
        if current:
            messages.append(f"{heading}\n\n{current}")
            current = ""

    for (command_name,) in commands:
        description = descriptions.get(command_name, "Description unavailable.")
        entry = f"{command_name}\n{description}\n\n"

        while entry:
            available = max_body_length - len(current)
            if available == 0:
                flush()
                available = max_body_length

            if len(entry) <= available:
                current += entry
                entry = ""
            else:
                if current:
                    flush()
                    continue

                current = entry[:max_body_length]
                entry = entry[max_body_length:]
                flush()

    flush()
    return messages


async def GetCommandsHere(objects: InteractionObjects, guild:Guild, user:Member) -> str:
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
    objects: InteractionObjects,
    discord: Guild,
    user: Member,
    command_tree: app_commands.CommandTree,
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
    descriptions = _GetSlashCommandDescriptions(command_tree)
    return _BuildCommandDescriptionMessages(commands, descriptions)
