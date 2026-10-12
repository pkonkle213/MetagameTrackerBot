from discord.ext.commands import Bot
from custom_errors import KnownError
from discord_messages import MessageChannel
from discord import app_commands, Interaction
from settings import BOTGUILDID, ERRORCHANNELID
from traceback import format_exception


async def Error(
    bot: Bot, interaction: Interaction, error: app_commands.AppCommandError | Exception
):
    if isinstance(error, app_commands.errors.MissingRole):
        feedback = "You do not have the required role to use this command."
    elif isinstance(error, app_commands.errors.CommandOnCooldown):
        feedback = str(error)
    elif isinstance(error, app_commands.errors.CheckFailure):
        feedback = str(error)
    elif isinstance(error, KnownError):
        feedback = error.message
    else:
        original_error = getattr(error, "original", error)
        error_traceback = "".join(
            format_exception(
                type(original_error), original_error, original_error.__traceback__
            )
        )
        feedback = "Something unexpected went wrong. It's been reported. Please try again in a few hours."
        await MessageChannel(
            bot,
            f"```{error_traceback[:1994]}```",
            BOTGUILDID,
            ERRORCHANNELID,
        )
    try:
        await interaction.response.send_message(feedback, ephemeral=True)
    except Exception:
        await interaction.followup.send(feedback, ephemeral=True)
