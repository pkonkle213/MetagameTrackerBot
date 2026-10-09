import discord
from discord import Interaction, Object, app_commands
from discord.ext import commands

from checks import isPhil
from data.store_data import GetStoresWithOwners
from settings import BOTGUILDID
from tuple_conversions import MTBRoles, Store


class NewRoleCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="sync_store_roles",
        description="Ensure MTStore and MTSubmitter roles are assigned to every store owner.",
    )
    @app_commands.guilds(BOTGUILDID)
    @app_commands.guild_only()
    @app_commands.check(isPhil)
    async def SyncStoreRoles(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)

        try:
            stores = await GetStoresWithOwners()
        except Exception as error:
            await interaction.followup.send(
                f"Unable to load stores from the database ({type(error).__name__}).",
                ephemeral=True,
            )
            return

        if not stores:
            await interaction.followup.send("No stores were found.", ephemeral=True)
            return

        processed = 0
        skipped = 0
        roles_created = 0
        roles_assigned = 0
        roles_already_assigned = 0
        issues: list[str] = []
        required_roles = (MTBRoles.MTSubmitter.name, MTBRoles.MTStore.name)

        for store in stores:
            store_label = store.store_name or store.discord_name or str(store.discord_id)
            guild = self.bot.get_guild(store.discord_id)
            if guild is None:
                skipped += 1
                issues.append(f"{store_label}: bot is not in this server.")
                continue

            if not store.owner_id:
                skipped += 1
                issues.append(f"{store_label}: no owner ID is set in stores_view.")
                continue

            owner = guild.get_member(store.owner_id)
            if owner is None:
                try:
                    owner = await guild.fetch_member(store.owner_id)
                except discord.NotFound:
                    skipped += 1
                    issues.append(f"{store_label}: owner is not a member of the server.")
                    continue
                except discord.HTTPException as error:
                    skipped += 1
                    issues.append(
                        f"{store_label}: could not fetch owner ({type(error).__name__})."
                    )
                    continue

            processed += 1
            for role_name in required_roles:
                try:
                    role = discord.utils.get(guild.roles, name=role_name)
                    if role is None:
                        role = await guild.create_role(
                            name=role_name,
                            reason="Ensure required roles for the store owner",
                        )
                        roles_created += 1

                    if role in owner.roles:
                        roles_already_assigned += 1
                    else:
                        await owner.add_roles(
                            role,
                            reason="Ensure required roles for the store owner",
                        )
                        roles_assigned += 1
                except discord.HTTPException as error:
                    issues.append(
                        f"{store_label}: {role_name} failed ({type(error).__name__})."
                    )

        summary = (
            f"Checked {len(stores)} stores.\n"
            f"Stores processed: {processed}; skipped: {skipped}.\n"
            f"Roles created: {roles_created}; assigned: {roles_assigned}; "
            f"already assigned: {roles_already_assigned}."
        )
        if issues:
            summary += "\n\nIssues:"
            for issue in issues[:8]:
                summary += f"\n• {issue}"
            if len(issues) > 8:
                summary += f"\n…and {len(issues) - 8} more."

        await interaction.followup.send(summary[:2000], ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(
        NewRoleCommands(bot), guilds=[Object(id=BOTGUILDID)]
    )
