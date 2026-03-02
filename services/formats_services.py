from replit import db
import discord
from discord import Interaction
from custom_errors import KnownError
from interaction_objects import GetObjectsFromInteraction, SplitInteractionData
from data.formats_data import AddFormatMap, GetFormatsByGameId
from tuple_conversions import Format


async def AddStoreFormatMap(interaction: Interaction,
                            chosen_format: Format) -> str:
  discord_id, category_id, channel_id, user_id = SplitInteractionData(interaction)

  rows = AddFormatMap(discord_id, chosen_format.FormatId, channel_id)
  if rows is None:
    return 'Unable to add game map to database'
  try:
    await SetChannelMessagePermissions(interaction)
    return f'Success! This channel ({channel_id}) is now mapped to {chosen_format.FormatName.title()}'
  except Exception:
    return f'Successfully mapped the channel ({channel_id}) to {chosen_format.FormatName.title()}, but failed to give the bot permissions to send messages in this channel. Please give the bot permissions manually.'

async def SetChannelMessagePermissions(interaction: Interaction):
  guild = interaction.guild
  if guild is None:
    raise KnownError('No guild found')
  channel = interaction.channel
  if channel is None:
    raise KnownError('No channel found')
  user_bot = guild.me
  if not user_bot:
    raise KnownError("Bot not found in guild")

  overwrite = discord.PermissionOverwrite()
  overwrite.send_messages = True
  if isinstance(channel, discord.TextChannel):
    await channel.set_permissions(user_bot, overwrite=overwrite)
  else:
    raise KnownError('Incorrect type of channel')


def GetFormatOptions(interaction: Interaction):
  store, game, format = GetObjectsFromInteraction(interaction)
  return GetFormatsByGameId(game)
