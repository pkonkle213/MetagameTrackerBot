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


async def assign_mt_roles(
    guild: discord.Guild, target_user_id: int, requester_id: int
) -> discord.Member:
    role_names = [MTBRoles.MTSubmitter.name, MTBRoles.MTStore.name]
    roles = [discord.utils.get(guild.roles, name=name) for name in role_names]
    missing_roles = [
        name for name, role in zip(role_names, roles) if role is None
    ]
    if missing_roles:
        raise ValueError(
            f"Required roles not found in the bot guild: {', '.join(missing_roles)}"
        )

    try:
        member = await guild.fetch_member(target_user_id)
    except discord.NotFound as error:
        raise LookupError(
            f"Discord user {target_user_id} is not a member of the bot guild."
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
    @app_commands.describe(discord_id="Discord ID of the member to assign roles to")
    async def AssignRoles(self, interaction: Interaction, discord_id: int):
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            member = await assign_mt_roles(
                interaction.guild, discord_id, interaction.user.id
            )
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
