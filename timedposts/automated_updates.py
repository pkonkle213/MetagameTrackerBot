from discord import CategoryChannel, ForumChannel
from discord.abc import PrivateChannel
from discord.ext import commands
from custom_errors import KnownError
from output_builder import BuildTableOutput
from data.automated_updates_data import GetDataChannels
from services.date_functions import BuildDateRange
from services.metagame_services import GetWholeMetagame
from data.hubs_data import GetHub


async def UpdateDataGuild(bot: commands.Bot):
    target_channels = await GetDataChannels()
    for data_channel in target_channels:
        channel = bot.get_channel(data_channel.channel_id)
        if (
            not channel
            or isinstance(channel, ForumChannel)
            or isinstance(channel, CategoryChannel)
            or isinstance(channel, PrivateChannel)
        ):
            raise KnownError("Cannot send a message to this channel")
        date_start, date_end = BuildDateRange("", "")
        data = await GetWholeMetagame(
            data_channel.game_id,
            data_channel.format_id,
            date_start,
            date_end
        )
        if len(data) > 0:
            title = f"Metagame from {date_start} to {date_end}"
            headers = ["Deck Archetype", "Meta %", "Win %"]
            output = BuildTableOutput(title, headers, data)
            await channel.send(output)
