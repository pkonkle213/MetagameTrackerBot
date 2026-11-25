import discord
from discord import Interaction, app_commands
from discord.ext import commands

import settings
from services.command_error_service import Error
from tuple_conversions import MTBRoles


async def _is_bot_owner_in_bot_guild(interaction: Interaction) -> bool:
    if (
        interaction.user.id != settings.PHILID
        or interaction.guild_id != settings.BOTGUILDID
    ):
        raise app_commands.CheckFailure(
            "This command is restricted to the bot owner in the bot guild."
        )
    return True


def parse_discord_id(value: str) -> int:
    normalized = value.strip()
    if not normalized or any(
        character < "0" or character > "9" for character in normalized
    ):
        raise ValueError("Enter a Discord ID using digits only.")

    target_user_id = int(normalized)
    if target_user_id <= 0:
        raise ValueError("Enter a valid positive Discord ID.")
    return target_user_id


async def get_assignment_guild(
    bot: commands.Bot, guild_id: int
) -> discord.Guild:
    guild = bot.get_guild(guild_id)
    if guild is not None:
        return guild

    try:
        return await bot.fetch_guild(guild_id)
    except (discord.NotFound, discord.Forbidden) as error:
        raise LookupError(
            f"The bot cannot access Discord guild {guild_id}."
        ) from error


async def assign_mt_roles(
    guild: discord.Guild, requester_id: int
) -> discord.Member:
    role_names = [MTBRoles.MTSubmitter.name, MTBRoles.MTStore.name]
    available_roles = await guild.fetch_roles()
    roles = [
        next(
            (
                role
                for role in available_roles
                if role.name.strip().casefold() == name.casefold()
            ),
            None,
        )
        for name in role_names
    ]
    missing_roles = [
        name for name, role in zip(role_names, roles) if role is None
    ]
    if missing_roles:
        raise ValueError(
            f"Required roles not found in the target guild: {', '.join(missing_roles)}"
        )

    try:
        member = await guild.fetch_member(settings.PHILID)
    except discord.NotFound as error:
        raise LookupError(
            f"You are not a member of Discord guild {guild.id}."
        ) from error

    await member.add_roles(
        *roles,
        reason=f"Role assignment requested by Discord user {requester_id}",
    )
    return member


class AssignRolesCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="assign_roles",
        description="Assign MTSubmitter and MTStore roles to a guild member",
    )
    @app_commands.guilds(settings.BOTGUILDID)
    @app_commands.guild_only()
    @app_commands.check(_is_bot_owner_in_bot_guild)
    @app_commands.describe(guild_id="Discord guild ID, entered as text")
    async def AssignRoles(self, interaction: Interaction, guild_id: str):
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            target_guild_id = parse_discord_id(guild_id)
            guild = await get_assignment_guild(self.bot, target_guild_id)
            member = await assign_mt_roles(guild, interaction.user.id)
        except (LookupError, ValueError) as error:
            await interaction.followup.send(str(error), ephemeral=True)
            return

        await interaction.followup.send(
            f"Assigned **MTSubmitter** and **MTStore** to {member.mention}.",
            ephemeral=True,
        )

    @AssignRoles.error
    async def Errors(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot: commands.Bot):
    await bot.add_cog(AssignRolesCommand(bot))
