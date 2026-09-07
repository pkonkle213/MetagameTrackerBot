from collections.abc import Sequence

import discord
from discord.ext import commands

import settings
from custom_errors import KnownError


async def MessageUser(
    bot: commands.Bot,
    msg: str,
    userId: int,
    files: Sequence[discord.File] | None = None,
):
    user = await bot.fetch_user(userId)
    if files is None:
        await user.send(f"{msg}")
    else:
        await user.send(f"{msg}", files=files)


async def MessageChannel(
    bot: commands.Bot,
    msg: str,
    guildId: int,
    channelId: int,
    file: discord.File | None = None,
):
    try:
        server = bot.get_guild(int(guildId))
        if server is None:
            print(f"Server {guildId} not found")
            raise KnownError(f"Server {guildId} not found")
        if msg != "":
            channel = server.get_channel(int(channelId))
            if channel is None:
                print(f"Channel {channelId} not found")
                raise KnownError(f"Channel {channelId} not found")
            if not isinstance(channel, discord.TextChannel):
                raise KnownError(f"Channel {channelId} is not a text channel")

            try:
                if file is None:
                    await channel.send(f"{msg}")
                else:
                    await channel.send(f"{msg}", file=file)
            except KnownError as ex:
                print(f"Error sending message to channel {channelId}: {ex}")
    except KnownError as ex:
        await MessageUser(
            bot, f"A user ran into an error:\n{msg}\nError: {ex}", settings.PHILID
        )
