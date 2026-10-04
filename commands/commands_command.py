from discord import Interaction, app_commands
from discord.ext import commands

from services.command_error_service import Error


def _command_lines(
    command_list: list[app_commands.Command | app_commands.Group],
    parent_path: str = "",
) -> list[str]:
    lines = []
    for command in sorted(command_list, key=lambda item: item.name):
        path = f"{parent_path} {command.name}".strip()
        if isinstance(command, app_commands.Group):
            lines.extend(_command_lines(command.commands, path))
        else:
            description = command.description or "No description"
            lines.append(f"`/{path}` — {description}")
    return lines


class BotCommands(commands.GroupCog, name="commands"):
    """Commands for discovering the bot's slash commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="all", description="List all commands available in the bot")
    async def ListAll(self, interaction: Interaction) -> None:
        command_lines = _command_lines(self.bot.tree.get_commands())
        if not command_lines:
            await interaction.response.send_message(
                "No commands are currently registered.", ephemeral=True
            )
            return

        header = "**Bot commands**\n"
        chunks: list[str] = []
        current_chunk = header
        for line in command_lines:
            if len(current_chunk) + len(line) + 1 > 1900:
                chunks.append(current_chunk)
                current_chunk = ""
            current_chunk += f"{line}\n"
        if current_chunk:
            chunks.append(current_chunk)

        await interaction.response.send_message(chunks[0], ephemeral=True)
        for chunk in chunks[1:]:
            await interaction.followup.send(chunk, ephemeral=True)

    @app_commands.command(
        name="here", description="List commands available in this server"
    )
    async def ListHere(self, interaction: Interaction) -> None:
        raise NotImplementedError("Listing commands available in this server is not implemented yet.")

    @ListAll.error
    @ListHere.error
    async def Errors(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ):
        await Error(self.bot, interaction, error)


async def setup(bot: commands.Bot):
    await bot.add_cog(BotCommands(bot))